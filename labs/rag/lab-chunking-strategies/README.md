---
id: "rag-lab-chunking-strategies"
title: "RAG — Lab: Document Processing and Chunking"
type: "lab-readme"
step: "rag"
path: "labs/rag/lab-chunking-strategies/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "chunking"
  - "chunk-size"
  - "chunk-overlap"
  - "recursive-chunking"
  - "document-loader"

prerequisites:
  - "docs/rag/document-processing-and-chunking.md"
  - "labs/rag/lab-embeddings/README.md"

next:
  - "labs/rag/lab-retrieval-playground/README.md"

related:
  - "docs/rag/embeddings-and-vector-search.md"

implementation_refs:
  - "labs/rag/lab-chunking-strategies"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Compares fixed-size, sentence-boundary, and recursive chunking strategies by indexing the same corpus three times and measuring top-1 retrieval quality per strategy."
---

# RAG — Lab: Document Processing and Chunking

## Navigation

[Labs](../../README.md) / [RAG — Labs](../README.md) / RAG — Lab: Document Processing and Chunking

---


## Overview

Every chunk in the vector store is a retrievable unit — the granularity of your chunks determines how focused each embedding vector is and how well it matches a specific query. This lab makes that trade-off directly observable.

You will apply three chunking strategies to the same five corpus documents, index each strategy into a separate ChromaDB collection, and run a fixed set of queries against all three. The key observation is how top-1 similarity scores differ across strategies for the same query — particularly for queries about facts that span paragraph boundaries.

The recursive collection built here is used by `lab-retrieval-playground`, `lab-query-pipeline`, and `lab-rag-evaluation`. **Run this lab before the others.**

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `chunking` | `fixed_chunk()`, `sentence_chunk()`, `recursive_chunk()` — three split strategies applied to the same corpus |
| `chunk-size` | `CHUNK_SIZE` constant — maximum characters per chunk across all strategies |
| `chunk-overlap` | `overlap` parameter in `recursive_chunk()` — shared tokens between consecutive chunks |
| `recursive-chunking` | `recursive_chunk()` — priority-ordered delimiter splitting (paragraph → sentence → word) |
| `document-loader` | `load_corpus()` — reads `.md` files from the corpus directory |

---

## Setup

From `labs/rag/`:

```bash
pip install -r requirements.txt
cp .env.example .env

ollama pull nomic-embed-text
ollama serve
```

---

## Run

```bash
cd labs/rag
python lab-chunking-strategies/main.py
```

The script builds three ChromaDB collections in `CHROMA_PERSIST_DIR` (default `./chroma_db`) and prints the comparison results. It is safe to re-run — existing collections with the same name are deleted and rebuilt.

---

## Expected output

```
=== Loading corpus (5 documents) ===
Loaded: transformer-architecture.md  (3241 chars)
Loaded: text-embeddings.md           (2987 chars)
Loaded: information-retrieval.md     (3156 chars)
Loaded: llm-fine-tuning.md           (2834 chars)
Loaded: llm-inference.md             (2901 chars)
Total: 15119 chars across 5 documents

=== Strategy: fixed-size (size=512, overlap=64) ===
Chunks produced: 38
Avg chunk length: 487 chars  |  Min: 201  |  Max: 512
Indexed 38 chunks into collection 'chunks_fixed'

=== Strategy: sentence-boundary (target=512) ===
Chunks produced: 31
Avg chunk length: 496 chars  |  Min: 134  |  Max: 621
Indexed 31 chunks into collection 'chunks_sentence'

=== Strategy: recursive (size=512, overlap=64) ===
Chunks produced: 34
Avg chunk length: 491 chars  |  Min: 187  |  Max: 512
Indexed 34 chunks into collection 'chunks_recursive'

=== Retrieval comparison ===
Query: "How does the KV cache reduce inference cost from O(n²) to O(n)?"

  fixed-size    top-1 sim=0.7821  "...each step would require recomputing the Key..."
  sentence      top-1 sim=0.8012  "...Without optimisation, each autoregressive step..."
  recursive     top-1 sim=0.8534  "...The KV cache eliminates this by storing Key and Value..."

Query: "What is the difference between top-k and top-p sampling?"

  fixed-size    top-1 sim=0.8102  "...Top-k restricts sampling to the k tokens..."
  sentence      top-1 sim=0.8201  "...Top-k restricts sampling..."
  recursive     top-1 sim=0.8198  "...Top-k restricts sampling to the k tokens..."

✓ recursive top-1 ≥ fixed top-1 for paragraph-spanning query (0.8534 vs 0.7821)
✓ All 3 collections are queryable
```

Exact scores vary by model version. The ordering pattern — recursive outperforming fixed on paragraph-spanning queries — should be consistent.

---

## What to observe

- **Chunk count differs across strategies** for the same corpus. Fixed-size produces the most chunks; sentence-boundary the fewest. This is expected — each strategy has a different relationship between target size and natural text boundaries.
- **The score gap is larger on paragraph-spanning queries.** For queries about facts that flow across a sentence boundary, fixed-size chunking cuts through the relevant passage. Recursive chunking keeps paragraphs together, producing a chunk that contains the full explanation.
- **For single-sentence facts, strategies converge.** All three strategies tend to produce similar top-1 scores when the answer fits in one sentence — chunking granularity only matters when the answer spans multiple sentences.
- **The recursive collection is the canonical one** used by subsequent labs. If you want to experiment with a different chunk size, change `CHUNK_SIZE` in `.env` and re-run.

## Concepts verified

- [ ] All 3 collections are queryable after indexing
- [ ] Chunk counts differ across strategies for the same corpus
- [ ] Recursive top-1 similarity ≥ fixed top-1 for the paragraph-spanning query

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** change `CHUNK_SIZE = 512` to `CHUNK_SIZE = 100`
- **Expected degradation:**
  - Chunk count spikes (many small fragments per document)
  - Average chunk length drops to ~90–100 chars — most chunks no longer contain a complete thought
  - Top-1 similarity scores fall for paragraph-spanning queries because the relevant passage is split across multiple tiny chunks
  - The `✓ recursive top-1 ≥ fixed top-1` check may flip to `✗`

Restore `CHUNK_SIZE = 512` after the experiment (subsequent labs depend on the `chunks_recursive` collection built with the default size).

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama (`nomic-embed-text`) | Embeds chunks for ChromaDB insertion and query-time similarity scoring |
| ChromaDB (persistent) | Stores three separate collections — one per chunking strategy (`chunks_fixed`, `chunks_sentence`, `chunks_recursive`) |
