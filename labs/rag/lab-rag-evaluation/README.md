---
id: "rag-lab-rag-evaluation"
title: "RAG — Lab: Evaluation and Metrics"
type: "lab-readme"
step: "rag"
path: "labs/rag/lab-rag-evaluation/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "retrieval-precision"
  - "retrieval-recall"
  - "answer-faithfulness"
  - "answer-relevance"
  - "evaluation-dataset"

prerequisites:
  - "docs/rag/rag-evaluation-and-metrics.md"
  - "labs/rag/lab-query-pipeline/README.md"

next:
  - "docs/rag/validation.md"

related:
  - "docs/rag/retrieval-strategies.md"

implementation_refs:
  - "labs/rag/lab-rag-evaluation"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Measures RAG pipeline quality using Precision@k, Recall@k, and LLM-as-judge faithfulness on a fixed 20-question evaluation set, and compares results across top_k=5 and top_k=10."
---

# RAG — Lab: Evaluation and Metrics

## Navigation

[Labs](../../README.md) / [RAG — Labs](../README.md) / RAG — Lab: Evaluation and Metrics

---


## What this lab demonstrates

A pipeline that feels like it works may still be broken in ways that only measurement reveals. This lab applies the evaluation framework described in `docs/rag/rag-evaluation-and-metrics.md` to the full pipeline from `lab-query-pipeline`.

You will run a fixed 20-question evaluation set against two pipeline configurations (top_k=5 and top_k=10), compute Precision@5 and Recall@5 for each, and run LLM-as-judge faithfulness scoring on a subset of the generated answers. The key observation is that Recall@5 improves when top_k increases — demonstrating the recall/precision trade-off at the retrieval stage.

**Requires:** the `chunks_recursive` ChromaDB collection built by `lab-chunking-strategies`.

---

## Setup

```bash
cd labs/rag
python lab-chunking-strategies/main.py   # if not already run

ollama pull nomic-embed-text
ollama pull llama3.2
```

---

## Run

```bash
cd labs/rag
python lab-rag-evaluation/main.py
```

---

## Expected output

```
=== RAG Evaluation ===
Corpus       : 5 documents
Eval set     : 20 questions
Collection   : chunks_recursive

--- Retrieval metrics (top_k=5) ---
Precision@5 : 0.71
Recall@5    : 0.74
MRR         : 0.82

--- Retrieval metrics (top_k=10) ---
Precision@5 : 0.64   ← lower precision with more candidates
Recall@5    : 0.89   ← higher recall: correct chunks surface more often
MRR         : 0.85

✓ Recall@5 (top_k=10) > Recall@5 (top_k=5): 0.89 > 0.74

--- Faithfulness (LLM-as-judge, 10 answers) ---
Scored     : 10 answers
Faithful   : 8 / 10
Mean score : 0.80

✓ Mean faithfulness ≥ 0.70

=== Summary ===
Retrieval precision (top_k=5) : 0.71
Retrieval recall    (top_k=5) : 0.74
Retrieval recall    (top_k=10): 0.89
Faithfulness mean             : 0.80
```

---

## What to observe

- **Precision falls as top_k grows.** More candidates means more irrelevant chunks in the retrieved set. Precision@5 drops between top_k=5 and top_k=10.
- **Recall rises as top_k grows.** The correct chunk is more likely to appear somewhere in the top 10 than in the top 5. This is the recall/precision trade-off.
- **MRR reveals ranking quality.** An MRR near 1.0 means the correct chunk is almost always ranked first. An MRR near 0.5 means it is typically ranked second or third.
- **Faithfulness is independent of retrieval recall.** A high faithfulness score means the model is using the retrieved content correctly — but if recall is low, the context may not have contained the right information in the first place.

## Concepts verified

- [ ] Recall@5 (top_k=10) ≥ Recall@5 (top_k=5) — more candidates improve recall
- [ ] Precision@5 decreases when top_k increases — more candidates dilute precision
- [ ] Mean faithfulness ≥ 0.70

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in the second `evaluate_retrieval` call, change `top_k=10` to `top_k=50`
- **Expected degradation:**
  - Precision@5 drops dramatically (50 chunks retrieved, only 1–2 from the expected source)
  - Recall@5 approaches 1.0 — the correct source almost always appears somewhere in 50 results
  - The contrast makes the recall/precision trade-off extreme and shows why unbounded `top_k` is impractical
  - Faithfulness may also decline — more irrelevant context increases the chance of hallucination

Restore `top_k=10` after the experiment.

## About the evaluation set

The 20 questions are drawn directly from the five corpus documents. Each question maps to one source file that contains the answer. Ground truth is defined at the **source file level** — a retrieved chunk is counted as relevant if its `source` metadata field matches the expected source for that question. This is a practical approximation when chunk-level IDs are not pre-labelled.
