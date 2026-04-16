---
id: "rag-readme"
title: "Retrieval-Augmented Generation"
type: "step-readme"
step: "rag"
path: "docs/rag/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "retrieval-augmented-generation"
  - "embedding"
  - "vector-search"
  - "chunking"
  - "context-assembly"

prerequisites:
  - "docs/structured-outputs/README.md"

next:
  - "docs/rag/rag-fundamentals.md"

related:
  - "docs/memory-context/README.md"
  - "docs/ai-agents/README.md"

implementation_refs:
  - "labs/rag/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Covers Retrieval-Augmented Generation — the pattern of retrieving relevant documents from an external knowledge base and injecting them as context before LLM generation, enabling models to answer from up-to-date or private information."
---

## 1. Overview

Language models are trained on fixed corpora. They cannot access information added after training, and they have no knowledge of private or domain-specific data. Retrieval-Augmented Generation (RAG) solves this without retraining: the application retrieves relevant content from an external knowledge base at query time and injects it into the prompt as context. The model's role shifts from recall to reasoning — it reasons over the retrieved content rather than relying on parametric memory.

This step covers the full RAG pipeline: representing text as vectors, storing and searching them, chunking source documents for optimal retrieval, assembling context within token budget, and evaluating retrieval quality.

---

## 2. Scope

**Covered:**
- Embeddings: semantic text representation as dense vectors
- Vector search: similarity search using cosine or dot-product distance over embedding spaces
- Document processing and chunking: splitting source documents into retrievable units
- Retrieval strategies: dense retrieval, sparse retrieval, hybrid retrieval, reranking
- Context assembly: selecting, ordering, and injecting retrieved chunks within token budget
- RAG evaluation: precision, recall, faithfulness, and answer relevance metrics

**Not covered:**
- Agent-driven retrieval loops where the model decides when and what to retrieve (see `ai-agents`)
- Persistent memory and conversation history management (see `memory-context`)
- Evaluation frameworks and automated test pipelines (see `evaluation-testing`)
- Production deployment of vector databases and embedding services (see `deployment-scaling`)

---

## 3. Key Concepts

**Retrieval-Augmented Generation (RAG)**
A pattern that augments a model's prompt with content retrieved from an external knowledge source, enabling the model to produce grounded responses without retraining.

**Embedding**
A dense vector representation of a text segment that encodes semantic meaning, such that semantically similar texts are geometrically close in the embedding space.

**Vector search**
A retrieval mechanism that finds the most semantically similar documents to a query by computing geometric distance between embedding vectors in high-dimensional space.

**Chunking**
The process of splitting source documents into smaller, retrievable segments — balancing the need for focused retrieval units against the risk of losing cross-chunk context.

**Context assembly**
The step where retrieved chunks are selected, deduplicated, ranked, and assembled into a prompt-ready block that fits within the model's token budget.

**RAG evaluation**
A set of metrics — retrieval precision/recall, answer faithfulness, and answer relevance — that measure whether the pipeline retrieves the right content and whether the model uses it correctly.

---

## 4. Concept Map

```
Source documents
       │
       ▼
   Chunking ──────────────────────────────────────────┐
       │                                               │
       ▼                                               ▼
  Embedding model                              Chunk store
       │                                       (vector DB)
       ▼                                               │
  Vector index ◄─────────────────────────────────────┘
       │
       │  (query time)
       ▼
  Query embedding
       │
       ▼
  Vector search ──► Candidate chunks
       │
       ▼
  Reranking (optional)
       │
       ▼
  Context assembly
       │
       ▼
  Prompt + retrieved context
       │
       ▼
     LLM ──► Grounded response
       │
       ▼
  RAG evaluation
```

---

## 5. Learning Flow

| Order | Topic | Dependency |
|-------|-------|------------|
| 1 | `rag-fundamentals.md` | structured-outputs |
| 2 | `embeddings-and-vector-search.md` | rag-fundamentals.md |
| 3 | `document-processing-and-chunking.md` | embeddings-and-vector-search.md |
| 4 | `retrieval-strategies.md` | embeddings-and-vector-search.md |
| 5 | `context-assembly.md` | retrieval-strategies.md, document-processing-and-chunking.md |
| 6 | `rag-evaluation-and-metrics.md` | context-assembly.md |
| 7 | `architecture.md` | all topics |
| 8 | `implementation-reference.md` | architecture.md |
| 9 | `validation.md` | all above |

---

## 6. Documentation Structure

```text
docs/rag/
├── README.md                          ← this file
├── rag-fundamentals.md                ← RAG pattern, motivation, design space
├── embeddings-and-vector-search.md    ← embedding models, vector similarity, indexing
├── document-processing-and-chunking.md ← chunking strategies and trade-offs
├── retrieval-strategies.md            ← dense, sparse, hybrid, reranking
├── context-assembly.md                ← token budgeting, ordering, deduplication
├── rag-evaluation-and-metrics.md      ← retrieval and generation quality metrics
├── architecture.md                    ← system-level view of the full pipeline
├── implementation-reference.md        ← implementation patterns and lab bridge
└── validation.md                      ← completion criteria
```

---

## 7. Labs Overview

| Lab | Type | Purpose |
|-----|------|---------|
| `lab-embeddings` | implementation | Generate embeddings with Ollama's embedding API and measure cosine similarity |
| `lab-chunking-strategies` | implementation | Compare fixed-size, sentence-boundary, and recursive chunking on retrieval quality |
| `lab-retrieval-playground` | implementation | Implement dense retrieval with ChromaDB and observe score distributions |
| `lab-query-pipeline` | implementation | Build the full query pipeline: embed → retrieve → assemble → generate |
| `lab-rag-evaluation` | implementation | Measure retrieval precision/recall and answer faithfulness on a fixed evaluation set |

All five labs are required.

---

## 8. How to Use This Step

**Recommended path:**
1. Read this README.
2. Read `rag-fundamentals.md` (concept-only, no lab).
3. Read `embeddings-and-vector-search.md` and run `lab-embeddings`.
4. Read `document-processing-and-chunking.md` and run `lab-chunking-strategies`.
5. Read `retrieval-strategies.md` and run `lab-retrieval-playground`.
6. Read `context-assembly.md` and run `lab-query-pipeline`.
7. Read `rag-evaluation-and-metrics.md` and run `lab-rag-evaluation`.
8. Read `architecture.md` and `implementation-reference.md`.
9. Complete `validation.md`.

---

## 9. Relationship to Other Steps

| Position | Step | Relationship |
|----------|------|--------------|
| Before | `structured-outputs` | Tool use and schema design underpin how retrieval results are structured and returned |
| After | `memory-context` | Memory extends RAG by persisting retrieved content and conversation history across turns |
| Later dependency | `ai-agents` | Agentic RAG uses the retrieval patterns introduced here as tools within an agent loop |
| Later dependency | `evaluation-testing` | Evaluation frameworks build on the RAG evaluation metrics established in this step |

---

## 10. Next Steps

→ [`docs/rag/rag-fundamentals.md`](./rag-fundamentals.md)
