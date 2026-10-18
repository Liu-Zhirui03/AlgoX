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
const targetInput = document.querySelector("#target-input");
const bucketInput = document.querySelector("#bucket-input");
const defaultTarget = targetInput.value;
const defaultBuckets = bucketInput?.value;
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

function integerField(input, name) {
  const text = input.value.trim();
  if (!/^[+-]?\d+$/.test(text) || !Number.isSafeInteger(Number(text))) {
    const error = new Error(`${name} must be a whole number within the safe integer range.`);
    error.field = input;
    throw error;
  }
  return Number(text);
}

function parseRequest() {
  const values = parseNumbers();
  if (algorithmId === "binary-search" && values.some((value, index) => index && values[index - 1] > value)) {
    throw new Error("Binary Search needs numbers in ascending order. Please arrange your input first.");
  }
  const payload = {values, target: integerField(targetInput, "Target")};
  if (bucketInput) {
    payload.bucketCount = integerField(bucketInput, "Bucket count");
    if (payload.bucketCount < 3 || payload.bucketCount > 16) {
      const error = new Error("Choose a bucket count from 3 to 16.");
      error.field = bucketInput;
      throw error;
    }
  }
  return payload;
}

async function loadSearch(payload) {
  document.dispatchEvent(new Event("algox:trace-start"));
  sortButton.disabled = useExample.disabled = copyExample.disabled = true;
  examplePanel.setAttribute("aria-busy", "true");
  exampleMessage.textContent = "Searching your numbers...";
  exampleInput.textContent = JSON.stringify(payload);
  exampleOutput.textContent = "Searching...";
  try {
    const response = await fetch(`/api/algorithms/${encodeURIComponent(algorithmId)}`, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload), cache: "no-store", signal: AbortSignal.timeout(10000),
    });
    if (response.status === 422) {
      setInputError("The server rejected this request. Check the numbers, target, and input requirements.");
      throw new Error("Invalid input");
    }
    if (!response.ok) throw new Error("Search request failed");
    const result = await response.json();
    if (result.algorithmId !== algorithmId || result.renderer !== renderer ||
        result.language !== "python" || typeof result.source !== "string" || !result.source.trim() ||
        !Array.isArray(result.steps) || !result.steps.length ||
        typeof result.output?.found !== "boolean" || !Number.isInteger(result.output?.index)) {
      throw new Error("Invalid search response");
    }
    document.dispatchEvent(new CustomEvent("algox:trace", {detail: result.steps}));
    pythonSource = result.source;
    exampleCode.textContent = pythonSource;
    exampleInput.textContent = JSON.stringify(result.input);
    exampleOutput.textContent = result.output.found ? `Found at index ${result.output.index}` : "Not found (index -1)";
    exampleMessage.textContent = result.output.found ? "First matching index in your original input. Replay the search below." : "Target is not present. Replay the search to see why.";
    copyExample.disabled = false;
  } catch {
    pythonSource = "";
    exampleCode.textContent = "Python example could not be loaded.";
    exampleOutput.textContent = "Unavailable";
    exampleMessage.textContent = "Could not search this input. Check the AlgoX server and try again.";
  } finally {
    sortButton.disabled = useExample.disabled = false;
    examplePanel.setAttribute("aria-busy", "false");
  }
}

sortForm.addEventListener("submit", event => {
  event.preventDefault();
  if (sortButton.disabled) return;
  setInputError("");
  try { loadSearch(parseRequest()); }
  catch (error) { setInputError(error.message); (error.field || numbersInput).focus(); }
});
for (const input of [numbersInput, targetInput, bucketInput].filter(Boolean)) {
  input.addEventListener("input", () => {
    document.dispatchEvent(new Event("algox:input-edited"));
    setInputError("");
    exampleMessage.textContent = "Input edited. Choose Search my numbers to update the result.";
  });
}
useExample.addEventListener("click", () => {
  numbersInput.value = defaultValues.join(", ");
  targetInput.value = defaultTarget;
  if (bucketInput) bucketInput.value = defaultBuckets;
  setInputError("");
  loadSearch(parseRequest());
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


loadSearch(parseRequest());
