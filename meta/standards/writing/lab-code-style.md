# lab-code-style.md

## Purpose

This document defines code and documentation conventions for all lab implementations
under `labs/`. It complements `writing-style.md`, which governs prose documentation
under `docs/`.

---

## 1. Language

Python unless the module is explicitly Java-focused (`ai-java`, Java variants
in `real-world-projects`).

---

## 2. main.py Structure

Every lab entry point follows this order:

```python
# Lab: <lab-name>
# Module: <module-name>
# Doc reference: docs/<module-name>/<topic>.md

# 1. Imports
# 2. Configuration (constants, env vars)
# 3. Core logic (functions or classes)
# 4. Entry point (if __name__ == "__main__")
```

No business logic in the entry point. Keep `__main__` as an orchestrator only.

---

## 3. Configuration

Load configuration from environment variables. Never hardcode URLs, ports, or API keys.

```python
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("MODEL", "mistral")
```

Use `.env.example` to document all required variables.

---

## 4. Comments

Two types of comments are expected:

**Doc reference** — at the top of the file, linking to the concept being implemented:
```python
# Doc reference: docs/rag/embeddings-and-vector-search.md
```

**Concept marker** — inline, at the point where a key concept from the doc is applied:
```python
# Concept: cosine similarity used here to rank retrieved chunks
results = collection.query(query_embeddings=[embedding], n_results=5)
```

No commented-out code. No TODO comments in published labs.

---

## 5. Observability

Every lab must produce visible output that confirms correct behavior.
Use `print` for simple labs, `logging` for labs with multiple steps or external calls.

```python
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

log.info("Embedding generated: shape=%s", embedding.shape)
```

The output must confirm that the concept being demonstrated is working,
not just that the script ran.

---

## 6. Error Handling

Handle errors at the boundary with external services (Ollama, ChromaDB, APIs).
Do not wrap internal logic in broad try/except.

```python
try:
    response = client.chat(model=MODEL, messages=messages)
except ConnectionError as e:
    log.error("Could not reach Ollama at %s: %s", OLLAMA_URL, e)
    raise
```

---

## 7. requests.http

For FastAPI labs only. One file per lab, named `requests.http`.

```http
### Health check
GET http://localhost:8000/health

### <Main endpoint description>
POST http://localhost:8000/<endpoint>
Content-Type: application/json

{
  "<field>": "<value>"
}
```

Rules:
- Every endpoint exposed by the lab must have at least one request example
- Include a health check as the first request
- Use descriptive section comments (`###`)
- No auth tokens or secrets in the file — use variables if needed

---

## 8. shared/

Code in `shared/` must be genuinely reusable across labs in the module.
Do not move code to `shared/` prematurely.

```text
labs/<module>/shared/
├── client.py       ← API client wrappers
├── config.py       ← shared configuration loader
└── utils.py        ← common utilities
```

A lab must be runnable without depending on another lab's files.
Only `shared/` is a valid cross-lab dependency.

---

## 9. What to Avoid

| Anti-pattern | Why |
|--------------|-----|
| Hardcoded URLs or ports | Breaks reproducibility across environments |
| Logic in `__main__` | Untestable and hard to follow |
| Silent failures | Reader cannot tell if the lab worked |
| Overly complex labs | One concept per lab — complexity belongs in integration labs |
| Missing doc reference comment | Breaks the docs↔labs connection |
