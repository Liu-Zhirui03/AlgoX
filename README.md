# AlgoX

Adaptive Generative Algorithm Visualizer.

Explore algorithms and data structures through interactive steps, Canvas/SVG
visualizations, and copyable Python examples.

## Project goal

Build a local learning tool where users choose a supported algorithm, provide
input, and explore its execution with clear explanations and playback controls.
The project also develops skills in algorithm validation, frontend data flow,
animation, and structured model output.

The planned AI integration uses local Ollama with validated JSON and built-in
renderers. Local inference requires no paid API, account, or API key. Offline
operation after dependency and model downloads remains a verification target.

## Current features

- An algorithm library grouped into expandable categories.
- Interactive algorithm playgrounds with custom input and Python reference code.
- Deterministic execution traces, step explanations, and Canvas visualization.
- Play/pause, previous/next, reset, seeking, and playback speed controls.
- A local Ollama connection check with retry and error feedback.

Model-generated steps and Python samples remain planned. Existing playgrounds
use built-in implementations and work independently of Ollama.

## Run locally

See [Setup.md](Setup.md) for installation and environment preparation. From the
repository root, start the server:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open [AlgoX locally](http://127.0.0.1:8000), expand a library category, and choose
an available algorithm to enter its playground.

## Architecture

The stack is HTML, CSS, JavaScript, Python/FastAPI, and Canvas, with local Ollama
integration planned for generation.

`backend/main.py` routes requests through an explicit algorithm registry to
separate modules in `backend/algorithms/`. Modules define their input rules,
state shapes, and execution logic. Shared schemas, browser rendering, and
playback remain separate.

The browser requests `/api/algorithms/{id}`. The catalog at
`GET /api/algorithms` lists supported algorithms and their input schemas.
New algorithms also need matching input controls, a renderer, and a library card.

## Algorithm libraries

- Sorting and Searching Algorithms
- Greedy Algorithms
- Divide and Conquer Algorithms
- Dynamic Programming
- Backtracking and Branch and Bound Methods

The website shows available playgrounds and planned entries. Algorithm-specific
behavior, examples, and input details belong in the
[example documentation](examples/README.md) and relevant module documentation.

## Repository guide

- [backend/](backend/README.md): API, registry, algorithm modules, and Ollama connection.
- [frontend/](frontend/README.md): pages, local assets, rendering, and playback.
- [examples/](examples/README.md): standalone Python references and algorithm details.
- [tests/](tests/README.md): correctness, API, trace, and connection checks.
- [Setup.md](Setup.md): installation and startup.
- [Architecture.md](Architecture.md): architecture and integration design.
- [Workflow.md](Workflow.md): development stages and milestones.
- [Prompts.md](Prompts.md): draft model contracts and validation requirements.
- [AGENTS.md](AGENTS.md): project working guidance.
- `requirements.txt`: pinned Python dependencies.
- `LICENSE`: project license.

## Next development stage

Add shared Ollama generation with algorithm-specific prompts and correctness
checks, then verify failure handling and offline operation. Expand supported
algorithms incrementally. See [Workflow.md](Workflow.md) for the full plan.
