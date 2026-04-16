# Lab: lab-retrieval-playground
# Module: rag
# Doc reference: docs/rag/retrieval-strategies.md

import logging
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import (
    EMBED_MODEL,
    assert_ollama_ready,
    build_chroma_client,
    build_client,
    embed,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COLLECTION_NAME = "chunks_recursive"   # built by lab-chunking-strategies
TOP_K = 5

# Query set designed to expose the failure cases of each strategy.
# Paraphrase queries favour dense retrieval; exact-term queries favour BM25.
QUERIES = [
    {
        "text": "How does cosine similarity measure semantic proximity?",
        "type": "semantic",
        "note": "Paraphrase query — dense retrieval should rank text-embeddings.md first",
    },
    {
        "text": "How does the model know the order of words in the input?",
        "type": "semantic",
        "note": "Paraphrase of 'positional encoding' — dense should find it without exact words",
    },
    {
        "text": "BM25 saturation function",
        "type": "exact-term",
        "note": "Rare technical phrase — dense retrieval struggles; BM25 finds it directly",
    },
    {
        "text": "RoPE rotary position embedding",
        "type": "exact-term",
        "note": "Acronym + exact term — BM25 should outrank dense on this query",
    },
    {
        "text": "What happens to a model's general capabilities after heavy fine-tuning?",
        "type": "semantic",
        "note": "Paraphrase of 'catastrophic forgetting' — dense should retrieve it",
    },
]


# ---------------------------------------------------------------------------
# BM25 sparse retrieval
# ---------------------------------------------------------------------------

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In bm25_retrieve(), remove .lower() from the query tokenization:
#   change bm25.get_scores(query.lower().split()) to bm25.get_scores(query.split())
# - Observe:
#   * BM25 fails on mixed-case queries — query tokens no longer match the lowercased corpus
#   * exact-term queries that ranked first now score near 0
#   * the ✓ BM25 outranked dense on ... validation check flips to ✗
#   * RRF hybrid also degrades for exact-term queries because the BM25 signal collapses

def build_bm25_index(chroma_client) -> tuple:
    """
    Load all chunks from the ChromaDB collection and build a BM25 index.
    Returns (bm25_model, corpus_chunks) where corpus_chunks is the ordered
    list of chunk dicts used to map BM25 results back to source metadata.

    Concept: sparse-retrieval — inverted index over tokenised chunk texts
    """
    try:
        from rank_bm25 import BM25Okapi  # noqa: PLC0415
    except ImportError:
        log.error("rank-bm25 not installed. Run: pip install rank-bm25>=0.2.2")
        sys.exit(1)

    collection = chroma_client.get_collection(COLLECTION_NAME)
    # Fetch all chunks — ChromaDB returns everything when limit is very large
    results = collection.get(include=["documents", "metadatas"])

    corpus_chunks = [
        {"id": id_, "text": doc, "metadata": meta}
        for id_, doc, meta in zip(
            results["ids"], results["documents"], results["metadatas"]
        )
    ]

    # Concept: BM25 tokenises on whitespace — sufficient for English prose
    tokenised = [chunk["text"].lower().split() for chunk in corpus_chunks]
    bm25 = BM25Okapi(tokenised)
    log.info("BM25 index built over %d chunks", len(corpus_chunks))
    return bm25, corpus_chunks


def bm25_retrieve(bm25, corpus_chunks: list[dict],
                  query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Retrieve top-k chunks from the BM25 index for a query.
    Returns list of dicts with 'chunk' and 'score' keys, sorted by score.
    """
    # Concept: sparse-retrieval — scores by weighted term frequency
    scores = bm25.get_scores(query.lower().split())
    ranked_indices = sorted(
        range(len(scores)), key=lambda i: scores[i], reverse=True
    )[:top_k]
    return [
        {"chunk": corpus_chunks[i], "score": float(scores[i])}
        for i in ranked_indices
    ]


# ---------------------------------------------------------------------------
# Dense retrieval
# ---------------------------------------------------------------------------

def dense_retrieve(chroma_client, client, query: str,
                   top_k: int = TOP_K) -> list[dict]:
    """
    Retrieve top-k chunks from ChromaDB using embedding-based vector search.

    Concept: dense-retrieval — nearest-neighbour search over embedding vectors
    """
    collection = chroma_client.get_collection(COLLECTION_NAME)
    # Concept: embedding-model — query encoded with the same model as the index
    query_vec = embed(client, query)
    results = collection.query(
        query_embeddings=[query_vec],
        n_results=top_k,
        include=["documents", "distances", "metadatas"],
    )
    return [
        {
            "chunk": {
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
            },
            # ChromaDB returns cosine distance (1 - similarity)
            "similarity": round(1.0 - results["distances"][0][i], 4),
        }
        for i in range(len(results["ids"][0]))
    ]


# ---------------------------------------------------------------------------
# Hybrid: Reciprocal Rank Fusion
# ---------------------------------------------------------------------------

def rrf_merge(dense_results: list[dict], sparse_results: list[dict],
              k: int = 60) -> list[dict]:
    """
    Merge dense and BM25 ranked lists using Reciprocal Rank Fusion.

    Concept: reciprocal-rank-fusion — uses rank position, not raw scores,
    making the merge robust to scale differences between retrieval systems.
    """
    scores: dict[str, float] = {}
    chunk_by_id: dict[str, dict] = {}

    for rank, item in enumerate(dense_results, start=1):
        cid = item["chunk"]["id"]
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
        chunk_by_id[cid] = item["chunk"]

    for rank, item in enumerate(sparse_results, start=1):
        cid = item["chunk"]["id"]
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
        chunk_by_id[cid] = item["chunk"]

    ranked_ids = sorted(scores, key=scores.__getitem__, reverse=True)
    return [
        {"chunk": chunk_by_id[cid], "rrf_score": round(scores[cid], 6)}
        for cid in ranked_ids[:TOP_K]
    ]


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_dense(results: list[dict], query: str) -> None:
    for i, r in enumerate(results, 1):
        source = r["chunk"]["metadata"].get("source", "?")
        preview = r["chunk"]["text"][:65].replace("\n", " ") + "..."
        print(f"  #{i} sim={r['similarity']:.4f}  {source:<30} \"{preview}\"")


def print_sparse(results: list[dict]) -> None:
    for i, r in enumerate(results, 1):
        source = r["chunk"]["metadata"].get("source", "?")
        preview = r["chunk"]["text"][:65].replace("\n", " ") + "..."
        print(f"  #{i} score={r['score']:.2f}  {source:<30} \"{preview}\"")


def print_hybrid(results: list[dict]) -> None:
    for i, r in enumerate(results, 1):
        source = r["chunk"]["metadata"].get("source", "?")
        preview = r["chunk"]["text"][:65].replace("\n", " ") + "..."
        print(f"  #{i} rrf={r['rrf_score']:.4f}  {source:<30} \"{preview}\"")


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def top_source(results: list[dict], source_key: str = "source") -> str:
    """Return the source filename of the top-ranked result."""
    if not results:
        return ""
    meta = results[0].get("chunk", {}).get("metadata", {})
    return meta.get(source_key, "")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    assert_ollama_ready(models=[EMBED_MODEL])

    client = build_client()
    chroma = build_chroma_client()

    # Validate that the required collection exists
    try:
        chroma.get_collection(COLLECTION_NAME)
    except Exception:
        log.error(
            "Collection '%s' not found. Run lab-chunking-strategies first: "
            "python lab-chunking-strategies/main.py",
            COLLECTION_NAME,
        )
        sys.exit(1)

    # Build BM25 index from the same collection
    bm25, corpus_chunks = build_bm25_index(chroma)

    dense_beats_bm25_count = 0
    bm25_beats_dense_count = 0

    for query_def in QUERIES:
        query = query_def["text"]
        qtype = query_def["type"]
        note  = query_def["note"]

        print(f"\n{'='*60}")
        print(f"Query [{qtype}]: \"{query}\"")
        print(f"Note: {note}")

        # --- Dense retrieval ---
        print("\n  Dense retrieval:")
        dense = dense_retrieve(chroma, client, query)
        print_dense(dense, query)

        # --- BM25 sparse retrieval ---
        print("\n  BM25 sparse retrieval:")
        sparse = bm25_retrieve(bm25, corpus_chunks, query)
        print_sparse(sparse)

        # --- Hybrid RRF ---
        print("\n  Hybrid RRF merge:")
        hybrid = rrf_merge(dense, sparse)
        print_hybrid(hybrid)

        # Track which strategy wins top-1 for validation
        dense_top_sim  = dense[0]["similarity"] if dense else 0.0
        sparse_top_src = top_source(sparse)
        dense_top_src  = top_source(dense)

        if qtype == "exact-term":
            # Expect BM25 top-1 source to appear higher in sparse than dense
            dense_rank = next(
                (i for i, r in enumerate(dense)
                 if r["chunk"]["metadata"].get("source") == sparse_top_src),
                TOP_K,
            )
            sparse_rank = 0  # BM25 top-1 is always rank 0 in sparse list
            if sparse_rank < dense_rank:
                bm25_beats_dense_count += 1
        elif qtype == "semantic":
            # Expect dense top-1 similarity above a meaningful threshold
            if dense_top_sim >= 0.70:
                dense_beats_bm25_count += 1

    # --- Validation summary ---
    print(f"\n{'='*60}")
    print("=== Validation ===")
    if bm25_beats_dense_count > 0:
        print(
            f"✓ BM25 outranked dense on {bm25_beats_dense_count} exact-term "
            f"quer{'y' if bm25_beats_dense_count == 1 else 'ies'}"
        )
    else:
        print(
            "✗ BM25 did not outrank dense on any exact-term query. "
            "Try queries with rarer technical terms."
        )

    if dense_beats_bm25_count > 0:
        print(
            f"✓ Dense retrieval returned high-similarity results (≥0.70) on "
            f"{dense_beats_bm25_count} semantic quer"
            f"{'y' if dense_beats_bm25_count == 1 else 'ies'}"
        )

    print("\nDone. Proceed to lab-query-pipeline.")


if __name__ == "__main__":
    main()
