# Backend

`main.py` serves the website, connection status, and shared algorithm routes.
It dispatches only to explicitly registered modules; URL text never controls imports.

```text
backend/
  main.py                 # Shared routes and dispatch
  registry.py             # Supported algorithms and their metadata
  schemas.py              # Common result and visualization-step contracts
  ollama.py               # Shared Ollama connection handling
  algorithms/
    __init__.py
    sorting.py            # Shared integer-array input and extended frame models
    bubble_sort.py        # Adjacent comparison and swap snapshots
    quick_sort.py         # Pivot partitions and swap snapshots
    merge_sort.py         # Recursive splits, buffers, and copy-back snapshots
    searching.py          # Shared target input
    binary_search.py      # Ascending-input validation and shrinking bounds
    hash_search.py        # Chained table construction, collisions, and lookup
```

## API

- `GET /api/algorithms`: catalog with category, renderer, playground URL,
  and each algorithm's JSON input schema.
- `GET /api/algorithms/{id}`: run the registered default input.
- `POST /api/algorithms/{id}`: validate the request with the selected module's
  input model, then invoke its runner.
- `GET /algorithms/{id}`: serve that module's registered playground HTML.
- `GET /api/status`: check local Ollama availability.

Unsupported IDs return 404. Invalid inputs return 422.
`/api/examples/{id}` remains an alias for existing clients.

## Adding an algorithm

1. Create `algorithms/<name>.py` with metadata, a Pydantic input model, default
   input, and `run(payload) -> AlgorithmResult`.
2. Keep algorithm-specific state and trace rules in that module. The first
   adapter imports its pure Python reference from `examples/` for code display.
3. Register an `AlgorithmDefinition` in `registry.py`. No new main.py route is needed.
4. Supply its playground file, library card, input controls, and matching renderer.
   The current input controller and Canvas renderer handle integer arrays;
   graphs, trees, and other shapes need their own browser adapters.
5. Test input rejection, correctness, snapshots, API dispatch, and visualization.

`schemas.py` permits different input/output and state shapes. Step subclasses can
add renderer-specific fields, which are preserved in API responses. Each module
is responsible for validating its own shape and algorithm behavior.

Ollama generation and validation of model-produced traces remain planned.
See [setup instructions](../Setup.md) for startup and tests.

## Search requests

Both searches accept `values` (1-20 safe integers) and `target` (a safe integer).
Binary Search rejects non-ascending input. Hash Search also accepts optional
`bucketCount` (3-16, default 7). Results use `{"found": true, "index": 2}` or
`{"found": false, "index": -1}`. Indexes refer to the submitted input and duplicates
return the first matching index. API routes remain shared.

Search step subclasses hold typed state objects instead of sorting arrays.
Binary snapshots include bounds, a middle index, and a candidate. Hash snapshots
include independent bucket chains with value/original-index entries.

## Greedy graph adapters

- `algorithms/graphs.py`: common undirected graph validation, typed graph states,
  deep snapshot recording, and the shared default graph.
- `algorithms/dijkstra.py`: nonnegative weights, minimum tentative-node selection,
  edge relaxation, shortest distances, predecessors, and reconstructed paths.
- `algorithms/kruskal.py`: edges in ascending weight order, union-find, cycle
  rejection, component merges, and minimum spanning forest output.
- `algorithms/prim.py`: cheapest crossing edges, visited nodes, and restarts for
  disconnected components. Prim and Kruskal share the MST playground HTML.

POST `/api/algorithms/{dijkstra|kruskal|prim}` accepts `nodes` and `edges`:
`{"nodes": ["A", "B"], "edges": [{"source": "A", "target": "B", "weight": 4}]}`.
Dijkstra and Prim also require `start`. Node labels contain 1-8 ASCII letters,
digits, or underscores; graph limits are 1-10 nodes and 0-30 edges. Integer weights
are within [-1000000, 1000000], with the additional nonnegative Dijkstra rule.

Dijkstra returns `distances`, `parents`, and `paths` keyed by node. Unreachable
distances/paths are null. MST output includes selected input edge indexes,
`totalWeight`, `components`, and `connected`. Isolated vertices are components.
All graph frames are deep copies, independent of both input and other frames.

## Coding, scheduling, and packing adapters

- `algorithms/greedy.py`: common strict integer/label types and deep snapshot recording.
- `algorithms/huffman.py`: `HuffmanInput` accepts 1-10 unique `symbols`, each with
  a label `symbol` and positive integer `frequency` (1-1000000). Frames show the
  minimum-frequency root pair, parent creation, and code assignment. The output
  contains `codes` and `weightedCost`. Equal frequencies use creation order;
  the single-symbol convention is code 0.
- `algorithms/activity_selection.py`: `ActivityInput` accepts 1-12 unique named
  `activities`, each with integer `start` and `finish` in [0, 1000000], requiring
  start < finish. Frames show earliest-finish ordering and accept/reject decisions.
  The output contains original `selected` indexes, `names`, and `count`.
- `algorithms/fractional_knapsack.py`: `KnapsackInput` accepts 1-12 unique named
  `items`, each with positive `weight` and nonnegative `value`, plus nonnegative
  `capacity`. Integer limits are 1000000. Ratios and accumulated values use
  `fractions.Fraction` before float conversion. Output fractions retain input
  order and include `totalWeight` and `totalValue`. Zero-value items are skipped.

All labels use 1-8 ASCII letters, digits, or underscores. The API routes remain
`/api/algorithms/{id}` with optional legacy aliases. Invalid inputs return 422.
