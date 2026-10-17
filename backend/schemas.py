"""Shared API contracts; algorithms supply their own input and state shapes."""

from typing import Any, Literal

from pydantic import BaseModel, SerializeAsAny


class VisualizationStep(BaseModel):
    stepIndex: int
    explanation: str
    stateData: Any
    highlights: list[int | str]


class AlgorithmResult(BaseModel):
    algorithmId: str
    title: str
    renderer: str
    language: Literal["python"] = "python"
    source: str
    input: Any
    output: Any
    steps: list[SerializeAsAny[VisualizationStep]]


class AlgorithmInfo(BaseModel):
    id: str
    title: str
    category: str
    renderer: str
    playgroundUrl: str
    inputSchema: dict[str, Any]
