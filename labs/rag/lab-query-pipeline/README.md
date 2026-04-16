---
id: "rag-lab-query-pipeline"
title: "RAG — Lab: Query Pipeline"
type: "lab-readme"
step: "rag"
path: "labs/rag/lab-query-pipeline/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "context-assembly"
  - "token-budget"
  - "chunk-deduplication"
  - "lost-in-the-middle"
  - "prompt-context-block"

prerequisites:
  - "docs/rag/context-assembly.md"
  - "labs/rag/lab-retrieval-playground/README.md"

next:
  - "labs/rag/lab-rag-evaluation/README.md"

related:
  - "docs/rag/retrieval-strategies.md"
  - "docs/llm-fundamentals/context-window.md"

implementation_refs:
  - "labs/rag/lab-query-pipeline"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Assembles the full RAG query pipeline — embed, retrieve, deduplicate, budget-guard, assemble context, generate — and makes token budget management and out-of-scope handling observable."
---

## What this lab demonstrates

Individual components — embedding, retrieval, context assembly — work in isolation in the previous labs. Here they are composed into a single `rag_query()` function that runs end-to-end: embed the query, retrieve candidates, deduplicate, select within the token budget, format the context block, and generate a grounded response.

Two behaviours are tested explicitly:
1. **In-scope query** — the answer is in the corpus. The response should cite at least one `[N]` source reference.
2. **Out-of-scope query** — the answer is not in the corpus. The response should decline to answer rather than hallucinate.

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
python lab-query-pipeline/main.py
```

---

## Expected output

```
=== RAG Query Pipeline ===
Embedding model : nomic-embed-text
Generation model: llama3.2
Context window  : 8192 tokens
Token budget    : 7330 tokens available for context

--- Query 1 (in-scope) ---
Q: What is the difference between top-k and top-p sampling?

Retrieved 5 chunks | After dedup: 4 | Selected: 4 (712 tokens)
Context block fits within budget ✓

Answer:
Top-k sampling restricts the candidate pool to the k tokens with the highest
probability [1]. Top-p (nucleus) sampling retains the smallest set of tokens
whose cumulative probability reaches a threshold p [1]. The key difference is
that top-k fixes the pool size while top-p adapts it to the shape of the
distribution [2].

Sources used: [1] llm-inference.md  [2] llm-inference.md

--- Query 2 (in-scope) ---
Q: How does LoRA reduce the number of trainable parameters?
...

--- Query 3 (out-of-scope) ---
Q: What is the capital of France?

Retrieved 5 chunks | After dedup: 5 | Selected: 5
Highest similarity: 0.3821 — below threshold (0.50)

Answer:
I don't have enough information in the provided context to answer that question.

✓ Out-of-scope query correctly declined
```

---

## What to observe

- **Token budget printed explicitly** — observe how system prompt, query, and output reservation consume the window before any context is added.
- **Deduplication removes near-duplicate chunks** — if two chunks from the same document section are retrieved, one is dropped. Watch the "After dedup" count.
- **Source citations `[N]`** — in-scope answers cite the chunks they draw from. Check whether the cited source matches the expected corpus file.
- **Out-of-scope decline** — the system prompt instructs the model to say it doesn't know rather than guess. Observe that no fabricated answer appears for the France query.

## Concepts verified

- [ ] In-scope queries include at least one `[N]` source citation in the answer
- [ ] Out-of-scope query produces a decline response — no hallucinated answer
- [ ] Token budget is not exceeded for any query (context block fits within budget)

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** change `MIN_SIMILARITY_THRESHOLD = 0.50` to `MIN_SIMILARITY_THRESHOLD = 0.0`
- **Expected degradation:**
  - Out-of-scope queries (e.g., "What is the capital of France?") are no longer flagged as out-of-scope
  - The model receives irrelevant retrieved chunks as context and may fabricate an answer
  - The `✓ Out-of-scope query correctly declined` check disappears or flips to `✗`
  - The similarity score is still printed but no longer gates the pipeline

Restore `MIN_SIMILARITY_THRESHOLD = 0.50` after the experiment.
