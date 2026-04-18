# Shared configuration for memory-context labs
# Doc reference: docs/memory-context/implementation-reference.md

import os
import httpx
import tiktoken
from openai import OpenAI

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------

MODEL = os.getenv("MODEL", "mistral")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# ---------------------------------------------------------------------------
# Token budget configuration
# ---------------------------------------------------------------------------

# Concept: token budget — available tokens for history after fixed reservations
CONTEXT_WINDOW = int(os.getenv("CONTEXT_WINDOW", "8192"))
OUTPUT_RESERVATION = 512     # reserved for model output
SAFETY_MARGIN = 400          # absorbs tiktoken approximation error (~5% of 8k window)
SYSTEM_PROMPT_TOKENS = 60    # approximate for a minimal one-line system prompt
HISTORY_BUDGET = CONTEXT_WINDOW - SYSTEM_PROMPT_TOKENS - OUTPUT_RESERVATION - SAFETY_MARGIN

# Trigger compression at 80% of budget before the ceiling is reached
COMPRESSION_THRESHOLD = int(HISTORY_BUDGET * 0.80)

# ---------------------------------------------------------------------------
# ChromaDB path (used by labs that require persistent storage)
# ---------------------------------------------------------------------------

import pathlib
CHROMA_PATH = str(pathlib.Path(__file__).parent.parent / ".chroma")

# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------

# cl100k_base is compatible with Mistral and most current Ollama-served models
_encoder = tiktoken.get_encoding("cl100k_base")


def count_tokens(messages: list[dict]) -> int:
    """
    Count tokens in a message list.

    Concept: token counting — each message carries 4 tokens of framing overhead
    (role marker + separators); the reply itself adds 2 priming tokens.
    Approximation error vs Ollama models: ±5%. Covered by SAFETY_MARGIN.
    """
    total = 0
    for msg in messages:
        total += 4  # role + framing overhead per message
        total += len(_encoder.encode(msg["content"]))
    return total + 2  # reply priming tokens


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------

def build_client() -> OpenAI:
    """Build an OpenAI-compatible client pointing at Ollama."""
    return OpenAI(base_url=f"{OLLAMA_URL}/v1", api_key="ollama")


def embed(client: OpenAI, text: str) -> list[float]:
    """Embed a single text using the configured embedding model."""
    response = client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding


# ---------------------------------------------------------------------------
# Readiness check
# ---------------------------------------------------------------------------

def assert_ollama_ready(models: list[str] | None = None) -> None:
    """
    Verify that Ollama is reachable and that required models are available.
    Raises RuntimeError with a clear message if either check fails.
    """
    try:
        r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        r.raise_for_status()
    except Exception as e:
        raise RuntimeError(
            f"Ollama not reachable at {OLLAMA_URL}: {e}\n"
            f"Start it with: docker-compose --profile light up -d"
        ) from e

    if models:
        available = {m["name"].split(":")[0] for m in r.json().get("models", [])}
        for model in models:
            if model not in available:
                raise RuntimeError(
                    f"Model '{model}' not found in Ollama.\n"
                    f"Pull it with: ollama pull {model}"
                )
