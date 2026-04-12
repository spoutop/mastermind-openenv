#!/usr/bin/env python3

import argparse
import sys

try:
    from mastermind_env.server.triage_environment import TriageEnvironment
    from mastermind_env.models import TriageAction
except ImportError:
    from server.triage_environment import TriageEnvironment
    from models import TriageAction


OPTIMAL_PATHS = {
    "easy": [
        ("query_logs", ""),
        ("block_ip", None),  # None = fill from scenario
        ("resolve", ""),
    ],
    "medium": [
        ("query_logs", ""),
        ("analyze", ""),
        ("block_ip", None),
        ("resolve", ""),
    ],
    "hard": [
        ("query_logs", ""),
        ("analyze", ""),
        ("classify", None),
        ("block_ip", None),
        ("resolve", ""),
    ],
}


def run_episode(task, seed):
    env = TriageEnvironment()
    env.reset(seed=seed, task=task)

    inc = env._scenario["incident"]
    targets = env._scenario.get("correct_targets", {})

    path = OPTIMAL_PATHS[task]
    rewards = []

    for act, tgt in path:
        if tgt is None:
            if act == "block_ip":
                tgt = targets.get("block_ip", inc["source_ip"])
            elif act == "classify":
                tgt = targets.get("classify", inc["severity"])
            else:
                tgt = ""
        obs = env.step(TriageAction(action=act, target=tgt))
        rewards.append(float(obs.reward))
        if obs.done:
            break

    success = obs.incident_resolved
    score = sum(rewards) / len(rewards) if rewards else 0.0
    return success, score, rewards


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=3)
    args = parser.parse_args()

    for task in ["easy", "medium", "hard"]:
        scores = []
        for seed in range(args.seeds):
            ok, score, rewards = run_episode(task, seed)
            scores.append(score)
            rstr = ",".join(f"{r:.2f}" for r in rewards)
            print(f"{task} seed={seed} success={ok} score={score:.3f} rewards={rstr}",
                  file=sys.stderr)
        avg = sum(scores) / len(scores)
        print(f"{task}: avg_score={avg:.3f}", file=sys.stderr)

    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
