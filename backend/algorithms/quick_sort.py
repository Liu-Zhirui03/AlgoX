"""Quick Sort input adapter, pivot partitions, and execution snapshots."""

from inspect import getsource
from backend.algorithms.sorting import ArraySortStep, IntegerArrayInput
from backend.schemas import AlgorithmResult
from examples.quick_sort import quick_sort

ALGORITHM_ID = "quick-sort"
TITLE = "Quick Sort"
CATEGORY = "Sorting and Searching Algorithms"
RENDERER = "array-bars"
DEFAULT_INPUT = {"values": [5, 2, 8, 1]}
PLAYGROUND_FILE = "quick-sort.html"


class QuickSortInput(IntegerArrayInput):
    pass


def quick_sort_steps(values: list[int]) -> list[ArraySortStep]:
    current = list(values)
    steps = []
    settled = set()

    def record(action, explanation, highlights=(), active=(), pivot=None):
        steps.append(ArraySortStep(
            stepIndex=len(steps), action=action, explanation=explanation,
            stateData=current.copy(), highlights=list(highlights),
            sortedIndices=sorted(settled), activeRange=list(active), pivotIndex=pivot,
        ))

    def sort(low, high):
        if low > high:
            return
        if low == high:
            settled.add(low)
            record("partition_complete", f"Index {low} is a one-element partition and is in its final position.", active=(low, high))
            return
        pivot = current[high]
        record("pivot", f"Partition indexes {low}-{high}. Choose the last value, {pivot}, as the pivot.", (high,), (low, high), high)
        boundary = low
        for index in range(low, high):
            decision = "Move it into the left partition." if current[index] <= pivot else "Leave it in the right partition."
            record("compare", f"Compare {current[index]} at index {index} with pivot {pivot}. {decision}", (index, high), (low, high), high)
            if current[index] <= pivot:
                if boundary != index:
                    current[boundary], current[index] = current[index], current[boundary]
                    record("swap", f"Swap indexes {boundary} and {index} to grow the partition of values at most {pivot}.", (boundary, index), (low, high), high)
                boundary += 1
        if boundary != high:
            current[boundary], current[high] = current[high], current[boundary]
            record("swap", f"Move pivot {pivot} from index {high} to index {boundary}.", (boundary, high), (low, high), boundary)
        settled.add(boundary)
        record("partition_complete", f"Pivot {pivot} is fixed at index {boundary}. Sort the partitions on either side.", active=(low, high))
        sort(low, boundary - 1)
        sort(boundary + 1, high)

    record("initial", "Start with the submitted numbers. Partition around a pivot, then recurse.")
    sort(0, len(current) - 1)
    settled.update(range(len(current)))
    record("complete", "Finished. All partitions are sorted in ascending order.")
    return steps


def run(payload: QuickSortInput) -> AlgorithmResult:
    return AlgorithmResult(
        algorithmId=ALGORITHM_ID, title=TITLE, renderer=RENDERER,
        source=getsource(quick_sort), input=payload.values,
        output=quick_sort(payload.values), steps=quick_sort_steps(payload.values),
    )
