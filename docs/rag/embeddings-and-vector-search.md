---
id: "rag-embeddings-and-vector-search"
title: "Embeddings and Vector Search"
type: "topic"
step: "rag"
path: "docs/rag/embeddings-and-vector-search.md"
status: "draft"
level: "intermediate"

concepts:
  - "embedding"
  - "vector-search"
  - "cosine-similarity"
  - "embedding-model"
  - "vector-index"

prerequisites:
  - "docs/rag/rag-fundamentals.md"

next:
  - "docs/rag/document-processing-and-chunking.md"

related:
  - "docs/rag/retrieval-strategies.md"

implementation_refs:
  - "labs/rag/lab-embeddings"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how embedding models encode text as dense vectors, how cosine similarity measures semantic proximity, and how vector indexes enable efficient nearest-neighbor retrieval at scale."
---

# Embeddings and Vector Search

## Navigation

[Docs](../README.md) / [Retrieval-Augmented Generation](README.md) / Embeddings and Vector Search

---

## 1. Intuition

Search engines have traditionally matched documents by keyword overlap: a query for "large language model" finds documents containing those exact words. This fails when the document uses synonyms ("foundation model", "transformer-based system") or describes the concept without naming it. Embeddings solve this by mapping text into a geometric space where semantic similarity becomes spatial proximity — texts that mean similar things end up close together, regardless of the words used.

A vector search is then a nearest-neighbor problem: given the query's position in the space, find the stored documents that are geometrically closest.

---

## 2. Explanation

### 2.1 Why

Keyword search cannot capture synonymy, paraphrase, or conceptual proximity. Two texts that express the same idea with different words have zero lexical overlap and would receive a score of zero in a BM25 ranking. For retrieval-augmented generation, this is a critical failure: the correct answer exists in the store, but the retrieval step cannot find it.

Embedding-based retrieval separates meaning from surface form. The embedding model learns from a large corpus that "car", "automobile", and "vehicle" occupy nearby regions of the vector space — so a query for "car rental" can retrieve documents that only use the word "automobile." This semantic alignment is the property that makes embeddings useful for RAG.

### 2.2 How

**Embedding models** are neural networks trained to map text to dense vectors. The embedding is the activation of the model's last hidden layer (or a pooled version of it). The OpenAI `text-embedding-ada-002` model produces 1536-dimensional vectors. Ollama serves open-weight embedding models such as `nomic-embed-text` (768 dimensions) and `mxbai-embed-large` (1024 dimensions) locally.

**Cosine similarity** measures the angle between two vectors, ignoring their magnitude. For normalized vectors it equals the dot product:

```
cosine_similarity(a, b) = (a · b) / (|a| × |b|)
```

Values range from -1 (opposite meaning) to 1 (identical direction). In practice, RAG similarity scores cluster between 0.6 and 0.95 for relevant matches; anything below 0.5 is typically noise.

**Vector indexes** store embedding vectors and support fast approximate nearest-neighbor (ANN) queries. Exact nearest-neighbor search is O(n) — it compares the query against every stored vector. ANN algorithms (HNSW, IVF) trade a small accuracy loss for sub-linear query time by building a graph or cluster index over the vectors.

ChromaDB, the vector store used in this module's labs, supports in-process storage (no separate server) and integrates an HNSW index for cosine similarity search.

**Indexing a document collection:**
1. For each chunk, call the embedding model's API with the chunk text.
2. Store the returned vector alongside the chunk's text and metadata (source file, chunk index, etc.) in the vector database.

**Querying:**
1. Encode the user query with the same embedding model.
2. Call the vector database's similarity search with the query vector and `top_k`.
3. The database returns the top-k stored vectors by cosine similarity, along with their associated text and metadata.

### 2.3 Code example

```python
# See: labs/rag/lab-embeddings/main.py
from openai import OpenAI
import numpy as np

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
EMBED_MODEL = "nomic-embed-text"

def embed(text: str) -> list[float]:
    response = client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding

def cosine_similarity(a: list[float], b: list[float]) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

query_vec   = embed("How do transformers process text?")
doc_vec     = embed("The transformer architecture uses self-attention layers.")
unrelated   = embed("The weather in Madrid is sunny today.")

print(cosine_similarity(query_vec, doc_vec))   # ~0.85
print(cosine_similarity(query_vec, unrelated)) # ~0.45
```

---

## 3. Table

| Embedding model | Dimensions | Provider | Local | Notes |
|----------------|------------|----------|-------|-------|
| `text-embedding-ada-002` | 1536 | OpenAI | No | Widely used baseline |
| `text-embedding-3-small` | 1536 | OpenAI | No | Cheaper than ada-002 |
| `nomic-embed-text` | 768 | Ollama | Yes | Good quality, fast |
| `mxbai-embed-large` | 1024 | Ollama | Yes | Higher quality, slower |
| `all-minilm-l6-v2` | 384 | Ollama | Yes | Very fast, lower quality |

| Similarity metric | Formula | Range | Use case |
|------------------|---------|-------|----------|
| Cosine similarity | dot(a,b)/(|a||b|) | -1 to 1 | Standard for normalized embeddings |
| Dot product | a·b | unbounded | Faster when vectors are pre-normalized |
| Euclidean distance | √Σ(aᵢ-bᵢ)² | 0 to ∞ | Less common in NLP retrieval |

| Vector index type | Query complexity | Accuracy | When to use |
|------------------|-----------------|----------|-------------|
| Flat (exact) | O(n) | 100% | Small collections (<100k vectors) |
| HNSW | O(log n) | ~99% | General purpose, ChromaDB default |
| IVF | O(√n) | ~95% | Very large collections (>1M vectors) |

---

## 4. Engineering Implications

**Model consistency is mandatory.** Vectors produced by different embedding models occupy incompatible spaces. If the embedding model changes after indexing, every stored vector is invalidated and the index must be rebuilt from scratch.

**Dimensionality affects storage and latency.** A 1536-dimensional float32 vector occupies 6 KB. One million such vectors require 6 GB of storage. Higher-dimensional models cost more to store and are slower to index and query. For local development, 768-dimensional models are a practical compromise.

**Cosine similarity does not imply relevance.** Two texts can be geometrically close in the embedding space but contextually unrelated for a specific query. Embedding similarity is a proxy for relevance, not a guarantee. Reranking (a second-pass relevance model applied to the top-k results) can improve precision at the cost of additional latency.

**Batch embedding is significantly faster.** Embedding APIs accept arrays of inputs. Submitting chunks in batches of 64 or 128 instead of one at a time reduces indexing time by 10–50x by amortizing API round-trip overhead.

**Normalization affects score comparability.** Cosine similarity scores are comparable across queries only when all stored vectors are normalized to unit length. Some embedding models return normalized vectors; others do not. Normalize explicitly if comparability is required.

---

## 5. Implementation Connection

`lab-embeddings` demonstrates:

1. Embedding single texts with Ollama's embedding API and inspecting the returned vector shape.
2. Computing cosine similarity between a query and a set of candidate texts — observing that semantically related texts score higher than unrelated ones.
3. Batch embedding a small document collection and searching it for a query using sorted cosine similarity.

The lab uses `nomic-embed-text` via Ollama so no external API key is required. Run it after this topic to build intuition for the score distributions that determine retrieval quality.

---

## 6. Failure Modes and Limitations

**Semantic gap for specialized domains.** General-purpose embedding models may not capture the semantic structure of highly specialized domains (legal, medical, financial). A query using domain-specific terminology may not be geometrically close to the correct document if the model was not trained on that vocabulary.

**Short text degradation.** Embedding models trained on full paragraphs produce lower-quality vectors for very short chunks (fewer than 20 tokens). The resulting vectors have high variance and produce noisy similarity scores. Minimum chunk size should be empirically validated against retrieval quality.

**Cross-lingual gaps.** Most embedding models are English-centric. Cross-lingual retrieval requires explicitly multilingual models. Mixing languages in the same index without a multilingual model degrades retrieval quality across language boundaries.

**False negatives from threshold filtering.** Applying a hard similarity threshold to filter results (e.g., only return chunks with similarity ≥ 0.75) can silently drop the best available answer when all scores fall below the threshold. Use threshold filtering as a quality gate, not as a replacement for top-k selection.

---

## 7. Summary

Embedding models map text to dense vectors in a space where semantic proximity corresponds to geometric proximity. Cosine similarity measures the angle between vectors, enabling ranking of stored documents by their relevance to a query vector. Vector indexes support efficient approximate nearest-neighbor search over large collections. The fundamental constraint is model consistency: all vectors in an index must be produced by the same model, and changing the model requires a full re-index.
