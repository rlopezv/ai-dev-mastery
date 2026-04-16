# Shared configuration for ai-agents labs
# Doc reference: docs/ai-agents/implementation-reference.md

import os
import httpx
from openai import OpenAI

# ---------------------------------------------------------------------------
# Model and runtime configuration
# ---------------------------------------------------------------------------

MODEL = os.getenv("MODEL", "mistral")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Concept: stop condition — ceiling enforced by the application, not the model
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------

def build_client() -> OpenAI:
    """Build an OpenAI-compatible client pointing at Ollama."""
    return OpenAI(base_url=f"{OLLAMA_URL}/v1", api_key="ollama")


# ---------------------------------------------------------------------------
# Readiness check
# ---------------------------------------------------------------------------

def assert_ollama_ready(models: list[str] | None = None) -> None:
    """
    Verify that Ollama is reachable and required models are available.
    Raises RuntimeError with a clear message if either check fails.
    """
    try:
        r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        r.raise_for_status()
    except Exception as e:
        raise RuntimeError(
            f"Ollama not reachable at {OLLAMA_URL}: {e}\n"
            "Start it with: docker-compose --profile light up -d"
        ) from e

    if models:
        available = {m["name"].split(":")[0] for m in r.json().get("models", [])}
        for model in models:
            if model not in available:
                raise RuntimeError(
                    f"Model '{model}' not found in Ollama.\n"
                    f"Pull it with: ollama pull {model}"
                )
