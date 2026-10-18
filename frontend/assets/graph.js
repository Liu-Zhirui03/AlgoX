/* Weighted-graph inputs, algorithm selection, results, and code display. */
const graphPanel = document.querySelector("[data-algorithm-id]");
const graphForm = document.querySelector("#graph-form");
const nodesInput = document.querySelector("#nodes-input");
const edgesInput = document.querySelector("#edges-input");
const startInput = document.querySelector("#start-input");
const algorithmSelect = document.querySelector("#algorithm-select");
const runButton = document.querySelector("#run-button");
const useExample = document.querySelector("#use-example");
const inputError = document.querySelector("#input-error");
const exampleCode = document.querySelector("#example-code");
const exampleMessage = document.querySelector("#example-message");
const copyExample = document.querySelector("#copy-example");
const defaultNodes = nodesInput.value;
const defaultEdges = edgesInput.value;
let pythonSource = "";
if (algorithmSelect) algorithmSelect.value = location.pathname.endsWith("/prim") ? "prim" : "kruskal";

function selectedAlgorithm() { return algorithmSelect?.value || "dijkstra"; }
function setError(message) { inputError.textContent = message; inputError.hidden = !message; }
function invalid(message, field) { const error = new Error(message); error.field = field; throw error; }
function configureAlgorithm() {
  const id = selectedAlgorithm();
  graphPanel.dataset.algorithmId = id;
  algorithmTitle = id === "dijkstra" ? "Dijkstra's Algorithm" : id === "prim" ? "Prim's Algorithm" : "Kruskal's Algorithm";
  document.querySelector("#example-title").textContent = algorithmTitle;
  document.querySelector("#code-title").textContent = `${id}.py`;
  document.querySelector("#start-field").hidden = id === "kruskal";
  traceCanvas.dataset.metricAction = id === "dijkstra" ? "relax" : "accept";
}
function parseGraph() {
  const raw = nodesInput.value.trim();
  const nodes = raw.includes(",") ? raw.split(",").map(node => node.trim()) : raw.split(/\s+/);
  if (nodes.length < 1 || nodes.length > 10 || nodes.some(node => !/^[A-Za-z0-9_]{1,8}$/.test(node))) invalid("Enter 1-10 labels using 1-8 letters, digits, or underscores each.", nodesInput);
  if (new Set(nodes).size !== nodes.length) invalid("Node labels must be unique.", nodesInput);
  const lines = edgesInput.value.trim() ? edgesInput.value.trim().split(/\r?\n/) : [];
  if (lines.length > 30) invalid("Enter no more than 30 edges.", edgesInput);
  const seen = new Set();
  const edges = lines.map((line, index) => {
    const parts = line.trim().split(/[\s,]+/);
    if (parts.length !== 3 || !/^[+-]?\d+$/.test(parts[2])) invalid(`Line ${index + 1}: use source target integer-weight, such as A B 4.`, edgesInput);
    const [source, target] = parts;
    const weight = Number(parts[2]);
    if (!nodes.includes(source) || !nodes.includes(target)) invalid(`Line ${index + 1}: both endpoints must be listed nodes.`, edgesInput);
    if (source === target) invalid(`Line ${index + 1}: self-loops are not supported.`, edgesInput);
    if (!Number.isInteger(weight) || Math.abs(weight) > 1000000) invalid(`Line ${index + 1}: weights must be integers between -1000000 and 1000000.`, edgesInput);
    if (selectedAlgorithm() === "dijkstra" && weight < 0) invalid("Dijkstra requires nonnegative weights.", edgesInput);
    const pair = [source, target].sort().join("|");
    if (seen.has(pair)) invalid(`Line ${index + 1}: duplicate undirected edge.`, edgesInput);
    seen.add(pair);
    return {source, target, weight};
  });
  const payload = {nodes, edges};
  if (selectedAlgorithm() !== "kruskal") {
    payload.start = startInput.value.trim();
    if (!nodes.includes(payload.start)) invalid("Choose a start node from your listed nodes.", startInput);
  }
  return payload;
}
async function loadGraph(payload) {
  const id = selectedAlgorithm();
  document.dispatchEvent(new Event("algox:trace-start"));
  runButton.disabled = useExample.disabled = copyExample.disabled = true;
  if (algorithmSelect) algorithmSelect.disabled = true;
  graphPanel.setAttribute("aria-busy", "true");
  exampleMessage.textContent = "Generating the graph walkthrough...";
  document.querySelector("#example-input").textContent = `${payload.nodes.join(", ")} / ${payload.edges.length} edges${payload.start ? " / Start: " + payload.start : ""}`;
  document.querySelector("#example-output").textContent = "Working...";
  try {
    const response = await fetch(`/api/algorithms/${id}`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload), cache: "no-store", signal: AbortSignal.timeout(10000)});
    if (response.status === 422) { setError("The server rejected this graph. Check nodes, edges, weights, and the start node."); throw new Error("Invalid graph"); }
    if (!response.ok) throw new Error("Graph request failed");
    const result = await response.json();
    if (result.algorithmId !== id || result.renderer !== "weighted-graph" || result.language !== "python" || typeof result.source !== "string" || !result.source.trim() || !Array.isArray(result.steps) || !result.steps.length || !result.output) throw new Error("Invalid graph result");
    pythonSource = result.source;
    exampleCode.textContent = pythonSource;
    const output = result.output;
    document.querySelector("#example-output").textContent = id === "dijkstra" ? payload.nodes.map(node =>
      output.distances[node] === null ? `${node}: unreachable` : `${node}: ${output.distances[node]} via ${output.paths[node].join(" > ")}`).join("\n") :
      `${output.connected ? "Minimum spanning tree" : "Minimum spanning forest"} / Total weight: ${output.totalWeight}\nEdges: ${output.edges.map(index => { const edge = payload.edges[index]; return `${edge.source}-${edge.target} (${edge.weight})`; }).join(", ") || "none"}\nComponents: ${output.components.map(group => group.join(", ")).join(" / ")}`;
    document.dispatchEvent(new CustomEvent("algox:trace", {detail: result.steps}));
    exampleMessage.textContent = "Walkthrough ready. Replay each greedy decision below.";
    copyExample.disabled = false;
  } catch {
    pythonSource = "";
    exampleCode.textContent = "Python example could not be loaded.";
    document.querySelector("#example-output").textContent = "Unavailable";
    exampleMessage.textContent = "Could not run this graph. Check the AlgoX server, then retry.";
  } finally {
    runButton.disabled = useExample.disabled = false;
    if (algorithmSelect) algorithmSelect.disabled = false;
    graphPanel.setAttribute("aria-busy", "false");
  }
}
function runGraph() {
  setError("");
  try { loadGraph(parseGraph()); }
  catch (error) { setError(error.message); error.field?.focus(); }
}
graphForm.addEventListener("submit", event => { event.preventDefault(); if (!runButton.disabled) runGraph(); });
for (const input of [nodesInput, edgesInput, startInput]) input.addEventListener("input", () => {
  document.dispatchEvent(new Event("algox:input-edited")); setError("");
  exampleMessage.textContent = "Input edited. Choose Run algorithm to update the walkthrough.";
});
algorithmSelect?.addEventListener("change", () => {
  document.dispatchEvent(new Event("algox:trace-start"));
  configureAlgorithm();
  runGraph();
});
useExample.addEventListener("click", () => { nodesInput.value = defaultNodes; edgesInput.value = defaultEdges; startInput.value = "A"; runGraph(); });
copyExample.addEventListener("click", async () => {
  if (!pythonSource) return;
  try { await navigator.clipboard.writeText(pythonSource); exampleMessage.textContent = "Python code copied."; }
  catch {
    const range = document.createRange(); range.selectNodeContents(exampleCode);
    const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
    exampleCode.parentElement.focus();
    exampleMessage.textContent = "Code selected; press Ctrl+C or Command+C to copy.";
  }
});
configureAlgorithm();
runGraph();
