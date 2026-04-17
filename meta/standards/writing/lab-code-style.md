# lab-code-style.md

## Purpose

This document defines code and documentation conventions for all lab implementations
under `labs/`. It complements `writing-style.md`, which governs prose documentation
under `docs/`.

---

## 1. Language

**Programming language:** Python unless the module is explicitly Java-focused
(`ai-java`, Java variants in `real-world-projects`).

**Human language:** All lab content is written in English — without exception.
This applies to README files, inline comments, log messages, corpus files,
and any other learner-facing text produced by or accompanying a lab.

---

## 1a. Abstraction Policy by Level

The allowed abstraction level in lab code is governed by the module's declared level.
Full contract: `meta/system-design/LEVEL_MODE.md`.

| Level | Abstraction policy |
|-------|--------------------|
| `foundational` | Raw APIs only. No framework wrappers. Explicit request/response handling. |
| `intermediate` | Frameworks allowed when they serve the learning objective, but the underlying mechanism must remain visible. |
| `advanced` | Higher-level abstractions allowed. Trade-offs between convenience, control, and transparency must be explicit. |

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

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - <specific modification — e.g. "Remove one example from EXAMPLES">
# - Observe:
#   * <symptom 1 — e.g. "format drift in outputs">
#   * <symptom 2 — e.g. "inconsistent labeling">
```

No business logic in the entry point. Keep `__main__` as an orchestrator only.

The `# FAILURE CASE` block is a comment scaffold placed immediately after the
configuration or core logic block it relates to. It is not executable — it guides
the learner to the exact location for the experiment described in `## Failure case`
of the lab README. Content must be specific to the lab's concept, not generic.

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

## 9. corpus/ convention

Use a `corpus/` directory at the module level when a lab set requires a fixed
knowledge base — a set of documents that the learner reads before running the labs
and that the code loads at runtime.

```text
labs/<module>/corpus/
├── <topic-a>.md
├── <topic-b>.md
└── <topic-c>.md
```

**When to use it.** A `corpus/` is appropriate when:
- Multiple labs in the module operate on the same document set.
- The document content affects observable output (retrieval results, evaluation scores).
- You want the learner to be able to predict results by reading the files first.

**When not to use it.** If only one lab needs external documents and they are
generated programmatically (e.g., synthetic data), keep the data inside that
lab's own directory.

**Loading convention.** Each `shared/config.py` that serves a module with a corpus
should expose a `load_corpus()` function:

```python
import pathlib

CORPUS_DIR = pathlib.Path(__file__).parent.parent / "corpus"

def load_corpus(corpus_dir: pathlib.Path = CORPUS_DIR) -> list[dict]:
    """
    Load all .md files from corpus_dir.
    Returns list of dicts with 'source' (filename) and 'text' (content) keys.
    """
    docs = []
    for path in sorted(corpus_dir.glob("*.md")):
        docs.append({"source": path.name, "text": path.read_text(encoding="utf-8")})
    return docs
```

**Labs README requirement.** Every module with a `corpus/` must include a
"Read the corpus before running the labs" section in `labs/<module>/README.md`
that lists the files and explains why reading them first matters.

**Content rules:**

Corpus files are independent of `docs/`. They are not summaries or mirrors of doc topics —
they are a shared technical knowledge base for the labs to operate on. Depth is greater
than in the docs: the learner already knows the domain and should be able to predict
retrieval results by reading the files.

- Files are plain Markdown. No frontmatter.
- Use `#` for the document title and `##` for major sub-concepts. Structure follows content — no rigid scaffold.
- Include formulas, algorithm descriptions, complexity bounds, and exact technical terms where relevant. Do not simplify for accessibility.
- Each file covers a coherent topic or area. It does not need to correspond 1:1 to a `docs/` topic and may span multiple related sub-concepts.
- Corpus files are not cross-referenced from `docs/` and are not part of the module learning sequence — they exist to make lab outputs observable and predictable.

---

## 10. What to Avoid

| Anti-pattern | Why |
|--------------|-----|
| Hardcoded URLs or ports | Breaks reproducibility across environments |
| Logic in `__main__` | Untestable and hard to follow |
| Silent failures | Reader cannot tell if the lab worked |
| Overly complex labs | One concept per lab — complexity belongs in integration labs |
| Missing doc reference comment | Breaks the docs↔labs connection |
