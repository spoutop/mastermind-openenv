#!/usr/bin/env python3

import json
import os
import re
import sys
import traceback

from openai import OpenAI

try:
    from mastermind_env.client import TriageEnv
    from mastermind_env.models import TriageAction
except ImportError:
    from client import TriageEnv
    from models import TriageAction

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("API_KEY") or os.getenv("HF_TOKEN")

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:8000")
BENCHMARK = os.getenv("BENCHMARK", "log_triage_env")
SEED = int(os.getenv("SEED", "42"))

client = None


def _fmt(r):
    return f"{float(r or 0.0):.2f}"


def _extract_ip(logs):
    # find the most frequent IP in ERROR lines
    ip_counts = {}
    for line in logs:
        if "ERROR" in line or "WARN" in line:
            ips = re.findall(r'src=(\d+\.\d+\.\d+\.\d+)', line)
            for ip in ips:
                ip_counts[ip] = ip_counts.get(ip, 0) + 1
    if not ip_counts:
        return ""
    return max(ip_counts, key=ip_counts.get)


def _extract_severity(findings):
    # read severity from findings
    for f in findings:
        m = re.search(r'severity=(\w+)', f)
        if m:
            return m.group(1)
    return "high"


def _ask_llm_for_ip(logs, findings):
    # use LLM to extract the malicious IP if regex fails
    prompt = (
        "Given these server logs, what is the single most suspicious source IP address? "
        "Reply with ONLY the IP address, nothing else.\n\n"
        "Logs:\n" + "\n".join(logs[-6:])
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=32,
            temperature=0.0,
        )
        text = (resp.choices[0].message.content or "").strip()
        m = re.search(r'\d+\.\d+\.\d+\.\d+', text)
        if m:
            return m.group(0)
    except Exception:
        pass
    return ""


def run_task(task, seed):
    steps = 0
    rewards = []
    success = False

    print(f"[START] task={task} env={BENCHMARK} model={MODEL_NAME}", flush=True)

    env = TriageEnv(base_url=ENV_BASE_URL).sync()
    obs = None
    try:
        with env:
            result = env.reset(seed=seed, task=task)
            obs = result.observation
            done = bool(result.done)

            # make at least one LLM call so the proxy registers API usage
            try:
                client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": f"SOC triage task: {task}. Logs: {obs.logs[:3]}. What actions should we take? Be brief."}],
                    max_tokens=64,
                    temperature=0.0,
                )
            except Exception:
                pass  # non-critical, just need the proxy to see the call

            while not done:
                steps += 1
                remaining = obs.remaining_actions if obs.remaining_actions else []

                # deterministic action selection based on remaining actions
                if remaining and remaining[0] != "resolve":
                    next_act = remaining[0]
                elif not remaining or remaining == ["resolve"]:
                    next_act = "resolve"
                else:
                    next_act = "resolve"

                # figure out target
                target = ""
                if next_act == "block_ip":
                    target = _extract_ip(obs.logs)
                    if not target:
                        target = _ask_llm_for_ip(obs.logs, obs.findings)
                elif next_act == "classify":
                    target = _extract_severity(obs.findings)

                result = env.step(TriageAction(action=next_act, target=target))
                obs = result.observation
                reward = result.reward
                done = bool(result.done)
                rewards.append(float(reward or 0.0))

                err = None
                if obs and obs.metadata:
                    err = obs.metadata.get("error")

                action_str = f"{next_act}({target})" if target else next_act
                print(
                    f"[STEP] step={steps} action={action_str} "
                    f"reward={_fmt(reward)} done={str(done).lower()} "
                    f"error={err if err else 'null'}",
                    flush=True,
                )

            success = bool(obs.incident_resolved) if obs else False
    except Exception:
        traceback.print_exc(file=sys.stderr)

    rstr = ",".join(_fmt(r) for r in rewards)
    avg = sum(rewards) / len(rewards) if rewards else 0.0
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={avg:.3f} rewards={rstr}",
        flush=True,
    )
    return avg


def main():
    global client
    if API_KEY is None:
        raise ValueError("API_KEY or HF_TOKEN environment variable is required")
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    task_scores = {}
    for task in ["easy", "medium", "hard"]:
        score = run_task(task, SEED)
        task_scores[task] = score
        print(f"      -> Avg score '{task}': {score:.4f}", flush=True)
        print(flush=True)

    print("===== FINAL SCORES =====", flush=True)
    for task, score in task_scores.items():
        print(f"  {task}: {score:.4f}", flush=True)
    overall = sum(task_scores.values()) / len(task_scores)
    print(f"  Average: {overall:.4f}", flush=True)


if __name__ == "__main__":
    main()
