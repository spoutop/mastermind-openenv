from typing import Dict

from openenv.core.client_types import StepResult
from openenv.core.env_client import EnvClient
from openenv.core.env_server.types import State

try:
    from mastermind_env.models import TriageAction, TriageObservation
except ImportError:
    from models import TriageAction, TriageObservation


class TriageEnv(EnvClient[TriageAction, TriageObservation, State]):

    def _step_payload(self, action: TriageAction) -> Dict:
        return {"action": action.action, "target": action.target}

    def _parse_result(self, payload: Dict) -> StepResult[TriageObservation]:
        obs = payload.get("observation", {}) or {}
        observation = TriageObservation(
            task=obs.get("task", "medium"),
            scenario_id=obs.get("scenario_id", ""),
            logs=obs.get("logs", []) or [],
            findings=obs.get("findings", []) or [],
            actions_taken=obs.get("actions_taken", []) or [],
            steps_used=obs.get("steps_used", 0),
            max_steps=obs.get("max_steps", 8),
            incident_resolved=obs.get("incident_resolved", False),
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=(obs.get("metadata") or {}),
            required_actions=obs.get("required_actions", []) or [],
            completed_actions=obs.get("completed_actions", []) or [],
            remaining_actions=obs.get("remaining_actions", []) or [],
        )
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
