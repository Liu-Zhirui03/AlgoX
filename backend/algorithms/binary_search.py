"""Binary Search adapter with shrinking bounds and first-match candidates."""

from inspect import getsource
from pydantic import BaseModel, model_validator
from backend.algorithms.searching import SearchInput
from backend.schemas import AlgorithmResult, VisualizationStep
from examples.binary_search import binary_search

ALGORITHM_ID = "binary-search"
TITLE = "Binary Search"
CATEGORY = "Sorting and Searching Algorithms"
RENDERER = "binary-search"
DEFAULT_INPUT = {"values": [1, 2, 5, 8, 12, 16, 23], "target": 8}
PLAYGROUND_FILE = "binary-search.html"


class BinarySearchInput(SearchInput):
    @model_validator(mode="after")
    def require_sorted(self):
        if any(left > right for left, right in zip(self.values, self.values[1:])):
            raise ValueError("Binary Search requires numbers in ascending order.")
        return self


class BinaryState(BaseModel):
    values: list[int]
    target: int
    low: int
    high: int
    middle: int | None = None
    candidate: int | None = None
    foundIndex: int | None = None


class BinaryStep(VisualizationStep):
    action: str
    stateData: BinaryState


def binary_search_steps(values: list[int], target: int) -> list[BinaryStep]:
    low, high = 0, len(values) - 1
    candidate = None
    steps = []

    def record(action, explanation, middle=None, found=None):
        steps.append(BinaryStep(
            stepIndex=len(steps), action=action, explanation=explanation,
            highlights=[] if middle is None else [middle],
            stateData=BinaryState(values=list(values), target=target, low=low,
                                  high=high, middle=middle, candidate=candidate, foundIndex=found),
        ))

    record("initial", f"Search for {target} in the ascending array. All indexes refer to the submitted input.")
    while low <= high:
        middle = (low + high) // 2
        record("compare", f"Bounds [{low}, {high}]: compare middle index {middle}, value {values[middle]}, with target {target}.", middle)
        if values[middle] < target:
            low = middle + 1
            record("discard", f"{values[middle]} is smaller than {target}. Discard indexes up to {middle}; low becomes {low}.")
        else:
            if values[middle] == target:
                candidate = middle
                reason = f"Match at index {middle}. Keep it as a candidate and search left for an earlier duplicate."
            else:
                reason = f"{values[middle]} is larger than {target}. Discard the middle and everything to its right."
            high = middle - 1
            record("discard", reason + f" High becomes {high}.")
    result = -1 if candidate is None else candidate
    message = f"Found {target}: its first occurrence is at index {result}." if result >= 0 else f"Target {target} is not present. The search range is empty."
    record("complete", message, found=result)
    return steps


def run(payload: BinarySearchInput) -> AlgorithmResult:
    index = binary_search(payload.values, payload.target)
    return AlgorithmResult(
        algorithmId=ALGORITHM_ID, title=TITLE, renderer=RENDERER,
        source=getsource(binary_search), input=payload.model_dump(),
        output={"found": index >= 0, "index": index},
        steps=binary_search_steps(payload.values, payload.target),
    )
