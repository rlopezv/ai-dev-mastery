---
id: "lab-llamaindex"
title: "LlamaIndex — VectorStoreIndex with ChromaDB, Query Engine, and Retriever"
type: "lab-readme"
step: "frameworks-tools"
path: "labs/frameworks-tools/lab-llamaindex/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "LlamaIndex"
  - "index"
  - "node"
  - "node parser"
  - "query engine"
  - "retriever"

prerequisites:
  - "docs/frameworks-tools/llamaindex.md"
  - "docs/rag/embeddings-and-vector-search.md"

related:
  - "docs/frameworks-tools/architecture.md"
  - "docs/frameworks-tools/implementation-reference.md"

summary: "Implements a LlamaIndex retrieval pipeline that builds a persistent VectorStoreIndex in ChromaDB, reloads it without re-ingestion, and demonstrates query engine and retriever decoupling with configurable top_k."
---

## Overview

This lab builds a LlamaIndex retrieval pipeline in three parts:

**Demo 1 — Index construction and reload.** Loads the shared corpus, splits it into nodes
using `SentenceSplitter`, builds a `VectorStoreIndex` backed by ChromaDB, and times the
operation. On subsequent runs, the index is reloaded from ChromaDB without re-embedding —
the learner observes the build time vs. reload time difference.

**Demo 2 — Query engine with configurable top_k.** Runs the same query with `top_k=1`
and `top_k=5`, printing the retrieved node count, similarity scores, source filenames,
and synthesized response. The learner observes how top_k affects retrieved context and
response quality.

**Demo 3 — Direct retriever.** Retrieves nodes without LLM synthesis, printing node
scores and sources. This demonstrates the index-query separation — the retriever can
be used independently of the synthesizer.

Out of scope: hierarchical node parsing, auto-merging retrieval, LlamaIndex agents,
and reranking postprocessors.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `node` | `main.py:build_index()` — `SentenceSplitter.get_nodes_from_documents()` produces nodes with metadata |
| `node parser` | `main.py:build_index()` — `SentenceSplitter(chunk_size=512, chunk_overlap=64)` |
| `index` | `main.py:build_index()` — `VectorStoreIndex(nodes, storage_context=...)` persisted to ChromaDB |
| `index` (reload) | `main.py:load_index()` — `VectorStoreIndex.from_vector_store(...)` — no re-embedding |
| `query engine` | `main.py:demo_query_engine()` — `index.as_query_engine(similarity_top_k=k)` |
| `retriever` | `main.py:demo_retriever()` — `index.as_retriever(similarity_top_k=3)` decoupled from synthesis |

---

## Setup

```bash
# Start full profile (Ollama + ChromaDB)
docker-compose --profile full up -d

# Pull the model if not already present
ollama pull mistral

# Install dependencies
pip install -r labs/frameworks-tools/requirements.txt

# Copy environment file
cp labs/frameworks-tools/.env.example labs/frameworks-tools/.env
```

**To force a fresh index on the next run:**

```bash
RESET_INDEX=true python main.py
```

**To use OpenAI instead of Ollama:**

```bash
LLM_PROVIDER=openai OPENAI_API_KEY=sk-... python main.py
```

---

## Run

```bash
cd labs/frameworks-tools/lab-llamaindex
python main.py
```

Environment variable overrides:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `ollama` | `ollama` or `openai` |
| `MODEL` | `mistral` | Ollama model (chat + embeddings) |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `CHROMA_HOST` | `localhost` | ChromaDB host |
| `CHROMA_PORT` | `8000` | ChromaDB port |
| `RESET_INDEX` | `false` | Set to `true` to delete and rebuild the index |

---

## Expected Output

**First run (index build):**

```
======== DEMO 1 — Index construction and reload ========
Provider: ollama  |  Model: mistral
ChromaDB: localhost:8000  |  Collection: frameworks-tools-corpus
Chunk size: 512  |  Overlap: 64

Building index from corpus...

Corpus loaded: 3 documents
  • agent-coordination.md
  • llm-api-design.md
  • vector-search.md
Nodes created: 28
  Node sample [agent-coordination.md]: Multi-agent systems decompose a complex task...
  Node sample [llm-api-design.md]: LLM APIs expose a request-response interface...
  Node sample [vector-search.md]: Vector search finds stored items that are semantically...

Index built and persisted to ChromaDB in 12.43s
Collection: 'frameworks-tools-corpus'  |  Vectors stored: 28

======== DEMO 2 — Query engine with configurable top_k ========
Query: How does HNSW enable fast approximate nearest-neighbor search?

--- top_k = 1 ---
Nodes retrieved: 1  |  Time: 3.21s
  1. [vector-search.md]  score=0.891  — Hierarchical Navigable Small World (HNSW) is
     the dominant ANN algorithm in production vector databases...

[Answer (top_k=1)]
HNSW builds a multi-layer navigable graph to enable fast ANN search. Queries traverse
from the top (coarse) layer down, greedy-walking toward the target vector at each level.

--- top_k = 5 ---
Nodes retrieved: 5  |  Time: 3.44s
  1. [vector-search.md]  score=0.891  — Hierarchical Navigable Small World (HNSW)...
  2. [vector-search.md]  score=0.856  — A query traverses the graph top-down: it enters
     at the top layer, greedy-walks toward the query vector...
  3. [vector-search.md]  score=0.812  — HNSW parameters: M — the number of bidirectional
     connections per node...
  4. [vector-search.md]  score=0.743  — IVF partitions the vector space into Voronoi cells
     via k-means clustering...
  5. [llm-api-design.md] score=0.612  — Rate limiting in LLM APIs restricts...

[Answer (top_k=5)]
HNSW enables fast ANN search through a multi-layer navigable graph. The top layer
contains few nodes with long-range connections (highway-like). Each query enters at
the top, greedy-walks toward the target, then descends through layers of increasing
granularity. Parameters M (connections per node) and ef_search (beam width) control
the recall/latency trade-off without rebuilding the index.
```

**Second run (index reload):**

```
Existing index found (28 vectors). Reloading...
Loaded index from ChromaDB in 0.041s (no re-ingestion)
```

---

## What to observe

- **Build time vs. reload time in Demo 1**: the first run embeds 28 nodes and stores them —
  expect 10–20 seconds depending on the model. The second run reloads the persisted index
  in under 100ms. This is the index-query separation in action: embedding cost is paid once.

- **top_k effect in Demo 2**: with `top_k=1`, the response uses a single node and may
  omit HNSW parameters (M, ef_search) covered in other nodes. With `top_k=5`, the response
  incorporates parameter details because more nodes are retrieved. Notice also that node 5
  (from `llm-api-design.md`) appears with a low score — borderline-relevant content
  sometimes enters the context with high top_k values.

- **Source attribution in Demo 2 and 3**: HNSW queries should retrieve exclusively from
  `vector-search.md`; rate limiting queries from `llm-api-design.md`; coordination queries
  from `agent-coordination.md`. Cross-file retrieval (e.g., `llm-api-design.md` appearing
  for an HNSW query) indicates the embedding model is conflating semantically distinct topics.

- **Retriever vs. query engine in Demo 3**: the retriever returns raw nodes with scores
  and no LLM call. Latency is under 1 second. The query engine adds synthesis — an LLM
  call that converts nodes to a coherent answer. Use the retriever when you need nodes for
  downstream processing; use the query engine when you need a natural language response.

---

## Concepts verified

- [ ] `node parser` — observable as "Nodes created: 28" with `SentenceSplitter` splitting 3 corpus files
- [ ] `node` — observable as each node carrying `metadata["source"]` with the originating filename
- [ ] `index` (build) — observable as "Index built and persisted to ChromaDB in N.Ns"
- [ ] `index` (reload) — observable as "Loaded index from ChromaDB in 0.04s (no re-ingestion)" on second run
- [ ] `query engine` — observable as answer quality difference between `top_k=1` and `top_k=5`
- [ ] `retriever` — observable as raw node scores and sources printed without an LLM call in Demo 3

---

## Failure case

Active experiment: modify `main.py` at the marked `# FAILURE CASE` block and re-run.

- **What to change:** change the embedding model in `configure_settings()` to one that
  differs from the model used to build the current index. For example, if the index was
  built with `mistral`, change to `llama3.2` (only if it is available):
  ```python
  Settings.embed_model = OllamaEmbedding(model_name="llama3.2", base_url=OLLAMA_URL)
  ```
  Do NOT set `RESET_INDEX=true` — you want to query the mismatched index.
- **Expected degradation:**
  - Retrieval returns nodes with uniform or near-zero similarity scores (no clear ranking)
  - The top-ranked nodes are from the wrong corpus files (e.g., `llm-api-design.md` for
    an HNSW query)
  - The synthesized response becomes incoherent because the retrieved context is irrelevant

Restore the original embedding model setting after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| `ollama` | Serves the local LLM for synthesis and produces embeddings for indexing and queries |
| `chromadb` | Persists the vector index between lab runs; required for the reload demo |
