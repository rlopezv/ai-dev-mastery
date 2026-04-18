---
id: "rag-architecture"
title: "RAG — Architecture"
type: "architecture"
step: "rag"
path: "docs/rag/architecture.md"
status: "draft"
level: "intermediate"

concepts:
  - "document-ingestion-pipeline"
  - "vector-store"
  - "query-pipeline"
  - "context-assembler"
  - "evaluation-harness"

prerequisites:
  - "docs/rag/rag-evaluation-and-metrics.md"
  - "docs/rag/context-assembly.md"

next:
  - "docs/rag/implementation-reference.md"

related:
  - "docs/rag/embeddings-and-vector-search.md"
  - "docs/rag/retrieval-strategies.md"
  - "docs/rag/document-processing-and-chunking.md"

implementation_refs:
  - "labs/rag/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes the components and data flows of a RAG system, covering the offline ingestion pipeline, online query pipeline, and evaluation harness."
---

# RAG — Architecture

## Navigation

[Docs](../README.md) / [Retrieval-Augmented Generation](README.md) / RAG — Architecture

---

## 1. System Overview

A RAG system converts a static corpus of source documents into a queryable knowledge base that augments LLM generation. It solves the problem of LLMs being unable to answer questions about information outside their training data — private corpora, recent events, or domain-specific knowledge.

The system operates in two distinct modes:

**Ingestion mode** (offline) — runs once per corpus or on document update. It loads, chunks, embeds, and indexes all source documents, producing the vector store that retrieval queries against.

**Query mode** (online) — runs on every user request. It embeds the query, retrieves relevant chunks, assembles a context block, and generates a grounded response.

---

## 2. Core Components

| Component | Role | Responsibility |
|-----------|------|----------------|
| Document Loader | Ingestion | Load raw source documents from files, databases, or APIs; extract clean text |
| Chunker | Ingestion | Split clean text into retrievable segments with overlap |
| Embedding Model | Ingestion + Query | Encode text (chunks and queries) as dense vectors |
| Vector Store | Storage | Persist chunk vectors and metadata; serve nearest-neighbor queries |
| BM25 Index | Storage (optional) | Inverted term-frequency index for sparse retrieval |
| Query Embedder | Query | Encode the user query using the same embedding model as ingestion |
| Retriever | Query | Query the vector store (and optionally the BM25 index) for top-k candidates |
| Reranker | Query (optional) | Re-score retrieval candidates using a cross-encoder model |
| Context Assembler | Query | Deduplicate, select, order, and format chunks into a prompt context block |
| LLM | Query | Generate a grounded answer from the assembled context |
| Evaluation Harness | Evaluation | Execute evaluation queries, collect metrics, compare pipeline configurations |

---

## 3. Component Interactions

**Ingestion phase interactions:**

The Document Loader pulls raw content and passes clean text to the Chunker. The Chunker produces a list of (chunk_text, metadata) pairs and passes each to the Embedding Model. The Embedding Model returns a dense vector per chunk. The Vector Store receives (vector, text, metadata) triples and persists them. The BM25 Index, if used, receives the same chunk texts and builds an inverted index.

**Query phase interactions:**

The Query Embedder receives the user query and produces a query vector. The Retriever sends the query vector to the Vector Store to obtain top-k candidates by cosine similarity. If sparse retrieval is enabled, the Retriever also queries the BM25 Index and merges both ranked lists using RRF. The Reranker, if present, receives the merged candidates and rescores them with a cross-encoder. The Context Assembler receives the final ranked list, deduplicates, selects within the token budget, and formats the context block. The LLM receives the system prompt, context block, and user query, and returns the grounded response.

---

## 4. Data Flow

**Ingestion data flow:**

```
Source files (PDF, Markdown, text, HTML)
       │
       ▼ Document Loader
Clean text documents
       │
       ▼ Chunker (recursive split, size=512, overlap=64)
Chunks: [(text, metadata)]
       │
       ├──► Embedding Model ──► Vectors [(id, vector, text, metadata)]
       │                                │
       │                                ▼
       │                          Vector Store (ChromaDB)
       │
       └──► BM25 Index (optional)
```

**Query data flow:**

```
User query (text)
       │
       ▼ Query Embedder
Query vector
       │
       ├──► Vector Store ──► Dense candidates [(id, text, score)]
       │
       └──► BM25 Index ──► Sparse candidates [(id, text, score)]
                                    │
                                    ▼ RRF merge (if hybrid)
                              Merged candidates [(id, text, rrf_score)]
                                    │
                                    ▼ Reranker (optional)
                              Reranked candidates [(id, text, cross_score)]
                                    │
                                    ▼ Context Assembler
                              Context block (within token budget)
                                    │
                                    ▼ Prompt construction
            System prompt + context block + user query
                                    │
                                    ▼ LLM
                              Grounded response (+ citations)
```

---

## 5. Execution Flow

**Ingestion flow:**
1. Load documents from source directory (one call per file or batch).
2. Clean and extract text (format-specific: PDF → pymupdf, Markdown → direct, HTML → BeautifulSoup).
3. Chunk each document. Attach source file path and chunk index as metadata.
4. Embed all chunks. Use batch API calls to minimize round-trip overhead.
5. Insert (vector, text, metadata) triples into the vector store.
6. If BM25 is enabled, persist the inverted index to disk.
7. Record the embedding model name and version in index metadata for consistency validation.

**Query flow:**
1. Validate query: non-empty, within character limit.
2. Embed the query using the model recorded in index metadata.
3. Retrieve top-k candidates from the vector store.
4. If BM25 is enabled, retrieve top-k from the BM25 index and apply RRF.
5. If a reranker is configured, score candidates and sort by cross-encoder score.
6. Deduplicate candidates by cosine similarity between their vectors.
7. Compute token budget. Select chunks in score order until budget is consumed.
8. Format context block: numbered chunks with metadata.
9. Construct full prompt.
10. Call LLM; return response with source chunk references.

---

## 6. Integration Points

**External services:**
- **Ollama** — serves the embedding model (`nomic-embed-text`) and the generation model (`llama3.2`) locally via OpenAI-compatible REST API.
- **ChromaDB** — in-process vector store using HNSW index; no separate server required for development.

**Python libraries:**
- `openai` — embedding API and chat completion via Ollama's OpenAI-compatible endpoint.
- `chromadb` — vector store client.
- `rank-bm25` — BM25 sparse retrieval.
- `tiktoken` — token counting for OpenAI tokenizer family.
- `pypdf` or `pymupdf` — PDF text extraction.

**Lab integration:**
Each lab implements a portion of the pipeline independently, using ChromaDB in-process for storage. `lab-query-pipeline` assembles the full pipeline, consuming the index built by earlier labs.

---

## 7. Trade-offs and Design Decisions

**In-process ChromaDB vs. standalone vector database.** ChromaDB in-process (`:memory:` or local file path) requires no external server, making it the right choice for labs and development. Production deployments typically use standalone vector databases (Qdrant, Weaviate, Pinecone) that support concurrent readers, replication, and large index sizes — but they require an additional infrastructure component.

**Ollama for both embedding and generation.** Using the same local runtime for embedding and generation minimizes setup complexity. The trade-off is that Ollama's embedding model selection is smaller than cloud providers', and model quality differs. For production, dedicated embedding API providers (Cohere, Voyage) typically outperform general-purpose Ollama models.

**Synchronous query pipeline.** The query pipeline in this module executes each step sequentially: embed → retrieve → rerank → assemble → generate. A production pipeline may parallelize the dense and sparse retrieval steps, reducing latency when both indexes are available.

**No streaming in query pipeline.** Generation is not streamed in the lab implementations to keep the code simple and the output measurable. Adding streaming (`stream=True`) to the OpenAI client call is straightforward and has no effect on context assembly or retrieval.

---

## 8. Mapping to Labs

| Component | Lab |
|-----------|-----|
| Embedding model + cosine similarity | `lab-embeddings` |
| Chunker + Vector Store (index build) | `lab-chunking-strategies` |
| Retriever (dense + sparse + hybrid) | `lab-retrieval-playground` |
| Context Assembler + full query pipeline | `lab-query-pipeline` |
| Evaluation Harness | `lab-rag-evaluation` |

---

## 9. Limitations and Boundaries

**Index freshness.** The ingestion pipeline is offline. New or updated documents are not reflected in query results until re-ingestion is complete. Implementing incremental index updates — inserting only new or changed chunks — is possible but out of scope for this module.

**No authentication or access control.** The architecture does not include document-level access permissions. In a multi-tenant deployment, all users can retrieve all indexed content. Access-controlled retrieval requires filtering the vector store query by document permissions, which is a deployment concern addressed in `deployment-scaling`.

**Single embedding model.** The architecture assumes a single embedding model for the entire corpus. Multi-model or multi-language corpora require per-collection models and a routing layer, which increases operational complexity.

**Local scale only.** The ChromaDB in-process store is appropriate for corpora up to approximately 1 million chunks. Larger corpora require a standalone vector database with dedicated hardware, out of scope here.

---

## 10. Summary

The RAG architecture separates concerns into an offline ingestion pipeline and an online query pipeline. Ingestion loads, chunks, embeds, and indexes source documents. Querying embeds the user query, retrieves candidates, optionally reranks, assembles context within token budget, and generates a grounded response. ChromaDB and Ollama are the local runtime components. The five labs implement each major component independently, culminating in the full pipeline in `lab-query-pipeline` and quality measurement in `lab-rag-evaluation`.
