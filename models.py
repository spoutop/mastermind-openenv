from typing import List

from pydantic import Field

from openenv.core.env_server.types import Action, Observation


class TriageAction(Action):
    action: str
    target: str = ""


class TriageObservation(Observation):
    task: str = "medium"
    scenario_id: str = ""
    logs: List[str] = Field(default_factory=list)
    findings: List[str] = Field(default_factory=list)
    actions_taken: List[str] = Field(default_factory=list)
    steps_used: int = 0
    max_steps: int = 8
    incident_resolved: bool = False
    required_actions: List[str] = Field(default_factory=list)
    completed_actions: List[str] = Field(default_factory=list)
    remaining_actions: List[str] = Field(default_factory=list)
