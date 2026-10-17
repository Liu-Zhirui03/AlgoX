"""Bubble Sort adapter: input rules, snapshots, and reference result assembly."""

from inspect import getsource
from typing import Literal


from backend.schemas import AlgorithmResult, VisualizationStep
from backend.algorithms.sorting import IntegerArrayInput
from examples.bubble_sort import bubble_sort

ALGORITHM_ID = "bubble-sort"
TITLE = "Bubble Sort"
CATEGORY = "Sorting and Searching Algorithms"
RENDERER = "array-bars"
DEFAULT_INPUT = {"values": [5, 2, 8, 1]}
PLAYGROUND_FILE = "bubble-sort.html"

class BubbleSortInput(IntegerArrayInput):
    pass


class SortStep(VisualizationStep):
    action: Literal["initial", "compare", "swap", "pass_complete", "complete"]
    stateData: list[int]
    highlights: list[int]
    sortedIndices: list[int]


def bubble_sort_steps(values: list[int]) -> list[SortStep]:
    current = list(values)
    steps = []
    settled = []

    def record(action, explanation, highlights=None):
        steps.append(SortStep(
            stepIndex=len(steps), action=action, stateData=current.copy(),
            highlights=list(highlights or []), sortedIndices=settled.copy(),
            explanation=explanation,
        ))

    record("initial", "Start with the submitted numbers. Compare adjacent elements from left to right.")
    for end in range(len(current) - 1, 0, -1):
        swapped = False
        for index in range(end):
            left, right = current[index], current[index + 1]
            decision = "The left value is larger, so swap next." if left > right else "They are in order; no swap is needed."
            record("compare", f"Compare indexes {index} and {index + 1}: {left} and {right}. {decision}", [index, index + 1])
            if left > right:
                current[index], current[index + 1] = right, left
                swapped = True
                record("swap", f"Swap {left} and {right} at indexes {index} and {index + 1}.", [index, index + 1])
        settled = list(range(end, len(current)))
        record("pass_complete", f"Pass complete. Index {end} now holds its final value, {current[end]}.")
        if not swapped:
            break
    settled = list(range(len(current)))
    record("complete", "Finished. All values are in ascending order.")
    return steps


def run(payload: BubbleSortInput) -> AlgorithmResult:
    return AlgorithmResult(
        algorithmId=ALGORITHM_ID,
        title=TITLE,
        renderer=RENDERER,
        source=getsource(bubble_sort),
        input=payload.values,
        output=bubble_sort(payload.values),
        steps=bubble_sort_steps(payload.values),
    )
