# Setup status and Ollama preparation

## Current repository

AlgoX has a runnable connection-status page and FastAPI endpoint. Algorithm
generation through Ollama remains planned; the built-in Bubble Sort example
now supports Canvas animation and step playback. The agreed stack is HTML, CSS,
JavaScript, and a Python/FastAPI local server with Canvas and Bubble Sort.
Review [Workflow.md](Workflow.md) before starting the scaffold stage.

## Repository initialization example

The supplied concept includes these commands for a new, uninitialized repository:

```sh
git init
git add .
git commit -m "feat: initial project skeleton"
```

These are reference commands, not a required step for an existing repository.
Review the files to be staged before creating a commit. No initialization or
commit is performed by this documentation update.

## Local-model preparation

Status: Ollama's local API is reachable and lists `qwen2.5-coder:3b`.
The user reports successful local execution. API generation and schema validation
have not yet been tested. Python 3.13.9 is available through Anaconda at `D:\ANACONDA\python.exe`.
The project-local `.venv/` now contains FastAPI and Uvicorn. All installed
application dependencies are pinned in `requirements.txt`; `.venv/` is ignored
by Git. Anaconda's base environment was not modified.

## Python environment setup

From the repository root, recreate the environment with:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

These commands use the virtual environment directly, so activation is optional.
Python 3.13.9 was used for this installation. Package installation initially
requires network access.

## Ollama setup steps

1. Review hardware requirements and install
   Ollama from its [official website](https://ollama.com/).
2. The agreed command for running the selected model is:

   ```sh
   ollama run qwen2.5-coder:3b
   ```

3. Start AlgoX using the command below. Its status page checks whether Ollama
   responds and the model is installed. This does not verify generation quality.

The [official API documentation](https://docs.ollama.com/api/introduction) specifies
`http://localhost:11434/api` as the local API base URL. Local model requests do not
require an API key. The initial milestone should verify service availability,
the selected model, and a schema-constrained JSON response.

DeepSeek-Coder is not selected for this MVP. Local inference avoids paid API
calls while using local computing resources.

## Run AlgoX locally

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. Keep the
terminal open; press Ctrl+C to stop. If port 8000 is occupied, choose another
port with `--port` and open that port in your browser.

Use the served page rather than opening `frontend/index.html` directly or using
Live Server. The page calls the same server's `/api/status` endpoint; the Python
backend contacts Ollama at `http://127.0.0.1:11434/api/tags` with a five-second
timeout and without a system proxy. The page checks on load and on "Check again".

The endpoint returns `state`, `model`, and `message`. States are `ready`,
`model_missing`, `unavailable`, `timeout`, and `invalid_response`. These results
are returned as HTTP 200 so clients can inspect the connection state separately
from failures of the AlgoX server itself. `ready` means the service responded
and lists the selected model, not that generation was tested.

## Verify the connection handling

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Automated tests cover installed/missing models, malformed responses, HTTP and
connection failures, and timeouts. Live HTTP checks also verified the served
page, CSS, JavaScript, and the actual Ollama status. Headless Chrome checks
verified initial status loading, mouse and Enter-key retries, all connection
states, and recovery from a simulated server error. Desktop (1280px) and mobile
(390px) screenshots were inspected; neither layout overflowed horizontally.
No uncaught JavaScript errors were detected. The real service reported ready.

The page's CSS and JavaScript are local; no CDN is required.

## Bubble Sort website example

Restart the FastAPI server after changing Python code, then refresh the page.
The example appears above connection status, with Python source, sample input
`[5, 2, 8, 1]`, and output `[1, 2, 5, 8]`. Use Copy Python to copy the function,
or Sort my numbers to retry a request. If clipboard access is blocked, the page
selects the code for manual copying. This built-in example works even when
Ollama is unavailable. It now includes deterministic steps and live animation,
but is not model-generated.

## Custom Bubble Sort input

The website accepts 1-20 integers separated by commas or spaces. Choose
Sort my numbers (or press Enter) to submit; Use example restores the default
input and sorts it. Negative numbers and duplicates are supported. Empty
entries, decimals, invalid text, and integers outside the browser's exact integer
range (plus/minus 9,007,199,254,740,991) are rejected before sorting.

`POST /api/examples/bubble-sort` accepts `{"values": [9, 3, 7, 1]}` and returns
the Python source, submitted input, and sorted output. The backend independently
validates input; invalid requests return HTTP 422. The GET endpoint still returns
the default example. This built-in example includes steps and animation without model generation.

## Algorithm page and visualization

Open playground on the home page opens `/algorithms/bubble-sort`. Enter numbers
in the playground and use the visualization block below it to play/pause, move
between snapshots, reset, change speed, or seek to a step. A new submission
replaces the old trace and starts paused at step 1. Editing input pauses playback;
submit it to update the trace. Playback pauses when the browser tab is hidden.

Pink outlines indicate a comparison, yellow bars indicate a swap, and cyan bars
indicate final positions. Negative bars extend below the zero baseline. Longer
lists scroll horizontally. Exact values are also shown as text below the chart.
Reduced-motion preferences disable the swap transition; manual stepping remains
available. The reference algorithm and generated snapshots use the same ascending
Bubble Sort variant with early exit after a pass without swaps.

The API response includes `steps`, each containing `stepIndex`, `action`,
`stateData`, `highlights`, `sortedIndices`, and `explanation`. All playback uses
these local snapshots and makes no model or backend calls for individual frames.
