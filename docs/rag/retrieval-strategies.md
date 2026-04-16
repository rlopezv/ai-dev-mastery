---
id: "rag-retrieval-strategies"
title: "Retrieval Strategies"
type: "topic"
step: "rag"
path: "docs/rag/retrieval-strategies.md"
status: "draft"
level: "intermediate"

concepts:
  - "dense-retrieval"
  - "sparse-retrieval"
  - "hybrid-retrieval"
  - "reranking"
  - "reciprocal-rank-fusion"

prerequisites:
  - "docs/rag/embeddings-and-vector-search.md"
  - "docs/rag/document-processing-and-chunking.md"

next:
  - "docs/rag/context-assembly.md"

related:
  - "docs/rag/rag-evaluation-and-metrics.md"

implementation_refs:
  - "labs/rag/lab-retrieval-playground"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains the three retrieval paradigms — dense, sparse, and hybrid — and how reranking improves precision by applying a second-pass relevance model to the top-k candidates."
---

## 1. Intuition

A librarian asked "find me something about database transactions" can search two ways: by subject index (look up "transactions, databases") or by flipping through pages looking for familiar concepts. The subject index is fast and precise for known topics — it misses documents that discuss transactions without using the exact term. Browsing is slower but catches synonyms and related ideas.

Dense retrieval is the semantic browser: it finds meaning regardless of word choice. Sparse retrieval is the subject index: it excels at exact term matches. Hybrid retrieval combines both, recovering what each approach misses.

---

## 2. Explanation

### 2.1 Why

Neither dense nor sparse retrieval is universally better. Dense retrieval (embedding-based) captures semantic similarity but can miss rare technical terms — an acronym or product name that appears once in the training corpus may have a weak or ambiguous embedding. Sparse retrieval (keyword-based) excels at exact term matching but is blind to paraphrase.

In practice, the failure cases of each approach are largely non-overlapping: dense retrieval fails on exact-match queries for rare terms; sparse retrieval fails on paraphrase queries. Combining them increases recall — the probability that the correct document appears in the candidate set — at the cost of requiring two retrieval calls and a merge step.

Reranking then applies a more expensive but more accurate relevance model to the merged candidate set, improving the precision of what ultimately reaches the context assembly step.

### 2.2 How

**Dense retrieval** uses embedding-based vector search as described in `embeddings-and-vector-search.md`. The query and all chunks are encoded as dense vectors; retrieval is a top-k approximate nearest-neighbor query.

**Sparse retrieval** operates over an inverted index of term frequencies. The dominant algorithm is **BM25** (Best Match 25), which scores each document by the weighted sum of TF-IDF scores for query terms, with normalization for document length. BM25 requires no embedding model and is fast for keyword-heavy queries. Libraries such as `rank-bm25` implement BM25 in Python without requiring an external search engine.

**Hybrid retrieval** runs both dense and sparse retrieval, produces two ranked lists, and merges them. The standard merge algorithm is **Reciprocal Rank Fusion (RRF)**:

```
RRF_score(d) = Σ 1 / (k + rank_i(d))
```

where `rank_i(d)` is document d's rank in the i-th list and `k` is a constant (typically 60). RRF does not require scores to be on the same scale, making it robust to the score distribution differences between cosine similarity and BM25.

**Reranking** applies a cross-encoder model to re-score the top-k candidates from retrieval. A cross-encoder receives the query and a candidate chunk together as a single input and produces a relevance score; unlike bi-encoder embedding models, it attends jointly to both texts and captures their interaction. Cross-encoders are significantly more accurate than cosine similarity for relevance scoring but are too slow to run over the entire index — they operate only on the small candidate set from first-pass retrieval.

### 2.3 Code example

```python
# See: labs/rag/lab-retrieval-playground/main.py
# Reciprocal Rank Fusion merge

def rrf_merge(dense_ids: list[str], sparse_ids: list[str],
              k: int = 60) -> list[str]:
    """Merge two ranked lists using RRF."""
    scores: dict[str, float] = {}
    for rank, doc_id in enumerate(dense_ids, start=1):
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    for rank, doc_id in enumerate(sparse_ids, start=1):
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)
```

---

## 3. Table

| Strategy | Representation | Index type | Strengths | Weaknesses |
|----------|---------------|------------|-----------|------------|
| Dense retrieval | Dense vectors (embeddings) | Vector (HNSW/IVF) | Semantic similarity, paraphrase tolerance | Weak on exact terms, rare words |
| Sparse retrieval | Term frequency (BM25) | Inverted index | Exact term matching, fast | Blind to synonyms and paraphrase |
| Hybrid (dense + sparse) | Both | Both | High recall, robust to both failure cases | Two index passes, merge overhead |
| Reranking | Cross-encoder | None (scored on candidates) | High precision, query-chunk interaction | Slow, cannot run on full index |

| Retrieval component | When to add |
|--------------------|-------------|
| Dense only | Baseline for most RAG applications |
| Sparse (BM25) added | Corpus contains technical terms, product names, code |
| Hybrid (RRF) | Recall matters more than latency; production systems |
| Reranking | Top-k precision critical; latency budget allows extra 50–200ms |

---

## 4. Engineering Implications

**First-pass recall determines the ceiling.** Reranking can only improve the ranking of candidates already in the top-k list. If the correct document was not retrieved in the first pass, reranking cannot recover it. Optimizing first-pass recall (through hybrid retrieval or larger top-k) is more impactful than reranking alone.

**BM25 is stateless and fast.** A BM25 index requires no GPU, no embedding model, and no vector database. For applications where the corpus contains many domain-specific terms, adding BM25 alongside dense retrieval costs little operationally and meaningfully improves recall.

**Reranking latency is additive.** A cross-encoder model scoring 20 candidates adds 50–200ms to query latency depending on the model size and hardware. This is often acceptable but must be budgeted explicitly. Online reranking with smaller distilled cross-encoder models (e.g., `ms-marco-MiniLM`) keeps latency manageable.

**RRF is score-scale agnostic.** BM25 scores and cosine similarity scores are not directly comparable — they live on different scales. RRF uses only rank position, not score magnitude, making it stable without calibration.

**top-k must grow with reranking depth.** If the final context window accepts 5 chunks, first-pass retrieval should return 15–25 candidates so the reranker has a meaningful pool to filter. A top-k that is too small defeats the purpose of reranking.

---

## 5. Implementation Connection

`lab-retrieval-playground` demonstrates:

1. Dense retrieval against a ChromaDB collection: observe top-k scores and their distribution.
2. BM25 sparse retrieval on the same corpus using `rank-bm25`: compare which queries it handles better than dense retrieval.
3. Hybrid retrieval with RRF merge: observe how the merged list combines the strengths of both approaches on a query set designed to expose their individual failures.

Run queries that include exact product names or acronyms to observe where dense retrieval fails and BM25 recovers; run paraphrase queries to observe the reverse.

---

## 6. Failure Modes and Limitations

**Score threshold instability.** Cosine similarity scores vary with chunk length and embedding model. A threshold that works for one corpus may silently drop correct results on another. Use top-k selection rather than threshold filtering in the retrieval step; apply threshold filtering as a post-processing gate only when the score distribution is empirically validated.

**RRF amplifies retrieval errors.** RRF gives equal weight to both ranked lists. If one list is completely wrong (dense retrieval fails on all queries in a particular domain), it actively degrades the merged ranking by promoting irrelevant documents. Monitor per-query performance to detect list quality collapse.

**Cross-encoder models are not provider-portable.** Open-weight cross-encoder models are available via Hugging Face's `sentence-transformers` library. Running them locally requires a Python environment with PyTorch, which adds significant dependency weight. In labs, cross-encoder reranking is demonstrated as a concept but the primary implementation uses dense-only retrieval to avoid the PyTorch dependency.

**Large top-k values saturate context budget.** Increasing first-pass top-k to improve reranking quality also increases the number of tokens that must be assembled and potentially truncated. This is not free — it transfers cost from retrieval to context assembly.

---

## 7. Summary

Dense retrieval finds semantically similar content; sparse retrieval (BM25) excels at exact term matches. Hybrid retrieval with Reciprocal Rank Fusion combines both approaches without requiring calibrated scores. Reranking applies a cross-encoder to the candidate set to improve final precision. The key engineering constraint is that first-pass recall is the ceiling: reranking cannot recover documents that retrieval did not surface. In practice, starting with dense-only and adding BM25 hybrid when exact-term recall is poor is the recommended incremental approach.
