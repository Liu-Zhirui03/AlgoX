# Algorithm examples

`bubble_sort.py` is a hand-written Python reference example. It sorts integers
in ascending order and preserves the original input. It handles empty lists,
single values, duplicates, negative values, and already sorted input.

From the repository root:

```powershell
.\.venv\Scripts\python.exe examples/bubble_sort.py
```

Expected output:

```text
Input:  [5, 2, 8, 1]
Sorted: [1, 2, 5, 8]
```

The loop compares adjacent values and swaps them if the left value is larger.
Each pass places the largest remaining value at the end. A pass without swaps
ends the algorithm early. Worst-case time is O(n squared); already sorted input
takes O(n). Copying the input takes O(n) space.

This example can run standalone and is also displayed on the AlgoX website.
The backend imports this same function to compute the sample result and reads
its source for the copyable code panel. The standalone script does not use Ollama or animation; the website records its execution for playback.

`quick_sort.py` and `merge_sort.py` are also standalone Python references:

```powershell
.\.venv\Scripts\python.exe examples/quick_sort.py
.\.venv\Scripts\python.exe examples/merge_sort.py
```

Both return a sorted copy. Quick Sort uses a last-element pivot and Lomuto
partitioning: average O(n log n), worst O(n squared) time, with a copied array
and recursion stack. Merge Sort is stable, takes O(n log n) time, and uses O(n)
auxiliary space. The website displays these same functions.

## Sorting playground input and API

The current sorting playgrounds accept 1-20 integers separated by commas or
spaces, including negative values and duplicates. Empty entries, decimals,
invalid text, and values outside the browser's exact integer range
(plus/minus 9,007,199,254,740,991) are rejected. The original input is preserved.

Choose Sort my numbers, or press Enter, to submit. Use example restores the
default input. Each result includes the Python reference, submitted input,
sorted output, and execution snapshots.

`POST /api/algorithms/{id}` accepts `{"values": [9, 3, 7, 1]}` for the registered
sorting adapters. The backend validates input independently; invalid requests
return HTTP 422. GET on the same endpoint returns the default example.
See [backend documentation](../backend/README.md) for the shared API contract.

## Search references

`binary_search.py` accepts ascending values and a target, returning the first
matching index or -1. Its search takes O(log n) time and O(1) extra space. The
website validates ascending input separately in O(n); it never silently sorts it.

`hash_search.py` builds a separate-chaining table using `value % bucket_count`.
Each entry retains its original index; duplicates stay in insertion order. Python
modulo gives a nonnegative bucket for negative values. Building the table costs
O(n); lookup is expected O(1 + n/m) for m buckets and worst-case O(n). Each website
request rebuilds the table, so its total work includes the O(n) build.

```powershell
.\.venv\Scripts\python.exe examples/binary_search.py
.\.venv\Scripts\python.exe examples/hash_search.py
```

The website accepts 1-20 safe integers and a target. Binary Search requires
ascending input. Hash Search allows arbitrary order and 3-16 buckets (default 7).
Both show the first original index or a not-found result and preserve the input.
POST `/api/algorithms/binary-search` accepts
`{"values": [1, 2, 2, 4], "target": 2}`. POST `/api/algorithms/hash-search` accepts
`{"values": [10, 17, 24], "target": 24, "bucketCount": 7}`.

## Greedy graph references

`dijkstra.py`, `kruskal.py`, and `prim.py` are pure Python references displayed by
the graph playgrounds. They accept a node list and `(source, target, weight)`
edge tuples for an undirected graph. Dijkstra and Prim also take a start label.

- Dijkstra uses an adjacency list and linear minimum-distance scans, taking
  O(V squared + E) time. Nonnegative weights are required. Null distances mean
  unreachable nodes; the API additionally reconstructs each reachable path.
- Kruskal sorts edges, then uses path compression and union by rank to accept
  edges between different components. Its main cost is O(E log E).
- Prim scans all crossing edges at each step and restarts at unvisited components.
  This educational version takes O(VE + V squared) time. Both MST routines return
  selected input edge indexes and total weight and handle negative weights.

The graph adapters validate input before invoking these references. Disconnected
graphs produce minimum spanning forests; isolated vertices remain separate
components. Equal edge weights are resolved by input edge index, while equal
Dijkstra node distances follow input node order. Chosen trees can differ between
Kruskal and Prim when multiple minimum solutions exist.

## Remaining Greedy references

`huffman.py` accepts `(symbol, frequency)` pairs and builds a prefix tree by
merging the two minimum-frequency roots. Equal priorities use creation order.
The returned `codes` map is prefix-free; `weightedCost` is the sum of frequency
times code length. A single symbol uses code 0. Tree construction is O(n log n),
with additional work to materialize the code strings.

`activity_selection.py` accepts `(name, start, finish)` intervals and returns
indexes of a maximum-cardinality non-overlapping schedule. It sorts by finish,
keeping input order for ties, then accepts compatible intervals in O(n log n)
time overall. Intervals are half-open [start, finish), so one may start exactly
when the previous one ends. This is unweighted interval scheduling.

`fractional_knapsack.py` accepts `(name, positive_weight, nonnegative_value)` items
and a nonnegative capacity. It takes items by descending exact value/weight,
keeping input order for ties, allowing one final partial item. Zero-value items
are skipped. The algorithm takes O(n log n) time; exact rational calculations
are converted to floats only for the returned fractions and total value.

Example API bodies:

```json
{"symbols": [{"symbol": "A", "frequency": 5}, {"symbol": "B", "frequency": 9}]}
```

```json
{"activities": [{"name": "A", "start": 0, "finish": 2}, {"name": "B", "start": 2, "finish": 3}]}
```

```json
{"items": [{"name": "A", "weight": 3, "value": 10}], "capacity": 1}
```

Send them to `/api/algorithms/huffman`, `/api/algorithms/activity-selection`, and
`/api/algorithms/fractional-knapsack`, respectively. Input labels are unique
and use 1-8 ASCII letters, digits, or underscores. The adapters validate integer
bounds and item counts before running these references.
