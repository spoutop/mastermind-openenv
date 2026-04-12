from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import EnvironmentMetadata, State

try:
    from mastermind_env.models import TriageAction, TriageObservation
    from mastermind_env.server.scenarios import TASK_TEMPLATES, TASK_CONFIG
except ImportError:
    from models import TriageAction, TriageObservation
    from server.scenarios import TASK_TEMPLATES, TASK_CONFIG

VALID_ACTIONS = {"query_logs", "analyze", "classify", "block_ip",
                 "restart_service", "escalate", "resolve"}

REWARD_BASE = {
    "query_logs": 0.90, "analyze": 0.92, "classify": 0.94,
    "block_ip": 0.96, "restart_service": 0.96, "escalate": 0.92,
}


class TriageEnvironment(Environment[TriageAction, TriageObservation, State]):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self) -> None:
        super().__init__()
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task = "medium"
        self._scenario: dict = {}
        self._visible_logs: List[str] = []
        self._findings: List[str] = []
        self._actions_taken: List[str] = []
        self._completed_required: Set[str] = set()
        self._steps_used = 0
        self._max_steps = 8
        self._done = False
        self._resolved = False
        self._all_logs: List[str] = []
        self._revealed_indices: Set[int] = set()

    def get_metadata(self) -> EnvironmentMetadata:
        return EnvironmentMetadata(
            name="log_triage_env",
            description=(
                "Log analysis and incident triage environment. "
                "3 tasks (easy/medium/hard) with seeded scenarios. "
                "Agent queries logs, analyzes findings, classifies severity, "
                "and takes remediation actions."
            ),
            version="0.2.0",
        )

    def _pick_scenario(self, task: str, seed: int) -> dict:
        templates = TASK_TEMPLATES.get(task, TASK_TEMPLATES["medium"])
        idx = seed % len(templates)
        return templates[idx]

    def _initial_slice(self) -> List[str]:
        # always show first 4 log entries as overview
        indices = list(range(min(4, len(self._all_logs))))
        for i in indices:
            self._revealed_indices.add(i)
        return [self._all_logs[i] for i in indices]

    def _is_relevant_target(self, target: str) -> bool:
        if not target:
            return True
        inc = self._scenario.get("incident", {})
        valid_targets = {
            inc.get("service", ""),
            inc.get("source_ip", ""),
            inc.get("type", ""),
        }
        return target in valid_targets

    def _reveal_logs(self, target: str) -> List[str]:
        # reveal up to 3 new matching entries
        new_entries = []
        count = 0
        for i, log in enumerate(self._all_logs):
            if i in self._revealed_indices:
                continue
            if not target or target in log:
                self._revealed_indices.add(i)
                new_entries.append(log)
                count += 1
                if count >= 3:
                    break
        return new_entries

    def _has_new_evidence(self) -> bool:
        inc = self._scenario.get("incident", {})
        tokens = {inc.get("source_ip", ""), inc.get("service", ""),
                  inc.get("type", "")}
        tokens.discard("")
        visible_text = " ".join(self._visible_logs)
        findings_text = " ".join(self._findings)
        for t in tokens:
            if t in visible_text and t not in findings_text:
                return True
        return False

    def _all_required_done(self) -> bool:
        required = set(self._scenario.get("required_actions", []))
        return required.issubset(self._completed_required)

    def _progress(self) -> float:
        required = self._scenario.get("required_actions", [])
        if not required:
            return 1.0
        return len(self._completed_required) / len(required)

    def _action_label(self, action: str, target: str) -> str:
        if target:
            return f"{action}({target})"
        return action

    def _observe(self, reward: float, done: bool, error: Optional[str]) -> TriageObservation:
        meta: Dict[str, Any] = {}
        if error:
            meta["error"] = error
        required = list(self._scenario.get("required_actions", []))
        remaining = [a for a in required if a not in self._completed_required]
        if not done:
            remaining.append("resolve")
        return TriageObservation(
            task=self._task,
            scenario_id=self._scenario.get("incident", {}).get("type", ""),
            logs=list(self._visible_logs),
            findings=list(self._findings),
            actions_taken=list(self._actions_taken),
            steps_used=self._steps_used,
            max_steps=self._max_steps,
            incident_resolved=self._resolved,
            done=done,
            reward=reward,
            metadata=meta,
            required_actions=required + ["resolve"],
            completed_actions=list(self._completed_required),
            remaining_actions=remaining,
        )

    def reset(self, seed=None, episode_id=None, **kwargs) -> TriageObservation:
        task = str(kwargs.get("task") or "medium")
        if task not in TASK_TEMPLATES:
            task = "medium"
        self._task = task
        self._state = State(episode_id=episode_id or str(uuid4()), step_count=0)

        actual_seed = seed if seed is not None else 0
        self._scenario = self._pick_scenario(task, actual_seed)
        cfg = TASK_CONFIG.get(task, TASK_CONFIG["medium"])
        self._max_steps = cfg["max_steps"]
        self._all_logs = list(self._scenario["all_logs"])
        self._revealed_indices = set()
        self._visible_logs = self._initial_slice()
        self._findings = []
        self._actions_taken = []
        self._completed_required = set()
        self._steps_used = 0
        self._done = False
        self._resolved = False
        return self._observe(reward=0.50, done=False, error=None)

    def step(self, action: TriageAction, timeout_s=None, **kwargs) -> TriageObservation:
        self._state.step_count += 1
        self._steps_used += 1
        act = action.action.strip().lower()
        target = action.target.strip() if action.target else ""

        # invalid action
        if act not in VALID_ACTIONS:
            self._actions_taken.append(self._action_label(act, target))
            if self._steps_used >= self._max_steps:
                self._done = True
                return self._observe(reward=0.20, done=True, error=f"unknown action: {act}")
            return self._observe(reward=0.20, done=False, error=f"unknown action: {act}")

        self._actions_taken.append(self._action_label(act, target))
        required = set(self._scenario.get("required_actions", []))
        correct_targets = self._scenario.get("correct_targets", {})

        # resolve is always terminal
        if act == "resolve":
            self._done = True
            if self._all_required_done():
                # for hard, check if classify was done correctly
                if self._task == "hard" and "classify" in required:
                    if "classify" not in self._completed_required:
                        self._resolved = False
                        return self._observe(reward=0.50, done=True, error=None)
                self._resolved = True
                eff = self._steps_used / self._max_steps
                reward = round(0.96 + 0.03 * (1.0 - eff), 4)
                return self._observe(reward=reward, done=True, error=None)
            else:
                self._resolved = False
                return self._observe(reward=0.35, done=True, error=None)

        # check correctness per action type
        is_correct = False
        if act == "query_logs":
            if self._is_relevant_target(target):
                is_correct = True
                new_logs = self._reveal_logs(target)
                self._visible_logs.extend(new_logs)
            if act in required and act not in self._completed_required:
                if is_correct:
                    self._completed_required.add(act)

        elif act == "analyze":
            if self._has_new_evidence():
                is_correct = True
                findings = self._scenario.get("findings_on_analyze", [])
                for f in findings:
                    if f not in self._findings:
                        self._findings.append(f)
                        break
            if act in required and act not in self._completed_required:
                if is_correct:
                    # in medium/hard, analyze must come before block_ip
                    self._completed_required.add(act)

        elif act == "classify":
            expected_sev = correct_targets.get("classify", "")
            if target.lower() == expected_sev.lower():
                is_correct = True
            if act in required and act not in self._completed_required:
                if is_correct:
                    self._completed_required.add(act)

        elif act == "block_ip":
            expected_ip = correct_targets.get("block_ip", "")
            if target == expected_ip:
                is_correct = True
                # in medium/hard, block_ip before analyze gets low reward
                if self._task in ("medium", "hard") and "analyze" in required:
                    if "analyze" not in self._completed_required:
                        is_correct = False
            if act in required and act not in self._completed_required:
                if is_correct:
                    self._completed_required.add(act)

        elif act == "restart_service":
            expected_svc = correct_targets.get("restart_service", "")
            if target == expected_svc:
                is_correct = True
            if act in required and act not in self._completed_required:
                if is_correct:
                    self._completed_required.add(act)

        elif act == "escalate":
            is_correct = True
            if act in required and act not in self._completed_required:
                self._completed_required.add(act)

        # check for repeated action (anti-farming)
        if act in self._completed_required and is_correct:
            label = self._action_label(act, target)
            prior_count = sum(1 for a in self._actions_taken[:-1] if a == label)
            if prior_count > 0:
                is_correct = False

        # compute reward
        if is_correct:
            base = REWARD_BASE.get(act, 0.90)
            reward = round(base + 0.03 * self._progress(), 4)
        else:
            reward = 0.20

        # check timeout
        if self._steps_used >= self._max_steps:
            self._done = True
            return self._observe(reward=reward, done=True, error=None)

        return self._observe(reward=reward, done=False, error=None)

    @property
    def state(self) -> State:
        return self._state
