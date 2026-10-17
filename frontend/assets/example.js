const examplePanel = document.querySelector("[data-algorithm-id]");
const exampleCode = document.querySelector("#example-code");
const exampleInput = document.querySelector("#example-input");
const exampleOutput = document.querySelector("#example-output");
const exampleMessage = document.querySelector("#example-message");
const copyExample = document.querySelector("#copy-example");
const sortForm = document.querySelector("#sort-form");
const numbersInput = document.querySelector("#numbers-input");
const inputError = document.querySelector("#input-error");
const sortButton = document.querySelector("#sort-button");
const useExample = document.querySelector("#use-example");
const algorithmId = examplePanel.dataset.algorithmId;
const renderer = examplePanel.dataset.renderer;
const defaultValues = parseNumbers();
let pythonSource = "";

function setInputError(message) {
  inputError.textContent = message;
  inputError.hidden = !message;
  numbersInput.setAttribute("aria-invalid", String(Boolean(message)));
}

function parseNumbers() {
  const text = numbersInput.value.trim();
  if (!text) throw new Error("Enter at least one integer.");
  const parts = text.includes(",") ? text.split(",").map(part => part.trim()) : text.split(/\s+/);
  if (parts.length > 20) throw new Error("Enter no more than 20 integers.");
  if (parts.some(part => !/^[+-]?\d+$/.test(part))) {
    throw new Error("Use whole numbers separated by commas or spaces, with no empty entries.");
  }
  const values = parts.map(Number);
  if (values.some(value => !Number.isSafeInteger(value))) {
    throw new Error("One of those numbers is too large. Please use smaller integers.");
  }
  return values;
}

async function loadExample(values) {
  document.dispatchEvent(new Event("algox:trace-start"));
  sortButton.disabled = true;
  useExample.disabled = true;
  copyExample.disabled = true;
  examplePanel.setAttribute("aria-busy", "true");
  exampleMessage.textContent = "Sorting your numbers...";
  exampleInput.textContent = JSON.stringify(values);
  exampleOutput.textContent = "Sorting...";
  try {
    const response = await fetch(`/api/algorithms/${encodeURIComponent(algorithmId)}`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({values}),
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
    if (response.status === 422) {
      setInputError("The server could not accept these numbers. Enter 1-20 integers and try again.");
      throw new Error("Invalid input");
    }
    if (!response.ok) throw new Error("Example request failed");
    const example = await response.json();
    if (example.algorithmId !== algorithmId || example.renderer !== renderer ||
        example.language !== "python" || typeof example.source !== "string" ||
        !example.source.trim() || !Array.isArray(example.input) || !Array.isArray(example.output) ||
        !Array.isArray(example.steps) || !example.steps.length) {
      throw new Error("Invalid example response");
    }
    document.dispatchEvent(new CustomEvent("algox:trace", {detail: example.steps}));
    pythonSource = example.source;
    exampleCode.textContent = pythonSource;
    exampleInput.textContent = JSON.stringify(example.input);
    exampleOutput.textContent = JSON.stringify(example.output);
    exampleMessage.textContent = "Sorted in ascending order. Your original list is preserved.";
    copyExample.disabled = false;
  } catch {
    pythonSource = "";
    exampleCode.textContent = "Python example could not be loaded.";
    exampleOutput.textContent = "Unavailable";
    exampleMessage.textContent = "Could not sort this input. Check the AlgoX server, then choose Sort my numbers to retry.";
  } finally {
    sortButton.disabled = false;
    useExample.disabled = false;
    examplePanel.setAttribute("aria-busy", "false");
  }
}

sortForm.addEventListener("submit", event => {
  event.preventDefault();
  if (sortButton.disabled) return;
  setInputError("");
  try {
    const values = parseNumbers();
    loadExample(values);
  } catch (error) {
    setInputError(error.message);
    numbersInput.focus();
  }
});

numbersInput.addEventListener("input", () => {
  document.dispatchEvent(new Event("algox:input-edited"));
  setInputError("");
  exampleMessage.textContent = "Input edited. Choose Sort my numbers to update the result.";
});

useExample.addEventListener("click", () => {
  numbersInput.value = defaultValues.join(", ");
  setInputError("");
  loadExample(defaultValues);
});

copyExample.addEventListener("click", async () => {
  if (!pythonSource) return;
  try {
    await navigator.clipboard.writeText(pythonSource);
    exampleMessage.textContent = "Python code copied.";
  } catch {
    const range = document.createRange();
    range.selectNodeContents(exampleCode);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    exampleCode.parentElement.focus();
    exampleMessage.textContent = "Automatic copying is unavailable. Code selected; press Ctrl+C or Command+C to copy.";
  }
});

loadExample(defaultValues);
