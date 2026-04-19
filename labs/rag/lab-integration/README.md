---
id: "rag-lab-integration"
title: "RAG — Lab: Full Pipeline Integration"
type: "lab-readme"
step: "rag"
path: "labs/rag/lab-integration/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "document-ingestion-pipeline"
  - "query-pipeline"
  - "context-assembler"
  - "vector-store"
  - "retrieval-augmented-generation"

prerequisites:
  - "docs/rag/architecture.md"
  - "labs/rag/lab-rag-evaluation/README.md"

next:
  - "docs/rag/validation.md"

related:
  - "docs/rag/implementation-reference.md"
  - "docs/rag/context-assembly.md"

implementation_refs:
  - "labs/rag/lab-integration"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Integrates all RAG pipeline components — ingestion, chunking, embedding, vector indexing, retrieval, context assembly, and generation — into a single end-to-end script that demonstrates the full architecture."
---

# RAG — Lab: Full Pipeline Integration

## Navigation

[Labs](../../README.md) / [RAG — Labs](../README.md) / RAG — Lab: Full Pipeline Integration

---

## Overview

The previous labs build each pipeline component in isolation. This lab composes all of them into a single end-to-end execution that mirrors the architecture described in `docs/rag/architecture.md`.

**Ingestion phase** (runs once): load the corpus → chunk with recursive splitting → batch-embed → persist to ChromaDB.

**Query phase** (runs per query): embed the query → dense retrieval from ChromaDB → deduplicate → token-budget assembly → grounded generation.

Five demo queries exercise the full pipeline: four in-scope questions drawn from the corpus and one out-of-scope question that the pipeline correctly declines.

Unlike the earlier labs, this lab builds its own index from scratch (`rag_integration` collection) and does not depend on collections from previous labs.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `document-ingestion-pipeline` | `build_index()` — loads corpus, chunks, embeds, and persists to ChromaDB |
| `query-pipeline` | `run_query()` — embed → retrieve → deduplicate → assemble → generate |
| `context-assembler` | `assemble_context()` (from shared) — token-budget selection and numbered chunk formatting |
| `vector-store` | ChromaDB collection `rag_integration` — persists vectors for cosine similarity retrieval |
| `retrieval-augmented-generation` | full `main()` flow — two-phase architecture: offline ingestion + online generation |

---

## Setup

```bash
cd labs/rag
pip install -r requirements.txt
cp .env.example .env     # edit only if Ollama is not on localhost:11434

ollama pull nomic-embed-text
ollama pull llama3.2
ollama serve             # already running if Ollama Desktop is installed
```

This lab does not require running any other lab first.

---

## Run

```bash
cd labs/rag
python lab-integration/main.py
```

No arguments. The script builds the index and runs all demo queries sequentially. Output goes to stdout.

---

## Expected Output

```
=== Ingestion phase ===
Loaded 5 corpus documents
Chunked 5 documents → 34 chunks (size=512, overlap=64)
Embedded 34 chunks in 2.3s using nomic-embed-text
Indexed 34 chunks into collection 'rag_integration' ✓

=== Query phase ===
Embedding model : nomic-embed-text
Generation model: llama3.2
Context window  : 8192 tokens

--- Query ---
Q: How does the KV cache reduce inference cost during autoregressive decoding?
Retrieved 5 | After dedup: 4 | Best similarity: 0.8712
Context block: 648 tokens (budget: 7330) ✓
Answer: The KV cache stores the Key and Value tensors computed for each token...
Sources: llm-inference.md

--- Query ---
Q: What is the capital of France?
Retrieved 5 | After dedup: 5 | Best similarity: 0.3821
Out-of-scope: declined ✓
Answer: I don't have enough information in the provided context to answer that question.

...

=== Pipeline summary ===
Total queries   : 5
In-scope        : 4
Declined (OOS)  : 1 ✓

Full RAG pipeline complete ✓
```

Exact similarity scores vary by model version. The ordering (in-scope answered, out-of-scope declined) and the pipeline summary counts should be consistent.

---

## What to observe

- **Ingestion timing**: note how long batch embedding takes for 34 chunks. Embedding is the dominant cost at index time.
- **Similarity gap**: in-scope queries score ≥ 0.75; the out-of-scope query scores ≤ 0.50. This gap is what makes the decline threshold meaningful.
- **Dedup count**: "After dedup" is usually 1–2 less than "Retrieved" when two chunks from the same document section are returned. Watch for cases where dedup makes no reduction — it means all top-k chunks came from different documents.
- **Token budget**: observe the context block token count printed for each query. It should always be below the stated budget. Large documents with many matches produce larger context blocks.
- **Out-of-scope decline**: the final query ("What is the capital of France?") should always be declined. This confirms the minimum similarity threshold is active.
- **Pipeline summary**: verify that `In-scope + Declined = Total queries`.

---

## Concepts verified

- [ ] Ingestion completes without error — collection contains N chunks ✓
- [ ] All in-scope queries receive a non-empty answer with at least one source file cited
- [ ] Out-of-scope query produces the decline message — no hallucinated answer
- [ ] Context block token count is below the stated budget for every query
- [ ] Pipeline summary: `In-scope + Declined (OOS) = Total queries`

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** replace `SYSTEM_PROMPT` with `"You are a helpful assistant."` (remove the "using only the information in the provided Context" constraint)
- **Expected degradation:**
  - Out-of-scope query ("What is the capital of France?") is answered from parametric memory — the model says "Paris" confidently despite zero corpus evidence
  - In-scope answers may blend retrieved content with model training knowledge, making source citations unreliable
  - Pipeline summary shows `Declined (OOS): 0`, hiding the loss of the out-of-scope guard
  - Faithfulness scores (if measured) would drop because the model no longer restricts itself to the context

Restore the original `SYSTEM_PROMPT` after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama (`nomic-embed-text`) | Generates embedding vectors for corpus chunks and user queries |
| Ollama (`llama3.2`) | Generates grounded answers from assembled context blocks |
| ChromaDB (persistent) | Hosts `rag_integration` collection — built fresh on each run |
