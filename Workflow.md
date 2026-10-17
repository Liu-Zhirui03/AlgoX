# AlgoX workflow

Develop AlgoX one stage at a time. Review each stage with the user before
starting the next. The minimal Ollama connection check is implemented.

## Development workflow

1. **Define the MVP and prepare Ollama.** Choose the application stack, local
   model, renderer, and first algorithm. Verify local service/model availability.
   Goal: a defined first version and a reachable local model.
2. **Create the scaffold and connection.** Build a minimal page and connection
   layer; document installation and startup.
   Goal: a runnable local app that can report Ollama connection status.
3. **Generate and validate steps.** Define the algorithm-specific JSON schema,
   send requests, and check returned data and algorithm correctness. Handle
   unavailable models, timeouts, and invalid responses.
   Include a Python sample of the same algorithm in the generation contract.
   Validate its field structure and syntax separately from trace correctness.
   Goal: accepted traces with explanations and a displayable Python example.
4. **Render the visualization.** Draw snapshots using a built-in Canvas or SVG
   renderer, as recommended for the first version.
   Goal: visible algorithm states independent of model requests.
5. **Add interaction.** Include input validation, loading/error feedback,
   play/pause, next/previous step, reset, and speed controls.
   Include a separate, copyable Python code panel. Display code as text only.
   Goal: users can explore a trace and read its Python implementation.
6. **Verify the experience.** Check correctness, model failure handling,
   playback, keyboard access, responsive layout, and offline operation after
   model and dependency downloads.
   Goal: a reliable first version with documented limitations.
7. **Expand supported algorithms.** Add requests, schemas, correctness checks,
   and renderers individually.
   Goal: wider coverage without promising arbitrary algorithm support.

## Application runtime workflow

1. Start local Ollama with a downloaded model and open AlgoX locally.
2. Enter an algorithm request and data, or choose an example.
3. Validate input and supported capabilities; explain rejected requests.
4. Send the request and schema to Ollama.
5. Receive and validate JSON steps. Show errors before playback if generation
   fails or the trace is invalid.
6. Render the current state, highlights, and explanation.
7. Play, pause, step forward/backward, or adjust speed using the accepted trace.
   Playback does not require a new model call per frame.
8. Reset the trace, or submit new input to generate another trace.

## Runtime requirements

- Use local Ollama for generation; Codex remains a development aid.
- Require no paid API, OpenAI account, or API key for local inference.
- Target offline operation after dependencies and model files are downloaded.
- Validate output; valid JSON alone does not establish correctness.
- Keep hosted AI backends and executable model-generated renderers outside
  the initial integration plan.

## MVP decisions and preparation status

- Confirmed frontend: HTML, CSS, and JavaScript.
- Confirmed local server: Python with FastAPI.
- Confirmed renderer: Canvas.
- Confirmed first algorithm: Bubble Sort.
- Confirmed sample-code language: Python; generation and code display are planned.
- Confirmed model: `qwen2.5-coder:3b`.
- Verified: `GET http://localhost:11434/api/tags` succeeds and lists the model.
- Verified: Python 3.13.9 is available through Anaconda. Schema-constrained generation remains pending.

- Completed: project-local `.venv/`, FastAPI and Uvicorn installation, and
  pinned `requirements.txt`. Package imports and `pip check` pass.
- Completed: separate `backend/`, `frontend/`, and `tests/` folders.
- Completed: `GET /api/status` and a page with connection feedback and retry.
  The check lists installed models; it does not load the model or generate steps.
- Verified: six automated connection tests and live HTTP checks for the page,
  styles, script, and status endpoint. The real service reported `ready`.

The requested status endpoint and simple page are complete. Browser checks
verified initial loading, mouse and keyboard retries, all connection states,
and recovery from a simulated server error. Desktop (1280px) and mobile (390px)
screenshots were visually inspected; neither viewport had horizontal overflow.
No uncaught JavaScript errors were detected. The local service reported ready.
Discuss generation and validation (Stage 3) before implementing them.
See [Architecture.md](Architecture.md) and [Setup.md](Setup.md).

## Bubble Sort reference example

A standalone Python example is available in `examples/bubble_sort.py`, with
usage in [examples/README.md](examples/README.md). It returns a sorted copy and
is now integrated into the website through `GET /api/algorithms/bubble-sort`.
The page shows its input, sorted output, Python source, a copy button, and reload
feedback. It now also includes a dedicated algorithm page and interactive
Canvas visualization with deterministic step data. Model-generated steps
remain future work.

## Custom Bubble Sort input

The website accepts 1-20 integers separated by commas or spaces. Choose
Sort my numbers (or press Enter) to submit; Use example restores the default
input and sorts it. Negative numbers and duplicates are supported. Empty
entries, decimals, invalid text, and integers outside the browser's exact integer
range (plus/minus 9,007,199,254,740,991) are rejected before sorting.

`POST /api/algorithms/bubble-sort` accepts `{"values": [9, 3, 7, 1]}` and returns
the Python source, submitted input, and sorted output. The backend independently
validates input; invalid requests return HTTP 422. The GET endpoint still returns
the default example. This built-in example now includes deterministic steps and animation, without
model generation.

## Dedicated algorithm page and live visualization

Completed: selecting Bubble Sort in the algorithm library leads to `/algorithms/bubble-sort`. A separate Canvas
block below the playground animates the submitted list with comparison/swap
highlights, sorted positions, explanations, counters, and a textual state.
Playback supports play/pause, previous/next, reset, speed, and a step slider.
This is a deterministic built-in reference trace; model generation is pending.

Verified: 14 automated tests, including exhaustive short trace transitions,
independent snapshots, sorted-input early exit, and the 20-element reverse case.
Browser checks passed for navigation, actual Canvas updates, pause timing, seek,
completion/replay, speed, new input, and desktop/mobile widths down to 320px.
No uncaught JavaScript errors were detected. Screenshots were inspected.

## Algorithm library categories

The home page groups algorithms under five expandable parent libraries:

- Sorting and Searching Algorithms
- Greedy Algorithms
- Divide and Conquer Algorithms
- Dynamic Programming
- Backtracking and Branch and Bound Methods

Sorting and Searching Algorithms lists Bubble Sort, Quick Sort, Merge Sort,
Binary Search, and Hash Search, in that order. Bubble Sort, Quick Sort, and
Merge Sort have working playgrounds. Binary Search and Hash Search are marked
Coming soon until implemented.
The other parent libraries currently have no algorithms. Add implementations
individually after agreeing on their scope. Parent libraries expand with mouse or keyboard. Algorithm cards
remain the only home-page links into playgrounds. Connection status stays below
all five libraries.

## Modular framework milestone

Completed: shared routes in `backend/main.py`, explicit dispatch in
`backend/registry.py`, common contracts in `backend/schemas.py`, and separate
algorithm adapters under `backend/algorithms/`. The website requests the selected
algorithm through `/api/algorithms/{id}`. The first adapter verifies the framework;
future algorithms define their own input validation and renderer requirements.

Next: add shared Ollama generation through this structure, with per-algorithm
prompts and correctness checks. Model generation is not implemented in this refactor.

## Sorting playgrounds

Bubble Sort, Quick Sort, and Merge Sort each have a dedicated playground with
1-20 integer inputs, a copyable Python reference, and deterministic Canvas steps.
All support play/pause, previous/next, reset, seeking, speed, negatives, and duplicates.

- `/algorithms/quick-sort`: last-element pivot with Lomuto partitioning; shows
  comparisons, swaps, active partitions, and final pivot positions.
- `/algorithms/merge-sort`: recursive splits, stable comparisons (left on ties),
  temporary buffer appends, and copy-back for each completed merge. The main
  array stays unchanged while the current merge buffer is being filled.

Both are separate registered Python adapters under `backend/algorithms/`, with
pure references in `examples/`. They use the existing generic API routes.
These playgrounds run independently of Ollama; model generation remains planned.
