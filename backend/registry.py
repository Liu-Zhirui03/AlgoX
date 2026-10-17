"""Explicit allowlist of supported algorithms; never import from URL text."""

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel

from backend.algorithms import bubble_sort, quick_sort, merge_sort
from backend.schemas import AlgorithmInfo, AlgorithmResult


@dataclass(frozen=True)
class AlgorithmDefinition:
    id: str
    title: str
    category: str
    renderer: str
    playground_file: str
    input_model: type[BaseModel]
    default_input: dict[str, Any]
    run: Callable[..., AlgorithmResult]

    def info(self) -> AlgorithmInfo:
        return AlgorithmInfo(
            id=self.id, title=self.title, category=self.category,
            renderer=self.renderer, playgroundUrl=f"/algorithms/{self.id}",
            inputSchema=self.input_model.model_json_schema(),
        )


# Add one definition here after implementing an algorithm module and its UI.
ALGORITHMS = {
    bubble_sort.ALGORITHM_ID: AlgorithmDefinition(
        id=bubble_sort.ALGORITHM_ID,
        title=bubble_sort.TITLE,
        category=bubble_sort.CATEGORY,
        renderer=bubble_sort.RENDERER,
        playground_file=bubble_sort.PLAYGROUND_FILE,
        input_model=bubble_sort.BubbleSortInput,
        default_input=bubble_sort.DEFAULT_INPUT,
        run=bubble_sort.run,
    ),
    quick_sort.ALGORITHM_ID: AlgorithmDefinition(
        id=quick_sort.ALGORITHM_ID, title=quick_sort.TITLE,
        category=quick_sort.CATEGORY, renderer=quick_sort.RENDERER,
        playground_file=quick_sort.PLAYGROUND_FILE, input_model=quick_sort.QuickSortInput,
        default_input=quick_sort.DEFAULT_INPUT, run=quick_sort.run,
    ),
    merge_sort.ALGORITHM_ID: AlgorithmDefinition(
        id=merge_sort.ALGORITHM_ID, title=merge_sort.TITLE,
        category=merge_sort.CATEGORY, renderer=merge_sort.RENDERER,
        playground_file=merge_sort.PLAYGROUND_FILE, input_model=merge_sort.MergeSortInput,
        default_input=merge_sort.DEFAULT_INPUT, run=merge_sort.run,
    ),
}
