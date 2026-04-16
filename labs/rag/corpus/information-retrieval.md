# Information Retrieval

Finding the right document in a large collection is harder than it looks. A user rarely types the exact words that appear in the answer. They describe what they are looking for, and the retrieval system has to figure out which documents are relevant. Getting this right is the core challenge of information retrieval — and it matters enormously in RAG, where the quality of what you retrieve directly determines the quality of what the model can generate.

## Keyword Search: BM25

**BM25** (Best Match 25) has been the dominant retrieval algorithm for decades. It scores each document by a weighted sum of term-frequency and inverse-document-frequency (TF-IDF) values for each query term. Two refinements make it more accurate than raw TF-IDF: a **saturation function** that gives diminishing returns to repeated occurrences of the same term (so a document that mentions "attention" twenty times is not ranked twenty times higher than one that mentions it once), and **document length normalisation** that prevents long documents from winning simply by having more words.

BM25 operates on an inverted index: a data structure that maps each term to the list of documents containing it, with term frequency stored alongside. Queries run by looking up each query term in the index, scoring the matching documents, and ranking by total score. This makes BM25 fast and memory-efficient even for very large corpora.

Its fundamental weakness is vocabulary mismatch: a query for "car" does not match documents that use only the word "automobile", because BM25 sees no token overlap between them.

## Semantic Search: Dense Retrieval

Dense retrieval solves vocabulary mismatch by encoding both the query and every document chunk as embedding vectors and finding the geometrically closest vectors using approximate nearest-neighbour search. Because the embedding space encodes meaning rather than tokens, "car" and "automobile" end up nearby, and a query for one retrieves documents that use the other.

The cost is that every document must be embedded using a neural network before indexing, and the index requires an approximate search structure — typically **HNSW** (Hierarchical Navigable Small World) for general use, or **IVF** (Inverted File Index) for very large collections. HNSW builds a multi-layer proximity graph that supports sub-linear query time with recall above 99% in typical configurations.

## Hybrid Retrieval

Neither approach is universally better. Dense retrieval struggles with rare technical terms — a product serial number or a proprietary API method name may not appear in the embedding model's training data and will have a weak, unreliable vector. BM25 misses paraphrase and synonymy entirely. Hybrid retrieval runs both pipelines and merges the two ranked lists.

**Reciprocal Rank Fusion (RRF)** is the standard merge algorithm:

```
RRF_score(d) = Σ 1 / (k + rank_i(d))
```

where `rank_i(d)` is the position of document d in the i-th ranked list and k is a constant, typically 60. Because RRF uses only rank position — not the raw BM25 or cosine scores — it is robust to the scale differences between the two systems and requires no calibration.

## Reranking

After first-pass retrieval returns a candidate set of 20–50 documents, a **cross-encoder reranker** can improve the final ranking. Unlike the bi-encoder models used for embedding — which score query and document independently and then compare vectors — a cross-encoder receives query and candidate concatenated as a single input and scores their relevance jointly. This captures fine-grained interaction between query and document that a simple vector distance cannot. Cross-encoders are more accurate but roughly 50–200ms slower per query and cannot run over an entire index.

## Measuring Retrieval Quality

Retrieval quality is measured with a labelled evaluation set: for each query, the set of relevant documents must be known in advance. The primary metrics are:

- **Precision@k** — what fraction of the top-k retrieved documents are relevant. Measures result quality.
- **Recall@k** — what fraction of all relevant documents appear in the top k. Measures coverage.
- **MRR (Mean Reciprocal Rank)** — the mean of `1/rank` where rank is the position of the first relevant result. Rewards systems that surface the correct answer near the top of the list.
