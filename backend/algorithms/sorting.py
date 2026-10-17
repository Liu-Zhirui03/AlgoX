"""Input and frame contracts shared by integer-array sorting adapters."""

from typing import Annotated
from pydantic import BaseModel, Field, StrictInt
from backend.schemas import VisualizationStep

SafeInteger = Annotated[StrictInt, Field(ge=-9007199254740991, le=9007199254740991)]


class IntegerArrayInput(BaseModel):
    values: list[SafeInteger] = Field(min_length=1, max_length=20)


class ArraySortStep(VisualizationStep):
    action: str
    stateData: list[int]
    highlights: list[int]
    sortedIndices: list[int]
    activeRange: list[int] = Field(default_factory=list)
    pivotIndex: int | None = None
    buffer: list[int] | None = None
