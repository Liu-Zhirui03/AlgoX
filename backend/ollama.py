"""Read local Ollama availability without loading or generating with a model."""

import json
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, build_opener

from pydantic import BaseModel

MODEL = "qwen2.5-coder:3b"
TAGS_URL = "http://127.0.0.1:11434/api/tags"
TIMEOUT_SECONDS = 5
# Local traffic must not be sent through a system proxy.
_opener = build_opener(ProxyHandler({}))


class ConnectionStatus(BaseModel):
    state: Literal["ready", "model_missing", "unavailable", "timeout", "invalid_response"]
    model: str = MODEL
    message: str


def check_connection() -> ConnectionStatus:
    try:
        with _opener.open(TAGS_URL, timeout=TIMEOUT_SECONDS) as response:
            payload = json.load(response)
    except HTTPError:
        return ConnectionStatus(
            state="unavailable",
            message="Ollama returned an HTTP error. Check the local service and retry.",
        )
    except (TimeoutError, URLError, OSError) as error:
        reason = error.reason if isinstance(error, URLError) else error
        if isinstance(reason, TimeoutError):
            return ConnectionStatus(
                state="timeout", message="Ollama did not respond within 5 seconds. Retry shortly."
            )
        return ConnectionStatus(
            state="unavailable", message="Cannot reach Ollama. Open Ollama on this computer and retry."
        )
    except (ValueError, UnicodeError):
        return ConnectionStatus(
            state="invalid_response", message="Ollama returned an unreadable model list. Check the service and retry."
        )

    models = payload.get("models") if isinstance(payload, dict) else None
    if not isinstance(models, list) or any(
        not isinstance(item, dict) or not isinstance(item.get("name"), str)
        for item in models
    ):
        return ConnectionStatus(
            state="invalid_response", message="Ollama returned an unexpected model list. Check the service and retry."
        )
    if any(item["name"] == MODEL for item in models):
        return ConnectionStatus(
            state="ready", message="Ollama is reachable and the selected model is installed."
        )
    return ConnectionStatus(
        state="model_missing",
        message=f"Ollama is reachable. Install the selected model with: ollama pull {MODEL}",
    )
