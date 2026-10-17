"""Merge Sort adapter with recursive splits and visible temporary buffers."""

from inspect import getsource
from backend.algorithms.sorting import ArraySortStep, IntegerArrayInput
from backend.schemas import AlgorithmResult
from examples.merge_sort import merge_sort

ALGORITHM_ID = "merge-sort"
TITLE = "Merge Sort"
CATEGORY = "Sorting and Searching Algorithms"
RENDERER = "array-bars"
DEFAULT_INPUT = {"values": [5, 2, 8, 1]}
PLAYGROUND_FILE = "merge-sort.html"


class MergeSortInput(IntegerArrayInput):
    pass


def merge_sort_steps(values: list[int]) -> list[ArraySortStep]:
    current = list(values)
    steps = []

    def record(action, explanation, highlights=(), active=(), buffer=None):
        steps.append(ArraySortStep(
            stepIndex=len(steps), action=action, explanation=explanation,
            stateData=current.copy(), highlights=list(highlights),
            sortedIndices=list(range(len(current))) if action == "complete" else [],
            activeRange=list(active), buffer=None if buffer is None else list(buffer),
        ))

    def sort(low, high):
        if low >= high:
            return
        middle = (low + high) // 2
        record("split", f"Split indexes {low}-{high} into {low}-{middle} and {middle + 1}-{high}.", active=(low, high))
        sort(low, middle)
        sort(middle + 1, high)
        left, right = low, middle + 1
        buffer = []
        record("merge_start", f"Merge sorted ranges {low}-{middle} and {middle + 1}-{high} into a temporary buffer.", active=(low, high), buffer=buffer)
        while left <= middle and right <= high:
            record("compare", f"Compare {current[left]} at index {left} and {current[right]} at index {right}. Select the smaller; ties take the left value.", (left, right), (low, high), buffer)
            if current[left] <= current[right]:
                source = left
                left += 1
            else:
                source = right
                right += 1
            buffer.append(current[source])
            record("take", f"Append {current[source]} from index {source} to buffer position {len(buffer) - 1}. The main array stays unchanged until copy-back.", (source,), (low, high), buffer)
        for source in list(range(left, middle + 1)) + list(range(right, high + 1)):
            buffer.append(current[source])
            record("take", f"Append remaining value {current[source]} from index {source} to buffer position {len(buffer) - 1}.", (source,), (low, high), buffer)
        current[low:high + 1] = buffer
        record("merge", f"Copy the completed buffer back to indexes {low}-{high}. This range is now sorted; larger merges may still move its values.", range(low, high + 1), (low, high), buffer)

    record("initial", "Start with the submitted numbers. Split into smaller ranges, then merge them.")
    sort(0, len(current) - 1)
    record("complete", "Finished. All merged ranges form one sorted array.")
    return steps


def run(payload: MergeSortInput) -> AlgorithmResult:
    return AlgorithmResult(
        algorithmId=ALGORITHM_ID, title=TITLE, renderer=RENDERER,
        source=getsource(merge_sort), input=payload.values,
        output=merge_sort(payload.values), steps=merge_sort_steps(payload.values),
    )
