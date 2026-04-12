from openenv.core.rubrics.base import Rubric
from openenv.core.rubrics.containers import WeightedSum


class OutcomeRubric(Rubric):
    def forward(self, action, obs):
        if not obs.done:
            return 0.5
        if obs.incident_resolved:
            return 0.95
        return 0.20


class CoverageRubric(Rubric):
    def forward(self, action, obs):
        if not obs.done:
            return 0.5
        total = obs.max_steps
        if total == 0:
            return 0.5
        eff = obs.steps_used / total
        return round(0.3 + 0.6 * (1.0 - eff), 4)


RUBRIC_NAMES = ["outcome", "coverage"]
RUBRIC_WEIGHTS = [0.60, 0.40]


class TriageRubric(WeightedSum):
    def __init__(self):
        rubrics = [OutcomeRubric(), CoverageRubric()]
        super().__init__(rubrics, RUBRIC_WEIGHTS)
        for name, r in zip(RUBRIC_NAMES, rubrics):
            setattr(self, name, r)
