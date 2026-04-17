# Shared configuration for frameworks-tools labs
# Doc reference: docs/frameworks-tools/implementation-reference.md

import os
import pathlib

# ---------------------------------------------------------------------------
# Environment variables
# ---------------------------------------------------------------------------

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")   # "ollama" | "openai"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("MODEL", "mistral")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
RESET_INDEX = os.getenv("RESET_INDEX", "false").lower() == "true"

CORPUS_DIR = pathlib.Path(__file__).parent.parent / "corpus"


# ---------------------------------------------------------------------------
# LLM factory
# ---------------------------------------------------------------------------

def build_llm(temperature: float = 0):
    """Return a LangChain chat model for the configured provider."""
    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=temperature,
            api_key=OPENAI_API_KEY,
        )
    from langchain_ollama import ChatOllama
    return ChatOllama(
        model=MODEL,
        temperature=temperature,
        base_url=OLLAMA_URL,
    )


def build_embeddings():
    """Return a LangChain embedding model for the configured provider."""
    if LLM_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    from langchain_ollama import OllamaEmbeddings
    return OllamaEmbeddings(model=MODEL, base_url=OLLAMA_URL)


# ---------------------------------------------------------------------------
# Corpus loader
# ---------------------------------------------------------------------------

def load_corpus(corpus_dir: pathlib.Path = CORPUS_DIR) -> list[dict]:
    """
    Load all .md files from corpus_dir.
    Returns list of dicts with 'source' (filename) and 'text' (content) keys.
    """
    docs = []
    for path in sorted(corpus_dir.glob("*.md")):
        docs.append({"source": path.name, "text": path.read_text(encoding="utf-8")})
    return docs


# ---------------------------------------------------------------------------
# Readiness checks
# ---------------------------------------------------------------------------

def assert_ollama_ready(models: list[str] | None = None) -> None:
    """Verify Ollama is reachable and required models are available."""
    import httpx
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


def assert_openai_key() -> None:
    """Raise a clear error if OPENAI_API_KEY is not set."""
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set.\n"
            "Set it in labs/frameworks-tools/.env or export it in your shell."
        )
