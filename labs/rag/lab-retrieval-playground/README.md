---
id: "rag-lab-retrieval-playground"
title: "RAG — Lab: Retrieval Strategies"
type: "lab-readme"
step: "rag"
path: "labs/rag/lab-retrieval-playground/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "dense-retrieval"
  - "sparse-retrieval"
  - "hybrid-retrieval"
  - "reciprocal-rank-fusion"
  - "reranking"

prerequisites:
  - "docs/rag/retrieval-strategies.md"
  - "labs/rag/lab-chunking-strategies/README.md"

next:
  - "labs/rag/lab-query-pipeline/README.md"

related:
  - "docs/rag/embeddings-and-vector-search.md"

implementation_refs:
  - "labs/rag/lab-retrieval-playground"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Compares dense retrieval, BM25 sparse retrieval, and RRF hybrid merge on a fixed query set designed to expose the failure cases of each strategy."
---

# RAG — Lab: Retrieval Strategies

## Navigation

[Labs](../../README.md) / [RAG — Labs](../README.md) / RAG — Lab: Retrieval Strategies

---


## Overview

No single retrieval strategy is universally better. Dense retrieval misses rare exact terms; BM25 misses paraphrase and synonymy. This lab runs both against the same index and merges their results, making the complementary failure modes directly observable.

You will run a fixed set of queries — some designed to favour dense retrieval, some to favour BM25 — and compare what each strategy surfaces. The hybrid RRF merge shows how combining both ranked lists recovers candidates that neither alone would rank at the top.

**Requires:** the `chunks_recursive` ChromaDB collection built by `lab-chunking-strategies`.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `dense-retrieval` | `dense_retrieve()` — queries ChromaDB by cosine similarity |
| `sparse-retrieval` | `bm25_retrieve()` — scores corpus texts using `rank_bm25.BM25Okapi` |
| `hybrid-retrieval` | `hybrid_retrieve()` — runs dense and sparse retrieval then merges results |
| `reciprocal-rank-fusion` | `rrf_merge()` — combines two ranked lists by summing `1/(k + rank)` per document |
| `reranking` | commentary in output — concept explained; cross-encoder not implemented to avoid PyTorch dependency |

---

## Setup

```bash
cd labs/rag
# Run lab-chunking-strategies first if you haven't already
python lab-chunking-strategies/main.py

pip install -r requirements.txt
ollama pull nomic-embed-text
```

---

## Run

```bash
cd labs/rag
python lab-retrieval-playground/main.py
```

---

## Expected output

```
=== Dense retrieval ===
Query: "How does cosine similarity measure semantic proximity?"
  #1 sim=0.8901  text-embeddings.md         "...cosine of the angle between..."
  #2 sim=0.8512  information-retrieval.md   "...encoding both the query and..."
  #3 sim=0.7834  transformer-architecture.md "...dot product of one token's..."

Query: "BM25 saturation function"
  #1 sim=0.6821  information-retrieval.md   "...BM25 (Best Match 25) has been..."
  #2 sim=0.6103  llm-fine-tuning.md         "...scores each document by a..."
  ← dense struggles with the exact term "saturation function"

=== BM25 sparse retrieval ===
Query: "BM25 saturation function"
  #1 score=4.21  information-retrieval.md   "...saturation function that gives..."
  ← BM25 recovers the exact term immediately

Query: "How does cosine similarity measure semantic proximity?"
  #1 score=2.12  text-embeddings.md         "...cosine similarity, defined as..."
  #2 score=1.87  information-retrieval.md   "...cosine similarity..."

=== Hybrid RRF merge ===
Query: "BM25 saturation function"
  #1 rrf=0.0323  information-retrieval.md  (dense #1 + BM25 #1)
  #2 rrf=0.0161  text-embeddings.md        (dense #2)

✓ BM25 outperforms dense on exact-term query "BM25 saturation function"
✓ Dense outperforms BM25 on semantic query (cosine similarity gap > 0.10)
✓ RRF top-1 matches BM25 top-1 for exact-term query
```

---

## What to observe

- **Exact-term queries** — queries containing a rare technical phrase ("BM25 saturation function", "RoPE positional encoding") expose dense retrieval's weakness. BM25 finds the term directly.
- **Semantic queries** — paraphrased queries ("how does the model know word order?") show dense retrieval's strength. BM25 returns nothing useful if the exact words are absent.
- **RRF is score-scale agnostic** — BM25 scores and cosine similarities live on different scales. RRF uses only rank position, so no calibration is needed.

## Concepts verified

- [ ] BM25 outranks dense on at least one exact-term query
- [ ] Dense retrieval returns similarity ≥ 0.70 on at least one semantic query
- [ ] RRF top-1 for an exact-term query matches or improves on BM25 top-1

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `bm25_retrieve()`, remove `.lower()` from the query tokenization: change `bm25.get_scores(query.lower().split())` to `bm25.get_scores(query.split())`
- **Expected degradation:**
  - BM25 fails on mixed-case queries — query tokens no longer match the lowercased corpus index
  - Exact-term queries that would have ranked first now score near 0
  - The `✓ BM25 outranked dense on ...` validation check flips to `✗`
  - RRF hybrid also degrades for exact-term queries because the BM25 signal collapses

Restore `.lower()` on both sides after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama (`nomic-embed-text`) | Generates query embedding for dense retrieval |
| ChromaDB (persistent) | Hosts `chunks_recursive` collection built by `lab-chunking-strategies` |
