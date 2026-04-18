---
id: "rag-implementation-reference"
title: "RAG — Implementation Reference"
type: "implementation-reference"
step: "rag"
path: "docs/rag/implementation-reference.md"
status: "draft"
level: "intermediate"

concepts:
  - "ingestion-pipeline"
  - "chromadb-collection"
  - "bm25-index"
  - "rrf-merge"
  - "token-budget-guard"

prerequisites:
  - "docs/rag/architecture.md"

next:
  - "docs/rag/validation.md"

related:
  - "docs/rag/retrieval-strategies.md"
  - "docs/rag/context-assembly.md"
  - "docs/rag/embeddings-and-vector-search.md"

implementation_refs:
  - "labs/rag/lab-embeddings"
  - "labs/rag/lab-chunking-strategies"
  - "labs/rag/lab-retrieval-playground"
  - "labs/rag/lab-query-pipeline"
  - "labs/rag/lab-rag-evaluation"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Translates RAG architecture components into concrete implementation patterns for ingestion, retrieval, context assembly, and evaluation, with data structures and execution flows for each lab."
---

# RAG — Implementation Reference

## Navigation

[Docs](../README.md) / [Retrieval-Augmented Generation](README.md) / RAG — Implementation Reference

---

## 1. Implementation Overview

The RAG module implements a two-phase pipeline in Python using Ollama for embeddings and generation and ChromaDB for vector storage. All labs run fully locally — no cloud API keys required for core functionality.

The implementation is split across five labs, each focusing on one pipeline component. A shared `config.py` file provides the Ollama client and ChromaDB collection factory. Labs are designed to be composable: `lab-query-pipeline` reuses the ChromaDB collection built by `lab-chunking-strategies`, and `lab-rag-evaluation` runs the full pipeline from `lab-query-pipeline`.

The key architectural principle is **separation of ingestion from query**. The ingestion pipeline (build index) runs once; the query pipeline (embed → retrieve → assemble → generate) runs on every request. Labs enforce this boundary by separating index-build scripts from query scripts.

---

## 2. Core Implementation Patterns

| Pattern | Description | When to use |
|---------|-------------|-------------|
| Batch embedding | Submit chunks in groups of 64 to the embedding API | Always during ingestion; never embed one chunk at a time |
| Collection-per-strategy | One ChromaDB collection per chunking or retrieval variant | When comparing strategies side-by-side in a lab |
| Embed-on-index, query-at-runtime | Store chunk text and metadata; embed query at query time | Standard RAG pattern |
| RRF merge | Merge dense and BM25 ranked lists by reciprocal rank | When both dense and sparse retrieval are active |
| Token-budget guard | Count tokens before assembling; drop trailing chunks | Always when the corpus is large relative to context window |
| LLM-as-judge | Use a second LLM call to score faithfulness | When evaluation requires semantic quality assessment |

---

## 3. Component Mapping

| Architecture Component | Implementation |
|------------------------|---------------|
| Document Loader | Custom `load_documents(path)` — reads `.txt` and `.md` files from a directory |
| Chunker | `recursive_chunk(text, chunk_size, overlap)` in `lab-chunking-strategies/main.py` |
| Embedding Model | `client.embeddings.create(model="nomic-embed-text", input=texts)` via Ollama |
| Vector Store | `chromadb.Client()` with `get_or_create_collection(name, metadata={"hnsw:space": "cosine"})` |
| BM25 Index | `rank_bm25.BM25Okapi(tokenized_corpus)` from `lab-retrieval-playground/main.py` |
| Query Embedder | Same embedding model as ingestion — enforced by reading model name from collection metadata |
| Retriever | `collection.query(query_embeddings=[qvec], n_results=top_k)` |
| RRF Merge | `rrf_merge(dense_ids, sparse_ids, k=60)` in `lab-retrieval-playground/main.py` |
| Context Assembler | `assemble_context(chunks, query, system_prompt, context_window)` using `tiktoken` |
| LLM | `client.chat.completions.create(model="llama3.2", messages=...)` |
| Evaluation Harness | `evaluate_retrieval(pipeline, eval_set, top_k)` in `lab-rag-evaluation/main.py` |

---

## 4. Data Structures and Interfaces

**Chunk object (internal representation):**
```python
{
    "id": "doc1_chunk_3",          # unique: filename + chunk index
    "text": "The transformer ...", # chunk text
    "metadata": {
        "source": "transformer_paper.md",
        "chunk_index": 3,
        "char_offset": 1024
    }
}
```

**ChromaDB collection schema:**
ChromaDB stores (id, embedding, document, metadata) per entry.
```python
collection.add(
    ids=["doc1_chunk_3"],
    embeddings=[[0.12, -0.34, ...]],     # list of float
    documents=["The transformer ..."],    # raw chunk text
    metadatas=[{"source": "...", "chunk_index": 3}]
)
```

**Retrieval result:**
```python
{
    "ids": [["doc1_chunk_3", "doc2_chunk_7", ...]],
    "documents": [["The transformer ...", "Attention is ...]],
    "distances": [[0.15, 0.21, ...]],     # cosine distance (1 - similarity)
    "metadatas": [[{"source": "..."}, ...]]
}
```

**Evaluation triple:**
```python
{
    "query": "What is the attention mechanism?",
    "relevant_chunk_ids": ["doc1_chunk_3", "doc1_chunk_4"],
    "expected_answer": "Self-attention allows each token to ..."
}
```

**Prompt structure:**
```python
messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful assistant. Answer the question using "
            "only the information in the provided Context. "
            "If the context does not contain the answer, "
            "say 'I don't have enough information to answer that.'"
        )
    },
    {
        "role": "user",
        "content": f"Context:\n{context_block}\n\nQuestion: {query}"
    }
]
```

---

## 5. Execution Flow

**Ingestion execution (run once):**
```
1. load_documents(corpus_dir)
      → list of (filename, full_text)
2. For each document:
   a. recursive_chunk(text, chunk_size=512, overlap=64)
         → list of chunk strings
   b. Attach metadata (source filename, chunk_index) to each chunk
3. Batch-embed all chunks (batch size = 64):
   client.embeddings.create(model="nomic-embed-text",
                            input=batch_of_texts)
4. collection.add(ids, embeddings, documents, metadatas)
5. (Optional) build BM25 index from all chunk texts
6. Print: f"Indexed {n_chunks} chunks from {n_docs} documents."
```

**Query execution (per request):**
```
1. query_vec = embed_single(query)
2. dense_results = collection.query(
       query_embeddings=[query_vec], n_results=top_k)
3. (Optional) sparse_results = bm25.get_top_n(query_tokens, corpus, n=top_k)
4. (Optional) merged = rrf_merge(dense_ids, sparse_ids)
5. (Optional) reranked = cross_encoder.rank(query, candidates)
6. context_block = assemble_context(
       chunks=results, query=query,
       system_prompt=SYSTEM_PROMPT,
       context_window=8192, output_reserve=1024)
7. response = client.chat.completions.create(
       model="llama3.2", messages=build_messages(context_block, query))
8. return response.choices[0].message.content
```

---

## 6. Integration with External Systems

**Ollama** — must be running locally before any lab executes:
```bash
ollama pull nomic-embed-text
ollama pull llama3.2
ollama serve   # already running if Ollama Desktop is installed
```

The embedding endpoint: `POST http://localhost:11434/v1/embeddings`
The chat endpoint: `POST http://localhost:11434/v1/chat/completions`
Both are accessed via the OpenAI Python client with `base_url="http://localhost:11434/v1"`.

**ChromaDB** — instantiated in-process:
```python
import chromadb
client = chromadb.Client()  # in-memory
# or
client = chromadb.PersistentClient(path="./chroma_db")  # persisted to disk
```

Persistent storage is required across labs that build an index in one script and query it in another (e.g., `lab-query-pipeline` reading the index built by `lab-chunking-strategies`).

**tiktoken** — used for token counting:
```python
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")  # compatible with llama-class models
token_count = len(enc.encode(text))
```

---

## 7. Mapping to Labs

| Pattern / Component | Lab |
|--------------------|-----|
| Embedding API, cosine similarity, batch embedding | `lab-embeddings` |
| Document loader, recursive chunker, ChromaDB ingestion | `lab-chunking-strategies` |
| Dense retrieval, BM25 sparse retrieval, RRF merge | `lab-retrieval-playground` |
| Full query pipeline, token budget guard, prompt assembly | `lab-query-pipeline` |
| Evaluation dataset, Precision@k, Recall@k, LLM-as-judge | `lab-rag-evaluation` |

---

## 8. Trade-offs and Constraints

**nomic-embed-text vs. mxbai-embed-large.** `nomic-embed-text` (768 dimensions) is faster and has a smaller memory footprint. `mxbai-embed-large` (1024 dimensions) produces higher-quality vectors, particularly for long documents. Labs default to `nomic-embed-text` for speed; `mxbai-embed-large` is available as an environment variable override.

**in-memory vs. persistent ChromaDB.** In-memory ChromaDB is destroyed when the Python process exits. Labs that write an index in one script and read it in another must use `PersistentClient`. The `.env.example` includes a `CHROMA_PERSIST_DIR` variable.

**tiktoken tokenizer approximation.** `cl100k_base` (the GPT-4 tokenizer) is used as a close approximation for llama3.2's tokenizer. Llama 3 uses a SentencePiece tokenizer that differs slightly; `cl100k_base` may overestimate token count by 5–10% for common English text. This is a safe direction: it results in slightly smaller context blocks, not overflow.

**BM25 index not persisted.** The `rank-bm25` library does not persist the index to disk. Each lab run rebuilds the BM25 index from the chunk texts, which takes under one second for corpora under 10,000 chunks.

---

## 9. Failure Modes

**Model name mismatch between ingestion and query.** Using `nomic-embed-text` at ingestion time and `mxbai-embed-large` at query time produces incompatible vectors and returns random chunks. The ingestion script stores the embedding model name in the ChromaDB collection metadata. The query script reads it and validates before querying.

**ChromaDB collection not found.** If `lab-query-pipeline` runs before `lab-chunking-strategies` has built the index, ChromaDB returns an empty collection and all retrieval returns zero results. Labs print a clear error and exit if the expected collection does not exist.

**tiktoken encoding mismatch.** If the system prompt, context block, and query are counted separately and summed without accounting for message-formatting tokens (role labels, separators), the actual token count sent to the API may exceed the calculated budget by 20–50 tokens. Add a 100-token overhead to the budget calculation to absorb formatting overhead.

**Empty retrieval result.** When the query vector is far from all indexed vectors (e.g., out-of-domain query), ChromaDB returns the top-k "closest" chunks but all have very low similarity (< 0.4). The context assembler should check the highest score and return a no-information response rather than assembling low-quality context.

---

## 10. Summary

The RAG implementation uses Ollama for local embedding and generation, ChromaDB for vector storage, and `rank-bm25` for sparse retrieval. The pipeline splits cleanly into an offline ingestion phase and an online query phase, each implemented as separate scripts. The token budget guard uses `tiktoken` to stay within the context window. Labs are composable: earlier labs build index artifacts consumed by later labs, culminating in `lab-query-pipeline` for end-to-end pipeline execution and `lab-rag-evaluation` for quality measurement.
