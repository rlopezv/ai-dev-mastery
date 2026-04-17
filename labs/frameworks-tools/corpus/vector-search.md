# Vector Search

Vector search finds stored items that are semantically similar to a query by computing
geometric distance between embedding vectors. Unlike keyword search, which matches
exact terms, vector search captures meaning: the query "fast nearest-neighbor lookup"
retrieves documents about HNSW even if the words "fast" and "lookup" do not appear in them.

## Embeddings

An embedding model maps text to a dense vector in a high-dimensional space (typically
384 to 3072 dimensions). Semantically similar texts map to geometrically close vectors.
The distance between two vectors — measured by cosine similarity or Euclidean distance —
is an approximation of semantic similarity.

Cosine similarity is preferred for text embeddings because it is invariant to vector
magnitude. Two vectors pointing in the same direction have cosine similarity 1.0
regardless of length. Euclidean distance conflates direction with magnitude and is
sensitive to text length differences.

## Approximate Nearest-Neighbor Search

Exact nearest-neighbor search over a large vector index requires computing the distance
from the query vector to every stored vector — O(n × d) operations where n is the index
size and d is the embedding dimension. At n = 10 million and d = 1536, this is
approximately 15 billion floating-point operations per query. Exact search is infeasible
at this scale.

Approximate nearest-neighbor (ANN) algorithms trade a small loss in recall for a
large reduction in query latency. They build data structures at index time that allow
sublinear-time traversal at query time.

## HNSW

Hierarchical Navigable Small World (HNSW) is the dominant ANN algorithm in production
vector databases. It builds a multi-layer graph where:

- The top layer contains a small subset of nodes with long-range connections.
- Lower layers contain progressively more nodes with progressively shorter connections.
- The bottom layer contains all nodes.

A query traverses the graph top-down: it enters at the top layer, greedy-walks toward
the query vector, then descends to the next layer and continues. This mimics navigating
a road network — start on highways (few exits, long distances), then descend to local
streets (many exits, short distances).

HNSW parameters:
- `M` — the number of bidirectional connections per node. Higher M improves recall but
  increases memory. Typical range: 8 to 64.
- `ef_construction` — the beam width during index construction. Higher values improve
  graph quality at the cost of build time.
- `ef_search` — the beam width during query traversal. Higher values improve recall at
  the cost of query latency. Can be tuned at query time without rebuilding the index.

HNSW achieves recall > 0.99 at queries-per-second rates that exact search cannot match.
Memory cost is O(n × M) vectors plus the graph adjacency lists.

## IVF (Inverted File Index)

IVF partitions the vector space into Voronoi cells via k-means clustering. At index time,
each vector is assigned to its nearest centroid and stored in that cell's posting list.
At query time, the query vector is compared to all centroids, and only the vectors in the
top `nprobe` cells are examined.

IVF is memory-efficient for very large indexes (hundreds of millions of vectors) because
centroid comparison is cheap. Its weakness is that vectors near cell boundaries may be
assigned to the wrong cell and missed at query time. Increasing `nprobe` recovers recall
at the cost of examining more cells.

## Product Quantization

Product quantization (PQ) compresses vectors to reduce memory usage. Each vector is split
into M sub-vectors, and each sub-vector is quantized to one of 256 centroids (8-bit code).
A 1536-dimensional float32 vector (6144 bytes) compresses to 96 bytes with PQ(M=96),
a 64× reduction.

PQ is commonly combined with IVF (IVF-PQ) for indexes that do not fit in RAM. The
accuracy loss from quantization is bounded by the quantization error, which decreases
as M increases.

## Filtering

Metadata filtering restricts the search to a subset of vectors that match a predicate
(e.g., `source = "product_manual.pdf"` or `date > 2024-01-01`). Vector databases
implement filtering in two ways:

- Pre-filtering: apply the metadata filter before ANN traversal, then search within the
  filtered set. Exact but expensive for small filter selectivity.
- Post-filtering: run ANN search over the full index, then discard results that fail
  the metadata predicate. Fast but requires over-fetching to compensate for discarded results.

ChromaDB uses post-filtering by default. Pinecone and Weaviate support both modes.

## Distance Metrics

| Metric | Formula | When to use |
|--------|---------|-------------|
| Cosine similarity | dot(a,b) / (|a| × |b|) | Text embeddings; length-invariant |
| Euclidean (L2) | sqrt(sum((a_i - b_i)²)) | Image embeddings; magnitude matters |
| Dot product | sum(a_i × b_i) | Pre-normalized vectors; fastest to compute |
| Manhattan (L1) | sum(|a_i - b_i|) | Sparse vectors; outlier-resistant |

Most embedding models produce L2-normalized vectors (unit norm). For these, cosine
similarity and dot product are equivalent and can be computed with a single BLAS call.
