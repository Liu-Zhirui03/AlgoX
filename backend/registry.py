"""Explicit allowlist of supported algorithms; never import from URL text."""

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel

from backend.algorithms import bubble_sort, quick_sort, merge_sort, binary_search, hash_search, dijkstra, kruskal, prim, huffman, activity_selection, fractional_knapsack
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
    binary_search.ALGORITHM_ID: AlgorithmDefinition(
        id=binary_search.ALGORITHM_ID, title=binary_search.TITLE,
        category=binary_search.CATEGORY, renderer=binary_search.RENDERER,
        playground_file=binary_search.PLAYGROUND_FILE, input_model=binary_search.BinarySearchInput,
        default_input=binary_search.DEFAULT_INPUT, run=binary_search.run,
    ),
    hash_search.ALGORITHM_ID: AlgorithmDefinition(
        id=hash_search.ALGORITHM_ID, title=hash_search.TITLE,
        category=hash_search.CATEGORY, renderer=hash_search.RENDERER,
        playground_file=hash_search.PLAYGROUND_FILE, input_model=hash_search.HashSearchInput,
        default_input=hash_search.DEFAULT_INPUT, run=hash_search.run,
    ),
    dijkstra.ALGORITHM_ID: AlgorithmDefinition(
        id=dijkstra.ALGORITHM_ID, title=dijkstra.TITLE,
        category=dijkstra.CATEGORY, renderer=dijkstra.RENDERER,
        playground_file=dijkstra.PLAYGROUND_FILE, input_model=dijkstra.DijkstraInput,
        default_input=dijkstra.DEFAULT_INPUT, run=dijkstra.run,
    ),
    kruskal.ALGORITHM_ID: AlgorithmDefinition(
        id=kruskal.ALGORITHM_ID, title=kruskal.TITLE,
        category=kruskal.CATEGORY, renderer=kruskal.RENDERER,
        playground_file=kruskal.PLAYGROUND_FILE, input_model=kruskal.GraphInput,
        default_input=kruskal.DEFAULT_INPUT, run=kruskal.run,
    ),
    prim.ALGORITHM_ID: AlgorithmDefinition(
        id=prim.ALGORITHM_ID, title=prim.TITLE,
        category=prim.CATEGORY, renderer=prim.RENDERER,
        playground_file=prim.PLAYGROUND_FILE, input_model=prim.StartGraphInput,
        default_input=prim.DEFAULT_INPUT, run=prim.run,
    ),
    huffman.ALGORITHM_ID: AlgorithmDefinition(
        id=huffman.ALGORITHM_ID, title=huffman.TITLE,
        category=huffman.CATEGORY, renderer=huffman.RENDERER,
        playground_file=huffman.PLAYGROUND_FILE, input_model=huffman.HuffmanInput,
        default_input=huffman.DEFAULT_INPUT, run=huffman.run,
    ),
    activity_selection.ALGORITHM_ID: AlgorithmDefinition(
        id=activity_selection.ALGORITHM_ID, title=activity_selection.TITLE,
        category=activity_selection.CATEGORY, renderer=activity_selection.RENDERER,
        playground_file=activity_selection.PLAYGROUND_FILE, input_model=activity_selection.ActivityInput,
        default_input=activity_selection.DEFAULT_INPUT, run=activity_selection.run,
    ),
    fractional_knapsack.ALGORITHM_ID: AlgorithmDefinition(
        id=fractional_knapsack.ALGORITHM_ID, title=fractional_knapsack.TITLE,
        category=fractional_knapsack.CATEGORY, renderer=fractional_knapsack.RENDERER,
        playground_file=fractional_knapsack.PLAYGROUND_FILE, input_model=fractional_knapsack.KnapsackInput,
        default_input=fractional_knapsack.DEFAULT_INPUT, run=fractional_knapsack.run,
    ),
}
