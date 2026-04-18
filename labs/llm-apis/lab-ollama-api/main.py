# Lab: lab-ollama-api
# Module: llm-apis
# Doc reference: docs/llm-apis/ollama-api.md

import logging
import os
import sys

import requests
from openai import OpenAI

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from config import MAX_TOKENS, OLLAMA_BASE_URL, OLLAMA_MODEL

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def assert_ollama_ready() -> None:
    """Exit with a clear message if Ollama is not reachable or model is missing."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
    except (requests.ConnectionError, requests.HTTPError):
        log.error("Ollama is not reachable at %s.", OLLAMA_BASE_URL)
        log.error("Start it with: ollama serve")
        sys.exit(1)

    available = [m["name"] for m in resp.json().get("models", [])]
    if not any(OLLAMA_MODEL in name for name in available):
        log.error("Model '%s' not found. Run: ollama pull %s", OLLAMA_MODEL, OLLAMA_MODEL)
        log.error("Available models: %s", available)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Observation 1 — OpenAI-compatible call via SDK
# ---------------------------------------------------------------------------

def observe_openai_compatible_call() -> None:
    """
    Call Ollama using the OpenAI Python SDK with a base_url override.

    Concept: the only change from a real OpenAI call is base_url and api_key.
    Response structure is identical.
    """
    log.info("=== Observation 1: OpenAI-compatible call via SDK ===")

    # Concept: base_url redirects the SDK to the local Ollama endpoint
    client = OpenAI(
        base_url=f"{OLLAMA_BASE_URL}/v1",
        api_key="ollama",  # required by SDK; not validated by Ollama
    )

    response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": "You are a concise technical assistant."},
            {"role": "user", "content": "What is a context window in one sentence?"},
        ],
        max_tokens=MAX_TOKENS,
    )

    log.info("Model:    %s", response.model)
    log.info("Response: %s", response.choices[0].message.content)
    log.info(
        "Usage:    prompt=%d  completion=%d",
        response.usage.prompt_tokens,
        response.usage.completion_tokens,
    )


# ---------------------------------------------------------------------------
# Observation 2 — native model listing
# ---------------------------------------------------------------------------

def observe_model_list() -> None:
    """
    Call the native Ollama /api/tags endpoint to list downloaded models.

    Concept: model management operations are only available via the native
    Ollama API, not through the OpenAI-compatible interface.
    """
    log.info("\n=== Observation 2: Native model listing (/api/tags) ===")

    resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
    resp.raise_for_status()
    models = resp.json().get("models", [])

    log.info("Downloaded models (%d):", len(models))
    for m in models:
        size_mb = m.get("size", 0) // (1024 * 1024)
        log.info("  %-40s  %d MB", m["name"], size_mb)


# ---------------------------------------------------------------------------
# Observation 3 — model metadata inspection
# ---------------------------------------------------------------------------

def observe_model_metadata() -> None:
    """
    Call /api/show to inspect the active model's parameter count and family.

    Concept: Ollama exposes model metadata that has no equivalent in the
    OpenAI-compatible interface — it is only accessible via native endpoints.
    """
    log.info("\n=== Observation 3: Model metadata (/api/show) ===")

    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/show",
        json={"name": OLLAMA_MODEL},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    details = data.get("details", {})
    log.info("Model family:    %s", details.get("family", "unknown"))
    log.info("Parameter size:  %s", details.get("parameter_size", "unknown"))
    log.info("Quantization:    %s", details.get("quantization_level", "unknown"))
    log.info("Format:          %s", details.get("format", "unknown"))


# ---------------------------------------------------------------------------
# Observation 4 — native /api/chat vs OpenAI-compatible
# ---------------------------------------------------------------------------

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In observe_native_chat_format(), replace:
#     data["message"]["content"]
#   with:
#     data["choices"][0]["message"]["content"]
# - Observe:
#   * KeyError: 'choices' — native format has no choices wrapper
#   * code written for the OpenAI-compatible path fails on native responses

def observe_native_chat_format() -> None:
    """
    Call /api/chat directly and compare the response shape to the OpenAI schema.

    Concept: the native Ollama format uses message.content directly on the
    response object, whereas the OpenAI-compatible format wraps it in choices[].
    """
    log.info("\n=== Observation 4: Native /api/chat response shape ===")

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": "What is temperature in LLMs?"}],
        "stream": False,
    }

    resp = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # Concept: native format — response text is at data["message"]["content"]
    text = data["message"]["content"]
    log.info("Native path:    data['message']['content']")
    log.info("OpenAI path:    response.choices[0].message.content")
    log.info("Response text:  %s", text[:200])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready()
    observe_openai_compatible_call()
    observe_model_list()
    observe_model_metadata()
    observe_native_chat_format()
    log.info("\nDone. Review the observations against docs/llm-apis/ollama-api.md.")
