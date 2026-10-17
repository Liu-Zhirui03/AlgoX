const button = document.querySelector("#check-button");
const heading = document.querySelector("#connection-title");
const message = document.querySelector("#status-message");
const card = document.querySelector("#connection-panel");
const labels = {
  ready: "Ollama is connected",
  model_missing: "Selected model is missing",
  unavailable: "Ollama is unavailable",
  timeout: "Connection timed out",
  invalid_response: "Unexpected Ollama response",
};

async function checkConnection() {
  button.disabled = true;
  button.textContent = "Checking…";
  card.setAttribute("aria-busy", "true");
  heading.dataset.state = "checking";
  heading.textContent = "Checking connection…";
  message.hidden = false;
  message.textContent = "Contacting your local Ollama service.";

  try {
    const response = await fetch("/api/status", {
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
    if (!response.ok) throw new Error("Status request failed");
    const status = await response.json();
    if (!Object.hasOwn(labels, status.state) || typeof status.message !== "string") {
      throw new Error("Invalid status response");
    }
    heading.dataset.state = status.state;
    heading.textContent = labels[status.state];
    message.hidden = status.state === "ready";
    message.textContent = status.state === "ready" ? "" : status.message;
  } catch {
    message.hidden = false;
    heading.dataset.state = "error";
    heading.textContent = "Cannot check the connection";
    message.textContent = "The AlgoX server did not return a status. Check that it is running, then retry.";
  } finally {
    button.disabled = false;
    button.textContent = "Check again";
    card.setAttribute("aria-busy", "false");
  }
}

button.addEventListener("click", checkConnection);
checkConnection();
