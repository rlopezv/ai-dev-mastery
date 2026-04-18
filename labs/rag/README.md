---
id: "rag-labs-readme"
title: "RAG — Labs"
type: "lab-readme"
step: "rag"
path: "labs/rag/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "embedding"
  - "vector-search"
  - "chunking"
  - "dense-retrieval"
  - "sparse-retrieval"
  - "hybrid-retrieval"
  - "context-assembly"
  - "retrieval-precision"
  - "answer-faithfulness"

prerequisites:
  - "docs/rag/implementation-reference.md"

next:
  - "labs/memory-context/README.md"

related:
  - "docs/rag/README.md"

implementation_refs:
  - "labs/rag/lab-embeddings"
  - "labs/rag/lab-chunking-strategies"
  - "labs/rag/lab-retrieval-playground"
  - "labs/rag/lab-query-pipeline"
  - "labs/rag/lab-rag-evaluation"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Five labs that build the RAG pipeline incrementally — from embedding a single text to running a fully evaluated query pipeline with Precision@k and faithfulness metrics."
---

# RAG — Labs

## Navigation

[Labs](../README.md) / RAG — Labs

---


## 1. Overview

These labs implement the RAG pipeline described in `docs/rag/` component by component. Each lab introduces one system layer, and the later labs compose the results of earlier ones. The sequence ends with a complete, measurable pipeline: `lab-query-pipeline` runs end-to-end retrieval and generation, and `lab-rag-evaluation` applies retrieval and generation quality metrics against a fixed evaluation set.

All labs run fully locally using **Ollama** for embeddings and generation and **ChromaDB** for vector storage. No cloud API keys are required.

**Not covered:**
- Agentic RAG where the model decides when to retrieve (see `ai-agents`)
- Persistent memory across conversation turns (see `memory-context`)
- Production vector database deployment (see `deployment-scaling`)

---

## 2. Lab Inventory

| Lab | Demonstrates | Type | Required | Doc |
|-----|-------------|------|----------|-----|
| `lab-embeddings` | Embedding API, cosine similarity, batch embedding, score distributions | implementation | yes | `embeddings-and-vector-search.md` |
| `lab-chunking-strategies` | Fixed-size, sentence-boundary, and recursive chunking; ChromaDB ingestion; per-strategy retrieval quality | implementation | yes | `document-processing-and-chunking.md` |
| `lab-retrieval-playground` | Dense retrieval, BM25 sparse retrieval, RRF hybrid merge; failure cases per strategy | implementation | yes | `retrieval-strategies.md` |
| `lab-query-pipeline` | Full query pipeline: embed → retrieve → deduplicate → assemble → generate; token budget guard | implementation | yes | `context-assembly.md` |
| `lab-rag-evaluation` | Precision@k, Recall@k, LLM-as-judge faithfulness; pipeline comparison across top-k values | implementation | yes | `rag-evaluation-and-metrics.md` |

All five labs are required.

---

## 3. Execution Model

All labs use the **`intermediate` infrastructure profile**: Ollama (embedding + generation) plus ChromaDB (in-process persistent).

**Prerequisites:**

```bash
# 1. Pull required Ollama models
ollama pull nomic-embed-text
ollama pull llama3.2

# 2. Install Python dependencies
pip install -r labs/rag/requirements.txt

# 3. Configure environment
cd labs/rag
cp .env.example .env
# Edit .env only if Ollama runs on a non-default URL or you want different models
```

**Running the labs in order:**

```bash
cd labs/rag

python lab-embeddings/main.py
python lab-chunking-strategies/main.py
python lab-retrieval-playground/main.py
python lab-query-pipeline/main.py
python lab-rag-evaluation/main.py
```

Each lab prints structured output to stdout. No server process is started. Labs 3–5 depend on the ChromaDB index built by `lab-chunking-strategies` — run them in order.

**Checking Ollama is ready:**

```bash
curl http://localhost:11434/api/tags
# Should list nomic-embed-text and llama3.2
```

---

## 4. Lab Structure

### Read the corpus before running the labs

```text
labs/rag/corpus/
├── transformer-architecture.md
├── text-embeddings.md
├── information-retrieval.md
├── llm-fine-tuning.md
└── llm-inference.md
```

These five documents are your knowledge base. Read them before running any lab. They are short (400–600 words each) and cover topics from this tutorial. Knowing their content lets you predict which chunks should be retrieved for a given query, understand why certain similarity scores are higher than others, and write the ground-truth evaluation questions in `lab-rag-evaluation` with confidence.

In a real RAG system, these files would be your company's documentation, product manuals, or knowledge articles. Here they are fixed so that results are comparable across labs and reproducible across runs.


### Directory layout

```text
labs/rag/
├── README.md                      ← this file
├── .env.example                   ← environment variable template
├── requirements.txt               ← Python dependencies
├── shared/
│   ├── __init__.py
│   └── config.py                  ← Ollama client, ChromaDB client factory, health check
├── corpus/                        ← read these before running the labs
│   ├── transformer-architecture.md
│   ├── text-embeddings.md
│   ├── information-retrieval.md
│   ├── llm-fine-tuning.md
│   └── llm-inference.md
├── lab-embeddings/
│   ├── README.md
│   └── main.py
├── lab-chunking-strategies/
│   ├── README.md
│   └── main.py
├── lab-retrieval-playground/
│   ├── README.md
│   └── main.py
├── lab-query-pipeline/
│   ├── README.md
│   └── main.py
└── lab-rag-evaluation/
    ├── README.md
    └── main.py
```

`shared/config.py` provides the Ollama OpenAI client and the ChromaDB PersistentClient. The `corpus/` directory contains the fixed plain-text Markdown files used across all labs. `lab-chunking-strategies` builds the ChromaDB collection from this corpus; later labs read from it.

---

## 5. Mapping to Documentation

| Documentation | Lab |
|---------------|-----|
| `docs/rag/embeddings-and-vector-search.md` | `lab-embeddings` |
| `docs/rag/document-processing-and-chunking.md` | `lab-chunking-strategies` |
| `docs/rag/retrieval-strategies.md` | `lab-retrieval-playground` |
| `docs/rag/context-assembly.md` | `lab-query-pipeline` |
| `docs/rag/rag-evaluation-and-metrics.md` | `lab-rag-evaluation` |
| `docs/rag/architecture.md` | all labs (pipeline components) |
| `docs/rag/implementation-reference.md` | all labs (patterns and data structures) |

---

## 6. Validation

**lab-embeddings**
```
Embedding API returns a vector of length 768 (nomic-embed-text dimension).
cosine_similarity(query_vec, related_doc_vec) ≥ 0.75.
cosine_similarity(query_vec, unrelated_doc_vec) ≤ 0.55.
Batch embedding of 10 texts completes without error.
Ranked output lists texts in decreasing similarity order.
```

**lab-chunking-strategies**
```
Fixed-size strategy:     N_fixed chunks indexed; chunk length ≤ chunk_size + 20 chars.
Sentence strategy:       N_sentence chunks indexed; each chunk ends at a sentence boundary.
Recursive strategy:      N_recursive chunks indexed; top-1 similarity for a paragraph-
                         spanning query is higher than fixed-size top-1 for the same query.
All three ChromaDB collections are queryable after the script exits.
```

**lab-retrieval-playground**
```
Dense retrieval:          top-5 results returned with cosine distance < 0.5 for
                          on-topic queries.
BM25 sparse retrieval:    at least one exact-term query where BM25 ranks the correct
                          chunk higher than dense retrieval.
RRF hybrid:               merged list contains the union of both candidates; RRF top-1
                          matches the human-expected best chunk for at least 3 of 5
                          test queries.
```

**lab-query-pipeline**
```
Full pipeline runs end-to-end without error.
Context block token count ≤ (context_window - system_prompt - query - output_reserve).
Generated response cites at least one [N] source reference.
Out-of-scope query returns "I don't have enough information" (or equivalent),
not a hallucinated answer.
```

**lab-rag-evaluation**
```
Evaluation set of ≥ 20 queries is executed against the pipeline.
Precision@5 and Recall@5 are printed for top_k=5 and top_k=10.
Recall@5 (top_k=10) ≥ Recall@5 (top_k=5) — demonstrating the recall/precision trade-off.
LLM-as-judge faithfulness scores are printed for ≥ 10 generated answers.
Mean faithfulness score ≥ 0.70 for a corpus-aligned query set.
```

---

## 7. Common Issues

**`nomic-embed-text` not found.**
Run `ollama pull nomic-embed-text` before executing any lab. The embedding model is separate from the generation model and must be pulled explicitly.

**ChromaDB collection not found in `lab-retrieval-playground` or later labs.**
`lab-chunking-strategies` must run first — it builds the persistent ChromaDB collection at `CHROMA_PERSIST_DIR`. If the directory is missing or empty, later labs will raise a `CollectionNotFoundError`. Re-run `lab-chunking-strategies/main.py`.

**Cosine distance returns 1.0 for all queries.**
ChromaDB returns cosine *distance* (1 − similarity), not similarity. A distance of 1.0 means the vectors are orthogonal — near-zero similarity. This happens when the collection was built with a different embedding model than the query uses. Check that `EMBED_MODEL` in `.env` matches what was used during ingestion. Delete `CHROMA_PERSIST_DIR` and re-run `lab-chunking-strategies/main.py`.

**Token budget exceeded — API returns context length error.**
The output reservation or prompt framing overhead is not being subtracted from the budget. Check `assemble_context()` in `shared/config.py` — ensure `output_reserve` and a framing overhead of at least 100 tokens are subtracted before selection.

**LLM returns empty response or `None`.**
Ollama is running but the `llama3.2` model is not loaded. Run `ollama pull llama3.2`. If the model is present but responses are empty, the context block may be malformed — print the full messages list before the API call to inspect.

**LLM-as-judge returns inconsistent scores.**
Small models (3B) are unreliable as judges. Use `llama3.2:7b` or larger for the judge role by setting `JUDGE_MODEL=llama3.2:7b` in `.env`. Alternatively, use a cloud model if an API key is available.

**BM25 returns empty results.**
`rank-bm25` tokenizes by whitespace. If the corpus contains very short chunks or single-word entries, the BM25 scores for multi-word queries may all be zero. Validate that chunks contain at least 20 words before BM25 indexing.

---

## 8. Engineering Notes

**Embedding model consistency.** `nomic-embed-text` produces 768-dimensional vectors. `mxbai-embed-large` produces 1024-dimensional vectors. Mixing them in the same collection produces incompatible vectors and random retrieval results. The `shared/config.py` stores the embedding model name as collection metadata and validates it on every query. If you change `EMBED_MODEL`, delete `CHROMA_PERSIST_DIR` and rebuild the index.

**PersistentClient vs. in-memory.** These labs use `chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)` so that the index built by `lab-chunking-strategies` persists across Python processes. The persist directory is set via `CHROMA_PERSIST_DIR` in `.env` (default: `./chroma_db`). Each lab run with the same persist dir accumulates collections — delete the directory to start fresh.

**tiktoken tokenizer approximation.** `cl100k_base` (GPT-4 tokenizer family) is used as a close approximation for `llama3.2`'s SentencePiece tokenizer. It may overestimate token count by 5–10% for common English text. This is a safe direction — it results in slightly smaller context blocks, not overflow.

**BM25 index rebuild per run.** `rank-bm25` does not persist to disk. `lab-retrieval-playground` rebuilds the BM25 index from the ChromaDB collection texts on each run. At the corpus sizes used in these labs (< 1 000 chunks), rebuild takes under one second.

**Lab ordering is a design choice, not a constraint.** Labs 3–5 read from the ChromaDB collection built by `lab-chunking-strategies`. This is intentional: it makes the composability of pipeline components explicit. If you want to run later labs independently, rebuild the index by running `lab-chunking-strategies/main.py` first.

**Generation variability.** LLM outputs are non-deterministic. Validation criteria in section 6 are stated as observable patterns (citations present, out-of-scope handling correct) rather than exact string matches. Use `temperature=0.0` in `.env` if you need reproducible outputs for debugging.

---

## 9. Next Steps

After completing all five labs and passing the criteria in `docs/rag/validation.md`:

→ Proceed to [`labs/memory-context/README.md`](../memory-context/README.md)

The memory-context module builds on the non-parametric memory concept introduced here: it adds persistent conversation history, external memory stores, and context management across turns. The retrieval patterns from `lab-retrieval-playground` reappear in `memory-context` as the mechanism for retrieving relevant history entries.

If a lab produces unexpected output, consult the **Failure Modes and Limitations** section of the corresponding topic document before modifying lab code.
