---
id: "rag-validation"
title: "RAG — Validation"
type: "validation"
step: "rag"
path: "docs/rag/validation.md"
status: "draft"
level: "intermediate"

concepts:
  - "retrieval-augmented-generation"
  - "retrieval-precision"
  - "retrieval-recall"
  - "answer-faithfulness"
  - "context-assembly"

prerequisites:
  - "docs/rag/implementation-reference.md"

next:
  - "docs/memory-context/README.md"

related:
  - "docs/rag/README.md"
  - "docs/rag/rag-evaluation-and-metrics.md"

implementation_refs:
  - "labs/rag/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"
  - "meta/standards/validation/labs-checklist.md"

summary: "Defines the conceptual, practical, lab, and integration validation criteria that must be satisfied for the RAG module to be considered complete."
---

# RAG — Validation

## Navigation

[Docs](../README.md) / [Retrieval-Augmented Generation](README.md) / RAG — Validation

---

## 1. Validation Overview

This document defines when the RAG module is complete. A learner has completed this module when they can explain the two-phase RAG pipeline, implement each component, run all six required labs, and reason about quality trade-offs at the retrieval and generation stages.

Validation is organized across four levels: conceptual (understanding), practical (implementation ability), lab (execution), and integration (cross-component reasoning).

---

## 2. Conceptual Validation

| Concept | Validation Method |
|---------|------------------|
| Retrieval-Augmented Generation | Explain the two-phase model (indexing vs. query) and why RAG solves a problem that fine-tuning does not |
| Parametric vs. non-parametric memory | Describe when each is appropriate; explain the staleness trade-off |
| Embeddings | Explain why cosine similarity measures semantic proximity; identify what breaks when the embedding model changes |
| Chunking | Explain the trade-off between chunk size and retrieval precision; describe why overlap is needed |
| Dense vs. sparse retrieval | Give a query example where dense retrieval fails but BM25 succeeds, and vice versa |
| Context assembly | Explain token budget allocation; describe the lost-in-the-middle effect and how to compensate |
| RAG evaluation | Distinguish retrieval metrics from generation metrics; explain why both must be measured independently |

---

## 3. Practical Validation

**Task 1: Build an ingestion pipeline**
- Load a directory of plain-text documents.
- Chunk them with recursive character splitting (chunk size 512, overlap 64).
- Embed all chunks with `nomic-embed-text` via Ollama.
- Store them in a ChromaDB collection.
- Expected: index contains N chunks, metadata attached, no embedding errors.

**Task 2: Implement the query pipeline**
- Accept a user query string.
- Embed the query, retrieve top-5 chunks, assemble context within an 8192-token window.
- Generate a response using `llama3.2`.
- Expected: response references content from retrieved chunks; context block does not exceed token budget.

**Task 3: Implement hybrid retrieval**
- Add BM25 sparse retrieval alongside the ChromaDB dense retrieval.
- Merge both ranked lists using RRF with k=60.
- Expected: a query containing a rare technical term returns better results than dense-only retrieval.

**Task 4: Compute retrieval metrics**
- Build a 10-question evaluation set for a small corpus.
- Run the retrieval pipeline on each question and record retrieved chunk IDs.
- Compute Precision@5 and Recall@5 against the ground-truth chunk IDs.
- Expected: Precision@5 ≥ 0.6, Recall@5 ≥ 0.7 for a well-configured pipeline.

---

## 4. Lab Validation

| Lab | Validation Criteria |
|-----|-------------------|
| `lab-embeddings` | Embedding API returns a vector of the expected dimension; cosine similarity between semantically related texts is ≥ 0.75; cosine similarity between unrelated texts is ≤ 0.55 |
| `lab-chunking-strategies` | Three strategy variants (fixed, sentence, recursive) are indexed into separate collections; query run against all three shows recursive chunking returns highest top-1 similarity for paragraph-spanning facts |
| `lab-retrieval-playground` | Dense retrieval, BM25 retrieval, and RRF hybrid retrieval all return results; at least one query shows BM25 outperforms dense retrieval for an exact-term query |
| `lab-query-pipeline` | Full pipeline runs end-to-end; generated response cites at least one source chunk; context block stays within the 8192-token budget |
| `lab-rag-evaluation` | Evaluation set of ≥ 20 questions is executed; Precision@5 and Recall@5 are computed and printed; LLM-as-judge faithfulness score is computed for ≥ 10 answers |
| `lab-integration` | Ingestion completes without error; all in-scope demo queries receive a grounded answer with at least one source cited; out-of-scope query is declined; context block stays within token budget for every query |

---

## 5. Integration Validation

**Explain the retrieval-to-generation dependency chain.**
Describe how a low Recall@5 score propagates to a low faithfulness score: if the correct chunk is never retrieved, the model cannot produce a faithful answer regardless of how well the context assembler or generation prompt is configured.

**Diagnose a pipeline failure.**
Given this observation: "The pipeline returns an answer but it is factually wrong, and faithfulness scores are high."
Expected analysis: High faithfulness with wrong answers means the retrieved chunks contain incorrect or outdated information — the model is faithfully reproducing bad source material. The fix is in the corpus (update or remove incorrect documents), not in the retrieval or generation components.

**Explain the embedding model consistency constraint.**
Describe what happens if the embedding model is updated after the index is built. Explain why the index must be rebuilt from scratch and what monitoring would detect the mismatch before it causes silent failures.

**Describe the token budget allocation.**
Given: context window = 8192 tokens, system prompt = 150 tokens, user query = 50 tokens, `max_tokens` = 512. Calculate the available budget for retrieved context and explain what happens if the assembler omits the output reservation.

---

## 6. Failure Detection

**Incorrect: embedding the query with a different model than was used for indexing.**
Result: cosine similarity scores are near 0.5 for all chunks; retrieval is essentially random. Detection: all queries return the same top-k candidates regardless of query content.

**Incorrect: not applying token budget guard.**
Result: prompt exceeds context window; API truncates input silently or returns error. Detection: response is malformed or references content that was not in the assembled context.

**Incorrect: using raw document text instead of chunks as retrieval units.**
Result: embedding of a full document averages many topics; queries match the document if any of their topics aligns, not specifically where the answer is. The retrieved "chunk" contains thousands of tokens that overflow the context budget. Detection: context block contains only 1–2 documents but exceeds the token budget.

**Incorrect: measuring only generation quality without retrieval quality.**
Result: low faithfulness scores appear to indicate a generation problem; prompt engineering changes are applied; no improvement is observed because the actual problem is low Recall@5 — the answer-bearing chunk is never in the context. Detection: checking Recall@5 reveals near-zero recall on failing queries.

**Incorrect: building a new ChromaDB in-memory collection on each query.**
Result: the collection is empty on every query; all retrieval returns zero results. Detection: retrieval always returns zero chunks regardless of query content.

---

## 7. Completion Criteria

The RAG module is complete when:

- All seven core concepts in section 2 can be explained accurately and causally.
- All four practical tasks in section 3 are implemented and produce expected outputs.
- All six labs in section 4 execute without errors and satisfy their validation criteria.
- All four integration scenarios in section 5 are reasoned through correctly.
- No failure patterns from section 6 are present in the implementation.

---

## 8. Self-Assessment Checklist

- [ ] I can explain why RAG solves the knowledge-currency problem without retraining
- [ ] I can implement recursive character chunking with overlap
- [ ] I can embed text with Ollama's embedding API and compute cosine similarity
- [ ] I can build and query a ChromaDB collection
- [ ] I can implement BM25 sparse retrieval and RRF merge
- [ ] I can assemble a context block within a calculated token budget
- [ ] I can construct a RAG prompt with framing instructions
- [ ] I can build a fixed evaluation set and compute Precision@k and Recall@k
- [ ] I can implement LLM-as-judge for faithfulness scoring
- [ ] I can diagnose whether a failure is in the retrieval or generation stage

---

## 9. Next Steps

**If validation fails on retrieval metrics:** revisit `retrieval-strategies.md` and `lab-retrieval-playground`. Run the hybrid retrieval variant and compare its recall against dense-only.

**If validation fails on generation quality:** revisit `context-assembly.md`. Check that the context framing instructions include an explicit "answer only from context" directive. Verify that the token budget guard is active.

**If validation passes:** proceed to `docs/memory-context/README.md`. Memory and context management extends the RAG pattern by maintaining persistent state across conversation turns — building on the non-parametric memory concept introduced in this module.
