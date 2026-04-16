---
id: "rag-lab-embeddings"
title: "RAG — Lab: Embeddings and Vector Search"
type: "lab-readme"
step: "rag"
path: "labs/rag/lab-embeddings/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "embedding"
  - "cosine-similarity"
  - "embedding-model"
  - "vector-search"

prerequisites:
  - "docs/rag/embeddings-and-vector-search.md"

next:
  - "labs/rag/lab-chunking-strategies/README.md"

related:
  - "docs/rag/rag-fundamentals.md"

implementation_refs:
  - "labs/rag/lab-embeddings"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Demonstrates the Ollama embedding API, cosine similarity computation, and batch ranking — making vector similarity directly observable before retrieval is introduced."
---

## What this lab demonstrates

This lab makes the embedding mechanism concrete before any retrieval index or vector database is involved. You will:

1. Call the Ollama embedding API and inspect the returned vector.
2. Compute cosine similarity between a query and related and unrelated texts — observing the score gap that makes retrieval possible.
3. Batch-embed a small corpus and rank all items by similarity to a query — seeing the full distribution that a retrieval step sorts through.

This is the foundation of every lab that follows. The retrieval labs depend on you understanding why cosine similarity scores differ across texts and what score ranges are meaningful.

---

## Setup

From `labs/rag/`:

```bash
pip install -r requirements.txt
cp .env.example .env       # edit only if Ollama is not on localhost:11434

ollama pull nomic-embed-text
ollama serve               # already running if Ollama Desktop is installed
```

---

## Run

```bash
cd labs/rag
python lab-embeddings/main.py
```

No arguments. Output goes to stdout.

---

## Expected output

```
=== Observation 1: Single text embedding ===
Model       : nomic-embed-text
Vector dim  : 768
First 5 dims: [0.0234, -0.0891, 0.1203, -0.0445, 0.0712]

=== Observation 2: Cosine similarity ===
Query: "How does the transformer attention mechanism work?"

  [related]    "Self-attention allows each token ..."  similarity=0.8712
  [related]    "The transformer architecture uses ..." similarity=0.8341
  [unrelated]  "The weather in Madrid is sunny ..."    similarity=0.3821
  [unrelated]  "Recipe: mix flour, eggs, and ..."      similarity=0.2904

Semantic gap (related avg − unrelated avg): 0.53
✓ related avg (0.85) ≥ threshold (0.75)
✓ unrelated avg (0.34) ≤ threshold (0.55)

=== Observation 3: Batch ranking ===
Query: "What is the attention mechanism in transformers?"
Ranked corpus (10 texts, highest similarity first):

  #1  sim=0.8891  corpus/transformer-architecture.md § Self-attention
  #2  sim=0.8512  corpus/text-embeddings.md § How Embedding Models Work
  #3  sim=0.7943  corpus/information-retrieval.md § Neural Retrieval
  ...
  #10 sim=0.3102  corpus/llm-fine-tuning.md § When Fine-Tuning Is Appropriate

Batch embedding time: 1.24s for 10 texts
```

Exact similarity values differ by model version and quantization. The ordering and the gap between related and unrelated texts should be consistent.

---

## What to observe

- **Vector dimension**: `nomic-embed-text` always returns 768 dimensions. This is fixed by the model, not by input length.
- **Score gap**: related texts score ≥ 0.75; unrelated texts score ≤ 0.55. The gap between these ranges is what makes retrieval possible.
- **Ranking**: the most relevant text for the query appears first. Notice that texts discussing adjacent concepts (attention in retrieval vs. attention in transformers) score higher than fully unrelated texts.
- **Batch time**: embedding 10 texts in one request is much faster than 10 sequential requests. Note the total time printed.

## Concepts verified

- [ ] Related texts score ≥ 0.75 against the query; unrelated texts score ≤ 0.55
- [ ] Semantic gap (related avg − unrelated avg) is clearly positive — typically > 0.30
- [ ] Vector dimension is consistent across all embeddings from the same model (768 for nomic-embed-text)
- [ ] Corpus ranking places the most topically relevant document at position #1

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `RELATED_TEXTS`, replace both entries with texts from a completely different domain (e.g., cooking recipes, sports news)
- **Expected degradation:**
  - Related avg drops below 0.75 — the `✓` threshold check flips to `✗`
  - The semantic gap between "related" and "unrelated" collapses
  - Observation 2 shows that example quality, not just category membership, drives the measurable score gap

Restore the original transformer-related texts after the experiment.
