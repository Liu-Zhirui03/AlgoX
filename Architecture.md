# AlgoX architecture

## Selected direction: local Ollama integration

The user has selected Ollama, superseding the earlier built-in-only direction.
The connection-status page and endpoint are implemented. Step generation,
validation of model output remain planned. Deterministic Bubble Sort traces,
Canvas rendering, and playback are implemented for the built-in example. The website also displays
a built-in Bubble Sort example through `GET /api/algorithms/bubble-sort`, including
source, custom input/output, and execution steps, independent of Ollama.

The recommended initial design asks Ollama for JSON steps and uses built-in
Canvas/SVG renderers. Executable model-generated rendering code remains a
separate proposal requiring an isolation design.

## Planned data flow

1. Accept a natural-language algorithm request and input data.
2. Validate the request and check supported algorithms and data shapes.
3. Send a schema-constrained request to a local Ollama model.
4. Parse and validate the returned steps, state transitions, and final result.
5. Pass the accepted trace to the playback controller.
6. Draw each snapshot with its highlights and explanation using Canvas/SVG.
7. Display the Python sample in a separate, copyable code panel as plain text.

Keep the model connection, validation, step data, rendering, and playback
separate. Valid JSON does not guarantee a correct algorithm trace.

## Local API

The local API base URL is `http://localhost:11434/api`. The planned connection
can use `POST /api/chat`, a downloaded local model, `stream: false`, and a JSON
schema in `format`. Parse the generated JSON from `message.content` and validate
it in the application.

References: [API introduction](https://docs.ollama.com/api/introduction) and
[structured outputs](https://docs.ollama.com/capabilities/structured-outputs).

Local inference avoids a paid API dependency, while using local computing
resources. Offline operation requires downloaded dependencies and model files,
local assets, and a running Ollama service; it must be verified.

## Agreed MVP

- Frontend: HTML, CSS, and JavaScript.
- Local server: Python with FastAPI, with the browser communicating through the server
  to Ollama.
- Local model: `qwen2.5-coder:3b`; the local API lists it as available.
- First algorithm: Bubble Sort. Renderer: Canvas.
- Sample code: Python, generated for supported algorithms and displayed as text.
  A built-in reference panel now exists. Model-generated code remains planned.
  Use `sampleCode.language` and `sampleCode.source` in the draft contract.
  Check syntax without executing the code. Syntax validity and correct traces
  do not establish that the sample code is semantically correct.

## Open decisions

- Algorithm-specific schemas, correctness checks, input limits, timeouts,
  and handling of unavailable services or invalid output.

Use an isolated project environment when installing dependencies rather than
Anaconda's base environment. FastAPI and Uvicorn are installed in `.venv/`,
with versions recorded in `requirements.txt`.

## Implemented connection check

- `backend/main.py`: serves `/`, local assets, and `GET /api/status`.
- `backend/ollama.py`: checks the local model list with a five-second timeout
  and translates failures into connection states. No generation is performed.
- `frontend/index.html` and `frontend/assets/`: accessible status text and a
  retry button, with separate CSS and JavaScript and no external assets.
- `tests/test_ollama.py`: model-list and connection failure checks.

Offline styling requires
local assets rather than a live CDN. Hosted AI backends are outside the current
scope. No automatic built-in step-generation fallback has been selected.

See [Prompts.md](Prompts.md) and [Setup.md](Setup.md).

## Implemented algorithm dispatch

Website selection -> `main.py` -> `registry.py` -> `algorithms/<name>.py`
-> shared result envelope -> matching browser renderer and playback.

The catalog endpoint `GET /api/algorithms` exposes each registered ID, category,
renderer, playground URL, and input JSON schema. GET/POST
`/api/algorithms/{id}` use the same routes for all registered algorithms.
Unsupported IDs return 404; algorithm-specific input failures return 422.
Legacy `/api/examples/{id}` requests use the same dispatcher.

Modules own their input models, defaults, deterministic trace logic, and result
assembly. `schemas.py` defines shared metadata, Python-source, input/output, and
step fields while allowing algorithm-specific state shapes and step extensions.
The first module uses the existing pure reference in `examples/`.
There is no new Ollama generation behavior yet.

The current browser controls and `array-bars` Canvas renderer support integer
arrays. Different structures require a matching renderer and input interface;
the generic API alone does not provide graph or tree visualization support.

## Additional sorting adapters

`quick_sort.py` uses last-element Lomuto partitioning and records pivot, compare,
swap, and partition-complete frames. Fixed pivots are marked as final positions.
`merge_sort.py` records recursive splits, comparisons, temporary-buffer appends,
and full-range copy-back. Equal values are taken from the left range first.
The main array only changes at copy-back, so values are preserved in every frame.

Both adapters reuse `sorting.py` integer input validation and array frame fields.
The Canvas renderer reads optional `activeRange`, `pivotIndex`, and `buffer` fields;
playback timing remains shared. Pure Python references are displayed as text.
