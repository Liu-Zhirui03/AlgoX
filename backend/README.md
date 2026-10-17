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
