"""Common small-input types and independent snapshots for greedy demonstrations."""

from copy import deepcopy
from typing import Annotated, Any
from pydantic import Field, StrictInt, StringConstraints
from backend.schemas import VisualizationStep

Label = Annotated[str, StringConstraints(strict=True, pattern=r"^[A-Za-z0-9_]{1,8}$")]
Positive = Annotated[StrictInt, Field(ge=1, le=1000000)]
Nonnegative = Annotated[StrictInt, Field(ge=0, le=1000000)]


class GreedyStep(VisualizationStep):
    action: str
    stateData: dict[str, Any]


class Recorder:
    def __init__(self, state):
        self.state = deepcopy(state)
        self.steps = []

    def record(self, action, explanation, highlights=()):
        self.steps.append(GreedyStep(stepIndex=len(self.steps), action=action,
            explanation=explanation, highlights=list(highlights), stateData=deepcopy(self.state)))
