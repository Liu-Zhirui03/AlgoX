/* Inputs and result presentation for coding, scheduling, and fractional packing. */
const panel = document.querySelector("[data-algorithm-id]");
const algorithmId = panel.dataset.algorithmId;
const form = document.querySelector("#greedy-form");
const itemsInput = document.querySelector("#items-input");
const capacityInput = document.querySelector("#capacity-input");
const runButton = document.querySelector("#run-button");
const useExample = document.querySelector("#use-example");
const inputError = document.querySelector("#input-error");
const exampleCode = document.querySelector("#example-code");
const exampleMessage = document.querySelector("#example-message");
const copyExample = document.querySelector("#copy-example");
const defaultItems = itemsInput.value;
const defaultCapacity = capacityInput?.value;
let pythonSource = "";
function setError(message) { inputError.textContent = message; inputError.hidden = !message; }
function invalid(message, field = itemsInput) { const error = new Error(message); error.field = field; throw error; }
function integer(text, minimum, name, field = itemsInput) {
  if (!/^[+-]?\d+$/.test(text) || !Number.isSafeInteger(Number(text)) || Number(text) < minimum || Number(text) > 1000000) invalid(`${name} must be an integer from ${minimum} to 1000000.`, field);
  return Number(text);
}
function parseInput() {
  const lines = itemsInput.value.trim() ? itemsInput.value.trim().split(/\r?\n/).filter(line => line.trim()) : [];
  const huffman = algorithmId === "huffman";
  if (!lines.length || lines.length > (huffman ? 10 : 12)) invalid(`Enter 1-${huffman ? 10 : 12} rows.`);
  const names = new Set();
  const rows = lines.map((line, index) => {
    const parts = line.trim().split(/[\s,]+/);
    if (parts.length !== (huffman ? 2 : 3)) invalid(`Line ${index + 1}: use ${huffman ? "symbol frequency" : algorithmId === "activity-selection" ? "name start finish" : "name weight value"}.`);
    const name = parts[0];
    if (!/^[A-Za-z0-9_]{1,8}$/.test(name)) invalid(`Line ${index + 1}: labels need 1-8 letters, digits, or underscores.`);
    if (names.has(name)) invalid("Labels must be unique.");
    names.add(name);
    if (huffman) return {symbol: name, frequency: integer(parts[1], 1, "Frequency")};
    if (algorithmId === "activity-selection") {
      const start = integer(parts[1], 0, "Start"), finish = integer(parts[2], 1, "Finish");
      if (start >= finish) invalid(`Line ${index + 1}: start must be before finish.`);
      return {name, start, finish};
    }
    return {name, weight: integer(parts[1], 1, "Weight"), value: integer(parts[2], 0, "Value")};
  });
  if (huffman) return {symbols: rows};
  if (algorithmId === "activity-selection") return {activities: rows};
  return {items: rows, capacity: integer(capacityInput.value.trim(), 0, "Capacity", capacityInput)};
}
function outputText(output, payload) {
  if (algorithmId === "huffman") return Object.entries(output.codes).map(([symbol, code]) => `${symbol}: ${code}`).join("\n") + `\nWeighted bit cost: ${output.weightedCost}`;
  if (algorithmId === "activity-selection") return `Selected ${output.count} activities: ${output.names.join(", ")}`;
  return `Total value: ${Number(output.totalValue.toFixed(6))} / Used weight: ${output.totalWeight} of ${payload.capacity}\n` + payload.items.map((item, index) => `${item.name}: ${Number((output.fractions[index] * 100).toFixed(4))}%`).join("\n");
}
async function loadGreedy(payload) {
  document.dispatchEvent(new Event("algox:trace-start"));
  runButton.disabled = useExample.disabled = copyExample.disabled = true;
  panel.setAttribute("aria-busy", "true");
  exampleMessage.textContent = "Generating the walkthrough...";
  document.querySelector("#example-input").textContent = itemsInput.value.trim() + (capacityInput ? ` / Capacity: ${payload.capacity}` : "");
  document.querySelector("#example-output").textContent = "Working...";
  try {
    const response = await fetch(`/api/algorithms/${algorithmId}`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload), cache: "no-store", signal: AbortSignal.timeout(10000)});
    if (response.status === 422) { setError("The server rejected this request. Check names, counts, and numeric requirements."); throw new Error("Invalid input"); }
    if (!response.ok) throw new Error("Request failed");
    const result = await response.json();
    if (result.algorithmId !== algorithmId || result.renderer !== panel.dataset.renderer || result.language !== "python" || typeof result.source !== "string" || !result.source.trim() || !Array.isArray(result.steps) || !result.steps.length || !result.output) throw new Error("Invalid result");
    pythonSource = result.source;
    exampleCode.textContent = pythonSource;
    document.querySelector("#example-output").textContent = outputText(result.output, payload);
    document.dispatchEvent(new CustomEvent("algox:trace", {detail: result.steps}));
    exampleMessage.textContent = "Walkthrough ready. Replay each greedy decision below.";
    copyExample.disabled = false;
  } catch {
    pythonSource = ""; exampleCode.textContent = "Python example could not be loaded.";
    document.querySelector("#example-output").textContent = "Unavailable";
    exampleMessage.textContent = "Could not run this input. Check the AlgoX server, then retry.";
  } finally {
    runButton.disabled = useExample.disabled = false;
    panel.setAttribute("aria-busy", "false");
  }
}
function run() { setError(""); try { loadGreedy(parseInput()); } catch (error) { setError(error.message); error.field?.focus(); } }
form.addEventListener("submit", event => { event.preventDefault(); if (!runButton.disabled) run(); });
for (const input of [itemsInput, capacityInput].filter(Boolean)) input.addEventListener("input", () => {
  document.dispatchEvent(new Event("algox:input-edited")); setError("");
  exampleMessage.textContent = "Input edited. Choose Run algorithm to update the walkthrough.";
});
useExample.addEventListener("click", () => { itemsInput.value = defaultItems; if (capacityInput) capacityInput.value = defaultCapacity; run(); });
copyExample.addEventListener("click", async () => {
  if (!pythonSource) return;
  try { await navigator.clipboard.writeText(pythonSource); exampleMessage.textContent = "Python code copied."; }
  catch {
    const range = document.createRange(); range.selectNodeContents(exampleCode);
    const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
    exampleCode.parentElement.focus(); exampleMessage.textContent = "Code selected; press Ctrl+C or Command+C to copy.";
  }
});
run();
