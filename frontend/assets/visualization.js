const algorithmTitle = document.querySelector("[data-algorithm-id]").dataset.algorithmTitle;
const traceCanvas = document.querySelector("#trace-canvas");
const renderMode = document.querySelector("[data-algorithm-id]").dataset.renderer;
const bars = renderMode === "array-bars" ? new CanvasBars(traceCanvas) : new SearchCanvas(traceCanvas, renderMode);
const playButton = document.querySelector("#trace-play");
const previousButton = document.querySelector("#trace-previous");
const nextButton = document.querySelector("#trace-next");
const resetButton = document.querySelector("#trace-reset");
const progressSlider = document.querySelector("#trace-progress");
const speedSelect = document.querySelector("#trace-speed");
const explanation = document.querySelector("#trace-explanation");
const currentValues = document.querySelector("#trace-values");
const stepCount = document.querySelector("#trace-count");
const actionLabel = document.querySelector("#trace-action");
const player = new TracePlayer((step, state, animate) => {
  bars.render(step, animate);
  const empty = !step;
  playButton.disabled = empty;
  previousButton.disabled = empty || state.index === 0;
  nextButton.disabled = empty || state.index === state.steps.length - 1;
  resetButton.disabled = empty;
  progressSlider.disabled = empty;
  speedSelect.disabled = empty;
  playButton.textContent = state.playing ? "Pause" : (step?.action === "complete" ? "Replay" : "Play");
  playButton.setAttribute("aria-pressed", String(state.playing));
  progressSlider.max = Math.max(0, state.steps.length - 1);
  progressSlider.value = state.index;
  progressSlider.setAttribute("aria-valuetext", empty ? "No steps" : `Step ${state.index + 1} of ${state.steps.length}`);
  stepCount.textContent = empty ? "No trace loaded" : `Step ${state.index + 1} / ${state.steps.length}`;
  actionLabel.textContent = step ? step.action.replaceAll("_", " ").toUpperCase() : "WAITING";
  explanation.textContent = step?.explanation || "Submit your numbers above to generate a fresh walkthrough.";
  if (!step) currentValues.textContent = "No values loaded";
  else if (Array.isArray(step.stateData)) currentValues.textContent = JSON.stringify(step.stateData);
  else {
    const data = step.stateData;
    const summary = renderMode === "binary-search" ?
      `Active bounds: ${data.low}..${data.high}${data.candidate === null ? "" : ` / Candidate index: ${data.candidate}`}` :
      data.buckets.map((chain, index) => `[${index}] ${chain.length ? chain.map(entry => `${entry.value} (index ${entry.index})`).join(" > ") : "empty"}`).join("; ");
    currentValues.textContent = `Input: ${JSON.stringify(data.values)} / Target: ${data.target} / ${summary}`;
  }
  const bufferText = document.querySelector("#trace-buffer");
  if (bufferText) {
    bufferText.hidden = !Array.isArray(step?.buffer);
    bufferText.textContent = Array.isArray(step?.buffer) ? `Merge buffer: ${JSON.stringify(step.buffer)}` : "";
  }
  document.querySelector("#trace-comparisons").textContent = state.steps.slice(0, state.index + 1).filter(item => item.action === "compare").length;
  document.querySelector("#trace-swaps").textContent = state.steps.slice(0, state.index + 1).filter(item => item.action === (traceCanvas.dataset.metricAction || "swap")).length;
  traceCanvas.setAttribute("aria-label", step ? `${algorithmTitle}: ${step.explanation}` : `${algorithmTitle} visualization awaiting input`);
});
playButton.addEventListener("click", () => player.toggle());
previousButton.addEventListener("click", () => player.seek(player.index - 1));
nextButton.addEventListener("click", () => player.next());
resetButton.addEventListener("click", () => player.seek(0));
progressSlider.addEventListener("input", () => player.seek(Number(progressSlider.value)));
speedSelect.addEventListener("change", () => player.setSpeed(Number(speedSelect.value)));
document.addEventListener("algox:trace-start", () => player.clear());
document.addEventListener("algox:trace", event => player.load(event.detail));
document.addEventListener("algox:input-edited", () => player.pause());
document.addEventListener("visibilitychange", () => { if (document.hidden) player.pause(); });
player.emit();
