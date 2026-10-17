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
