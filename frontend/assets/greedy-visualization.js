let algorithmTitle = document.querySelector("[data-algorithm-id]").dataset.algorithmTitle;
const traceCanvas = document.querySelector("#trace-canvas");
const mode = document.querySelector("[data-renderer]").dataset.renderer;
const greedyView = new GreedyCanvas(traceCanvas, mode);
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
  greedyView.render(step);
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
  explanation.textContent = step?.explanation || "Submit your input above to generate a fresh walkthrough.";
  const data = step?.stateData;
  if (!data) currentValues.textContent = "No values loaded";
  else if (mode === "huffman-tree") {
    currentValues.textContent = `Forest roots: ${data.roots.map(index => data.nodes[index].frequency).join(", ")} / Codes: ${Object.entries(data.codes).map(([symbol, code]) => `${symbol}=${code}`).join(", ") || "not assigned yet"} / Weighted cost assigned so far: ${data.weightedCost}`;
  } else if (mode === "activity-timeline") {
    currentValues.textContent = `Finish order: ${data.order.map(index => data.activities[index].name).join(", ")} / Selected: ${data.selected.map(index => data.activities[index].name).join(", ") || "none"} / Last finish: ${data.lastFinish ?? "none"}`;
  } else {
    currentValues.textContent = `Remaining capacity: ${data.remaining} / Used weight: ${data.totalWeight} / Value: ${Number(data.totalValue.toFixed(6))} / Portions: ${data.items.map((item, index) => `${item.name}=${Number((data.fractions[index] * 100).toFixed(4))}%`).join(", ")}`;
  }
  document.querySelector("#trace-comparisons").textContent = state.steps.slice(0, state.index + 1).filter(item => item.action === traceCanvas.dataset.inspectAction).length;
  document.querySelector("#trace-swaps").textContent = state.steps.slice(0, state.index + 1).filter(item => item.action === traceCanvas.dataset.metricAction).length;
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
