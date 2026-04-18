# Shared configuration and client helpers
# Module: prompt-engineering
# Doc reference: docs/prompt-engineering/implementation-reference.md

import logging
import os
import sys

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "600"))

log = logging.getLogger(__name__)


def build_client() -> OpenAI:
    """Return an OpenAI client pointed at the local Ollama endpoint."""
    return OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")


def assert_ollama_ready() -> None:
    """Exit with a clear message if Ollama is not reachable or model is missing."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        available = [m["name"] for m in resp.json().get("models", [])]
        if not any(OLLAMA_MODEL in name for name in available):
            log.error("Model '%s' not found. Run: ollama pull %s", OLLAMA_MODEL, OLLAMA_MODEL)
            sys.exit(1)
    except Exception:
        log.error("Ollama is not reachable at %s. Start it with: ollama serve", OLLAMA_BASE_URL)
        sys.exit(1)


def complete(client: OpenAI, messages: list[dict], temperature: float = 0.1) -> str:
    """Send a chat completion request and return the response text."""
    response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=temperature,
    )
    return response.choices[0].message.content
