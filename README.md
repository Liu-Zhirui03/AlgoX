# AlgoX

Adaptive Generative Algorithm Visualizer.

Explore how algorithms and data structures work through interactive steps
and Canvas/SVG animations.

## Project concept

Build a front-end interface where users select or search for a supported
algorithm or data structure and visualize its execution using Canvas or SVG.
Potential examples include A* pathfinding, red-black tree insertion, and sorting
processes. The first supported algorithm will be Bubble Sort. The planned result
will also include a copyable Python sample illustrating the selected algorithm;
a built-in Python example is now displayed on the website. Model-generated
code generation remains planned. Built-in Bubble Sort, Quick Sort, and Merge Sort examples include
deterministic execution traces and live Canvas playback.

The chosen approach is local step generation through Ollama, with validated JSON
and built-in Canvas/SVG renderers recommended for the first version. Users will not
need a ChatGPT/OpenAI account, Codex installation, API key, subscription, or paid
service for local inference. Offline operation is a target after dependency and
model downloads, with Ollama running locally. Codex may assist development,
but will not run inside the app.

The aim is to make algorithms easier to understand while exploring front-end
data flow, algorithm step generation, and DOM/Canvas manipulation.

## Learning goals

- Map algorithm state snapshots to UI updates and Canvas/SVG rendering.
- Learn animation timing with `requestAnimationFrame` and coordinate transforms.
- Understand algorithm invariants and time/space complexity through comparisons,
  swaps, tree rotations, and pathfinding states.
- Learn structured LLM output and schema validation through Ollama integration.
  Function calling remains a possible later learning topic.

## Selected AI direction

The user's decision to connect Ollama supersedes the earlier built-in-only plan.
Natural-language requests will be limited to supported algorithms and renderer
capabilities. Generated rendering code remains a separate proposal. Support for
arbitrary algorithms has not been established.

## Current stage

Environment preparation is complete: FastAPI and Uvicorn are installed in the
project-local `.venv/`, with dependencies pinned in `requirements.txt`.
A minimal FastAPI app now serves an Ollama connection-status page. Start it
from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open [AlgoX locally](http://127.0.0.1:8000). See [Setup.md](Setup.md) for installation.
Selecting Bubble Sort in the algorithm library leads to `/algorithms/bubble-sort`, where a visualization
below the input/code panel shows each comparison and swap. Play/pause, previous,
next, reset, a step slider, and playback speed are available. Model-generated
steps remain planned.
The MVP is agreed: HTML, CSS, JavaScript, a Python/FastAPI local server, Canvas,
Bubble Sort, and `qwen2.5-coder:3b`. Ollama's local API has been reached and lists
the selected model. Generation through the API still needs testing.

## Repository files

- `backend/`: shared FastAPI entry point, algorithm registry, common schemas,
  separate modules in `backend/algorithms/`, and Ollama integration.
- `frontend/`: browser HTML, CSS, JavaScript, and Canvas rendering.
- `tests/`: automated checks for implemented behavior.
- [examples/](examples/README.md): runnable Python algorithm references, starting
  with Bubble Sort. The website displays the same reference implementation.
  This built-in example works independently of Ollama.
- `.editorconfig`: shared indentation, encoding, and whitespace conventions.
- `.gitattributes`: consistent text line endings across operating systems.
- `.gitignore`: excludes local secrets, dependencies, and generated files.
- `.vscode/settings.json`: workspace editor defaults.
- `AGENTS.md`: project context and incremental development guidance.
- `requirements.txt`: pinned Python dependencies; see [Setup.md](Setup.md).
- `Workflow.md`: development stages, milestones, and application runtime flow.
- [Architecture.md](Architecture.md): planned Ollama architecture and open decisions.
- [Prompts.md](Prompts.md): draft model prompt, JSON example, and validation needs.
- [Setup.md](Setup.md): current setup status and local-model preparation.
- `LICENSE`: project license.

## Planned workflow

1. Agree on the application stack, local model, renderer, and first algorithm.
2. Verify Ollama access and create the smallest runnable application scaffold.
3. Integrate structured step generation, validation, and basic visualization.
4. Add playback controls and step explanations.
5. Verify offline operation and expand supported algorithms with correctness checks.

Work through these stages individually. Discuss the next stage before adding
its implementation.

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

## Modular algorithm framework

AlgoX uses one shared API entry point and separate Python algorithm adapters.
`backend/main.py` dispatches through `backend/registry.py` to the selected module
under `backend/algorithms/`. `backend/schemas.py` defines the common result
contract; individual modules define their own input rules and state shapes.

The browser calls `/api/algorithms/{id}` using the playground's algorithm ID.
`GET /api/algorithms` lists supported algorithms and their input schemas.
The first module is a reference test case for this framework. New algorithms
also need an appropriate input interface, library card, and renderer.
See [backend/README.md](backend/README.md) for the extension steps.
Model generation remains a future stage.

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
