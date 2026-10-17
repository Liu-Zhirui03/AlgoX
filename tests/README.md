# Tests

Automated checks belong here, including backend connection handling and
algorithm-step validation tests as those features are implemented.

`test_ollama.py` checks ready and missing-model states, malformed responses,
HTTP/connection failures, and timeouts. It uses Python's built-in `unittest`
and mocks the service, so Ollama does not need to run for these tests.

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

See [setup instructions](../Setup.md) for live startup and verification limits.

`test_bubble_sort.py` checks the demonstration and compares all 364 lists of
length zero through five over {-1, 0, 1} against Python sorting, while checking
that the input is preserved and a new list is returned.

`test_trace.py` checks adjacent swaps, unchanged comparison frames, value
preservation, final positions, immutable snapshots, early exit, and the maximum
input size. API tests also check initial and final snapshots in each response.

`test_algorithms_api.py` verifies shared catalog and dispatch routes, default
and custom inputs, 404/422 responses, compatibility aliases, and preservation
of renderer-specific step fields. A test-only graph adapter proves that another
input/state shape can be registered without changing `main.py`.

`test_partition_merge.py` checks both new sorts against Python sorting for all
364 short lists over {-1, 0, 1}, plus 20-element and safe-integer boundary cases.
It verifies exact swaps, pivot placement, buffer appends (including left-first
ties), copy-back, value preservation, and independent frame lists.
`test_algorithms_api.py` also covers both defaults, custom inputs, sample syntax,
compatibility routes, and input rejection. The suite now contains 23 tests.
