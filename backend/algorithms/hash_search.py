"""Hash Search adapter showing table construction, collisions, and lookup."""

from inspect import getsource
from typing import Annotated
from pydantic import BaseModel, Field, StrictInt
from backend.algorithms.searching import SearchInput
from backend.schemas import AlgorithmResult, VisualizationStep
from examples.hash_search import hash_search

ALGORITHM_ID = "hash-search"
TITLE = "Hash Search"
CATEGORY = "Sorting and Searching Algorithms"
RENDERER = "hash-search"
DEFAULT_INPUT = {"values": [10, 17, 24, 3, 10], "target": 24, "bucketCount": 7}
PLAYGROUND_FILE = "hash-search.html"


class HashSearchInput(SearchInput):
    bucketCount: Annotated[StrictInt, Field(ge=3, le=16)] = 7


class HashEntry(BaseModel):
    value: int
    index: int


class HashState(BaseModel):
    values: list[int]
    target: int
    buckets: list[list[HashEntry]]
    bucketIndex: int | None = None
    entryIndex: int | None = None
    inputIndex: int | None = None
    foundIndex: int | None = None


class HashStep(VisualizationStep):
    action: str
    stateData: HashState


def hash_search_steps(values: list[int], target: int, bucket_count: int = 7) -> list[HashStep]:
    buckets = [[] for _ in range(bucket_count)]
    steps = []

    def record(action, explanation, bucket=None, entry=None, source=None, found=None):
        steps.append(HashStep(
            stepIndex=len(steps), action=action, explanation=explanation,
            highlights=[] if bucket is None else [bucket],
            stateData=HashState(values=list(values), target=target,
                buckets=[[item.model_copy() for item in chain] for chain in buckets],
                bucketIndex=bucket, entryIndex=entry, inputIndex=source, foundIndex=found),
        ))

    record("initial", f"Build {bucket_count} buckets using value modulo {bucket_count}, then look up {target}. Entries retain their original indexes.")
    for index, value in enumerate(values):
        bucket = value % bucket_count
        record("hash", f"Input index {index}: {value} mod {bucket_count} = {bucket}.", bucket, source=index)
        if buckets[bucket]:
            record("collision", f"Bucket {bucket} already has entries. Resolve this collision by appending to its chain.", bucket, source=index)
        buckets[bucket].append(HashEntry(value=value, index=index))
        record("insert", f"Append value {value} (original index {index}) to bucket {bucket}.", bucket, len(buckets[bucket]) - 1, index)
    bucket = target % bucket_count
    record("lookup", f"Search target {target}: {target} mod {bucket_count} = {bucket}. Inspect only this bucket's chain.", bucket)
    for position, item in enumerate(buckets[bucket]):
        record("compare", f"Compare target {target} with {item.value} (original index {item.index}) in bucket {bucket}.", bucket, position)
        if item.value == target:
            record("complete", f"Found {target} at original index {item.index}. Insertion order gives the first duplicate.", bucket, position, found=item.index)
            return steps
    record("complete", f"Target {target} is not present: bucket {bucket}'s chain has no matching value.", bucket, found=-1)
    return steps


def run(payload: HashSearchInput) -> AlgorithmResult:
    index = hash_search(payload.values, payload.target, payload.bucketCount)
    return AlgorithmResult(
        algorithmId=ALGORITHM_ID, title=TITLE, renderer=RENDERER,
        source=getsource(hash_search), input=payload.model_dump(),
        output={"found": index >= 0, "index": index},
        steps=hash_search_steps(payload.values, payload.target, payload.bucketCount),
    )
