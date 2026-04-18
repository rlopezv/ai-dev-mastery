# Shared configuration and client helpers
# Module: rag
# Doc reference: docs/rag/implementation-reference.md

import logging
import os
import sys

import requests
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------

OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")
GENERATION_MODEL: str = os.getenv("GENERATION_MODEL", "llama3.2")
JUDGE_MODEL: str = os.getenv("JUDGE_MODEL", "llama3.2")
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CONTEXT_WINDOW: int = int(os.getenv("CONTEXT_WINDOW", "8192"))
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "512"))
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Client builders
# ---------------------------------------------------------------------------

def build_client() -> OpenAI:
    """Return an OpenAI client pointed at the local Ollama endpoint."""
    return OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")


def build_chroma_client():
    """Return a ChromaDB PersistentClient at CHROMA_PERSIST_DIR."""
    try:
        import chromadb  # noqa: PLC0415
    except ImportError:
        log.error("chromadb not installed. Run: pip install chromadb>=0.5.0")
        sys.exit(1)
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


# ---------------------------------------------------------------------------
# Embedding helpers
# ---------------------------------------------------------------------------

def embed(client: OpenAI, text: str) -> list[float]:
    """Embed a single text string using EMBED_MODEL."""
    # Concept: single text embedding — produces one dense vector
    response = client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding


def embed_batch(client: OpenAI, texts: list[str],
                batch_size: int = 64) -> list[list[float]]:
    """Embed a list of texts in batches to minimize round-trip overhead."""
    # Concept: batch embedding — amortizes API latency across many inputs
    vectors: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(model=EMBED_MODEL, input=batch)
        # Preserve order — API returns items sorted by index
        batch_vecs = sorted(response.data, key=lambda d: d.index)
        vectors.extend(v.embedding for v in batch_vecs)
    return vectors


# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------

# cl100k_base is the GPT-4 tokenizer family — used as an approximation
# for llama3.2's SentencePiece tokenizer. May overestimate by ~5-10%.
_ENCODER = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Return the approximate token count of a text using cl100k_base."""
    return len(_ENCODER.encode(text))


# ---------------------------------------------------------------------------
# Context assembly
# ---------------------------------------------------------------------------

def assemble_context(chunks: list[dict], query: str,
                     system_prompt: str) -> str:
    """
    Select chunks within the token budget and format the context block.

    Each chunk dict must have a 'text' key.
    Chunks are assumed pre-sorted by relevance (best first).

    Returns the formatted context block string (numbered entries).
    """
    # Concept: token budget allocation — prevents context overflow
    framing_overhead = 100  # tokens for context header and message formatting
    budget = (
        CONTEXT_WINDOW
        - count_tokens(system_prompt)
        - count_tokens(query)
        - MAX_TOKENS          # output reservation
        - framing_overhead
    )

    selected: list[dict] = []
    used_tokens = 0
    for chunk in chunks:
        chunk_tokens = count_tokens(chunk["text"])
        if used_tokens + chunk_tokens <= budget:
            selected.append(chunk)
            used_tokens += chunk_tokens

    lines = [f"[{i + 1}] {c['text']}" for i, c in enumerate(selected)]
    return "\n\n".join(lines)


# ---------------------------------------------------------------------------
# Readiness checks
# ---------------------------------------------------------------------------

def assert_ollama_ready(models: list[str] | None = None) -> None:
    """
    Exit with a clear message if Ollama is not reachable or a required
    model is not available.

    models: list of model name prefixes to check (e.g. ["nomic-embed-text"])
    """
    required = models or [EMBED_MODEL]
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        available = [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        log.error(
            "Ollama is not reachable at %s. Start it with: ollama serve",
            OLLAMA_BASE_URL,
        )
        sys.exit(1)

    for model in required:
        if not any(model in name for name in available):
            log.error(
                "Model '%s' not found in Ollama. Run: ollama pull %s",
                model, model,
            )
            sys.exit(1)
