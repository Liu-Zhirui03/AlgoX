# AlgoX project guidance

## Scope

This repository is AlgoX, the Adaptive Generative Algorithm Visualizer.

## Working agreement

- Before starting each task, read `README.md` for the project goal and read
  `AGENTS.md` and `Workflow.md` for working guidance, steps, and milestones.
- Work incrementally with the user. Complete only the requested stage.
- Discuss the next stage before implementing it; do not build the entire app
  from the project concept alone.
- The current stage is the minimal scaffold and connection check. The agreed stack is HTML, CSS,
  JavaScript, and a Python/FastAPI local server, using Canvas, Bubble Sort, and
  Ollama with `qwen2.5-coder:3b`. A status endpoint and page exist; algorithm
  generation through Ollama remains planned. The built-in Bubble Sort page
  includes deterministic step generation, Canvas animation, and playback.
- Do not install dependencies, scaffold a framework, or add application features
  until the user requests that stage.
- Preserve unrelated work and keep changes focused and reviewable.
- Algorithm library cards must omit the feature-summary line
  "Python example / Your input / Live Canvas playback" and similar feature
  lists. Apply this to every existing and future algorithm card.
- Keep the workspace tidy: use clear file names and group files by purpose.
  As implementation grows, separate frontend assets, server/Ollama integration,
  validation, rendering, playback, documentation, and tests where appropriate.
  Keep temporary and generated files out of the project root and exclude them
  from Git when appropriate. Avoid unnecessary folders or splitting tiny files
  without a clear purpose.

## Project intent

Users will select or search for a supported algorithm or data structure and
explore its steps through Canvas or SVG animation.

## Chosen approach: local Ollama integration

- Use locally running Ollama to generate algorithm step data. The recommended
  initial design uses validated JSON and built-in Canvas/SVG renderers.
- Users must be able to run the app locally without a ChatGPT/OpenAI account,
  Codex installation, API key, subscription, or paid service.
- Target offline operation after dependencies and model files are downloaded,
  with Ollama running locally. Verify this during implementation.
- Codex may help develop the project, but it is not a runtime dependency.
- Define supported algorithms and renderer capabilities. Clearly explain when
  an algorithm is unsupported; do not claim to visualize arbitrary algorithms.
- Local-model integration is now in scope, superseding the built-in-only plan.
- Validate model output before playback, including algorithm correctness.
- Include a Python sample for supported algorithms when generation is added.
  Display it as copyable text, without executing it. Validate the code field
  separately from trace data; trace validation does not prove code correctness.
- Hosted AI backends and executable model-generated rendering code remain
  outside the initial integration plan.

## Future implementation principles

- Keep algorithm logic, step data, rendering, and playback controls separate.
- Validate user inputs before generating algorithm steps or rendering them.
- Keep credentials out of Git and browser-delivered source.
- Include keyboard access and readable step explanations.
- Document setup commands once a runnable scaffold exists.
- Use checks appropriate to each change and report verification limits.
