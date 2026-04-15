# Shared Ollama API client
# Module: llm-fundamentals
# Doc reference: docs/llm-fundamentals/llm-architecture.md

import logging
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("MODEL", "llama3.2")

log = logging.getLogger(__name__)


def check_connection() -> bool:
    """Return True if Ollama is reachable at OLLAMA_URL."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def list_models() -> list:
    """Return the list of model metadata dicts available in Ollama."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        response.raise_for_status()
        return response.json().get("models", [])
    except requests.ConnectionError as e:
        log.error("Could not reach Ollama at %s: %s", OLLAMA_URL, e)
        raise


def assert_ready(model: str = MODEL) -> None:
    """Exit with a clear message if Ollama is unreachable or model is missing."""
    if not check_connection():
        print(f"ERROR: Ollama is not reachable at {OLLAMA_URL}.")
        print("       Start it with: ollama serve")
        sys.exit(1)

    available = [m["name"] for m in list_models()]
    if not any(model in name for name in available):
        print(f"ERROR: Model '{model}' not found in Ollama.")
        print(f"       Download it with: ollama pull {model}")
        print(f"       Available models: {available}")
        sys.exit(1)


def generate(
    prompt: str,
    model: str = MODEL,
    temperature: float = 0.8,
    top_k: int = 40,
    top_p: float = 0.9,
    num_predict: int = 256,
    stop: list = None,
) -> dict:
    """
    Send a completion request to Ollama and return the full response dict.

    Concept: wraps POST /api/generate — the entry point to the inference pipeline.
    Returns prompt_eval_count (input tokens) and eval_count (output tokens)
    alongside the generated text.
    """
    options = {
        "temperature": temperature,
        "top_k": top_k,
        "top_p": top_p,
        "num_predict": num_predict,
    }
    if stop:
        options["stop"] = stop

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": options,
    }

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError as e:
        log.error("Could not reach Ollama at %s: %s", OLLAMA_URL, e)
        raise
