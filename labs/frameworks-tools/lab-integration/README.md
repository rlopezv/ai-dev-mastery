---
id: "lab-integration"
title: "Frameworks Integration — LangChain + LlamaIndex with Session Memory"
type: "lab-readme"
step: "frameworks-tools"
path: "labs/frameworks-tools/lab-integration/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "pipeline composition"
  - "LangChain"
  - "LlamaIndex"
  - "LangChain memory"
  - "index"
  - "retriever"

prerequisites:
  - "labs/frameworks-tools/lab-langchain/README.md"
  - "labs/frameworks-tools/lab-llamaindex/README.md"

related:
  - "docs/frameworks-tools/architecture.md"
  - "docs/frameworks-tools/implementation-reference.md"

summary: "Connects a LlamaIndex VectorStoreIndex retriever to a LangChain LCEL chain with session memory, demonstrating cross-framework pipeline composition over a shared ChromaDB corpus."
---

## Overview

This lab composes two frameworks into a single retrieval pipeline:

- **LlamaIndex** provides the retrieval layer: builds (or reloads) a `VectorStoreIndex`
  backed by ChromaDB and exposes a `Retriever` that returns nodes with source metadata.
- **LangChain** provides the orchestration layer: wraps the LlamaIndex retriever in an
  LCEL chain and adds `RunnableWithMessageHistory` for session memory.

**Demo 1 — Integrated pipeline.** Issues three queries against the shared corpus. The
LlamaIndex retriever surfaces nodes; LangChain formats them into a prompt and generates
an answer that cites source files.

**Demo 2 — Memory pipeline.** Adds session memory to the integrated pipeline. Two turns
with the same `session_id` demonstrate that the second question — "What parameters control
its performance?" — is answered correctly despite lacking a subject, because the first turn
established "HNSW" as the topic.

Out of scope: tool-calling, agentic loops, and production streaming.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `pipeline composition` | `main.py` — LlamaIndex retriever wrapped in a LangChain LCEL chain via `make_langchain_retriever()` |
| `index` | `main.py:get_llamaindex_retriever()` — `VectorStoreIndex` built or reloaded from ChromaDB |
| `retriever` | `main.py:make_langchain_retriever()` — LlamaIndex nodes converted to LangChain `Document` objects |
| `chain` | `main.py:demo_integrated_pipeline()` — LCEL chain: `{context, question} \| prompt \| llm \| parser` |
| `LangChain memory` | `main.py:demo_memory_pipeline()` — `RunnableWithMessageHistory` wrapping the retrieval chain |

---

## Setup

```bash
# Start full profile (Ollama + ChromaDB)
docker-compose --profile full up -d

# Pull the model
ollama pull mistral

# Install dependencies
pip install -r labs/frameworks-tools/requirements.txt

# Copy environment file
cp labs/frameworks-tools/.env.example labs/frameworks-tools/.env
```

If `lab-llamaindex` was already run, the integration lab creates its own separate
collection (`frameworks-tools-integration`) and does not share the llamaindex lab's index.

---

## Run

```bash
cd labs/frameworks-tools/lab-integration
python main.py
```

Environment variable overrides:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `ollama` | `ollama` or `openai` |
| `MODEL` | `mistral` | Ollama model |
| `CHROMA_HOST` | `localhost` | ChromaDB host |
| `CHROMA_PORT` | `8000` | ChromaDB port |
| `RESET_INDEX` | `false` | Set to `true` to rebuild the index |

---

## Expected Output

```
=================== SETUP ===================
Provider: ollama  |  Model: mistral
ChromaDB: localhost:8000  |  top_k: 4
Building LlamaIndex index from corpus...
  Nodes created: 28
  Index persisted to collection 'frameworks-tools-integration'

======= DEMO 1 — LangChain chain + LlamaIndex retriever =======

--- Query: How does HNSW achieve fast approximate nearest-nei... ---

Sources retrieved:
  1. vector-search.md — Hierarchical Navigable Small World (HNSW) is the dominant
     ANN algorithm in production vector databases...
  2. vector-search.md — A query traverses the graph top-down: it enters at the top
     layer, greedy-walks toward the query vector...
  3. vector-search.md — HNSW parameters: M — the number of bidirectional connections...
  4. vector-search.md — IVF partitions the vector space into Voronoi cells...

[Answer]
According to vector-search.md, HNSW builds a multi-layer navigable graph. The top
layer has few nodes with long-range connections; each lower layer has more nodes with
shorter connections. A query greedy-walks from the top layer toward the target vector,
descending through layers until the bottom. Parameters M and ef_search (from
vector-search.md) control the recall/latency trade-off.

...

======= DEMO 2 — Integrated pipeline with session memory =======

--- Turn 1 | session_id=integration-session-001 ---
User: What is the HNSW algorithm used for?
Assistant: According to vector-search.md, HNSW is used for approximate
nearest-neighbor search in vector databases. It builds a multi-layer graph that
enables sub-linear query time compared to exhaustive search.

--- Turn 2 | session_id=integration-session-001 ---
User: What parameters control its performance?
Assistant: Based on vector-search.md and the prior context about HNSW, the key
parameters are M (connections per node, controls memory and recall) and ef_search
(beam width during traversal, controls latency vs. recall trade-off).
```

---

## What to observe

- **Cross-framework interface in Demo 1**: `make_langchain_retriever()` converts LlamaIndex
  `NodeWithScore` objects into LangChain `Document` objects, transferring metadata (source
  filename, similarity score). The LangChain chain receives standard `Document` objects and
  is unaware it is using a LlamaIndex retriever.

- **Source citation in Demo 1**: the system prompt instructs the model to state which
  document each claim comes from. Responses should cite `vector-search.md`, `llm-api-design.md`,
  or `agent-coordination.md` explicitly. If citations are absent, the model is answering from
  training knowledge rather than retrieved context.

- **Memory continuity in Demo 2**: Turn 2 ("What parameters control its performance?") has
  no explicit subject. The correct answer requires knowing Turn 1 established HNSW as the
  topic. The response should reference M and ef_search — parameters covered in
  `vector-search.md` — and connect them to HNSW from the prior turn.

- **Index reuse**: run the lab twice and observe that the second run prints "Reloading
  LlamaIndex index..." with a sub-100ms load time, not "Building LlamaIndex index from corpus...".
  The integration collection is separate from the `lab-llamaindex` collection.

---

## Concepts verified

- [ ] `pipeline composition` — observable as LlamaIndex nodes flowing into a LangChain prompt without adapter frameworks
- [ ] `index` — observable as "Reloading LlamaIndex index..." on the second run (no re-embedding)
- [ ] `retriever` — observable as source filenames printed for every query from LlamaIndex node metadata
- [ ] `chain` — observable as a single `retrieval_chain.invoke(query)` driving retrieval + synthesis
- [ ] `LangChain memory` — observable as Turn 2 correctly resolving "its" as HNSW from Turn 1 context

---

## Failure case

Active experiment: modify `main.py` at the marked `# FAILURE CASE` block and re-run.

- **What to change:** change `INTEGRATION_COLLECTION = "frameworks-tools-integration"` to
  `"test-collection-empty"` at the top of the file, and ensure `RESET_INDEX=false` (default).
- **Expected degradation:**
  - A new empty collection is found; `VectorStoreIndex.from_vector_store` returns an empty index
  - All queries retrieve 0 nodes; `lc_retriever(query)` returns an empty list
  - The prompt's `{context}` slot is empty
  - Responses answer from model training knowledge only — no source citations appear
  - This demonstrates that collection name and embedding model must be consistent between
    index build and query

Restore `INTEGRATION_COLLECTION = "frameworks-tools-integration"` after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| `ollama` | Serves the local LLM for synthesis and generates embeddings for LlamaIndex |
| `chromadb` | Persists the LlamaIndex vector index between runs |
