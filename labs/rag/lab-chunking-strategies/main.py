# Lab: lab-chunking-strategies
# Module: rag
# Doc reference: docs/rag/document-processing-and-chunking.md

import logging
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import (
    EMBED_MODEL,
    assert_ollama_ready,
    build_chroma_client,
    build_client,
    embed_batch,
    load_corpus,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CORPUS_DIR = pathlib.Path(__file__).parent.parent / "corpus"

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - Change CHUNK_SIZE = 512 to CHUNK_SIZE = 100
# - Observe:
#   * chunk count spikes — many small fragments per document
#   * avg chunk length drops to ~90-100 chars; most chunks contain an incomplete thought
#   * top-1 similarity falls for paragraph-spanning queries (passage is split)
#   * the ✓ recursive top-1 ≥ fixed top-1 check may flip to ✗
CHUNK_SIZE = 512      # target size in characters
CHUNK_OVERLAP = 64    # overlap between consecutive chunks in characters

# Collection names — used by lab-retrieval-playground, lab-query-pipeline,
# and lab-rag-evaluation. Do not rename without updating those labs.
COLLECTION_FIXED = "chunks_fixed"
COLLECTION_SENTENCE = "chunks_sentence"
COLLECTION_RECURSIVE = "chunks_recursive"

# Queries used for the comparison — chosen to expose strategy differences:
# first query spans a paragraph boundary; second fits in a single sentence
COMPARISON_QUERIES = [
    "How does the KV cache reduce inference cost from O(n²) to O(n)?",
    "What is the difference between top-k and top-p sampling?",
]


# ---------------------------------------------------------------------------
# Chunking strategies
# ---------------------------------------------------------------------------

def chunk_fixed(text: str, size: int = CHUNK_SIZE,
                overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Fixed-size chunking: split at a hard character boundary with overlap.

    Concept: chunk-size — fixed granularity regardless of sentence structure.
    Simple and predictable, but cuts mid-sentence on boundary tokens.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        start += size - overlap
    return chunks


def chunk_sentence(text: str, target: int = CHUNK_SIZE) -> list[str]:
    """
    Sentence-boundary chunking: accumulate sentences until the target size
    is reached, then start a new chunk.

    Concept: chunk-size — respects sentence endings, producing syntactically
    complete units at the cost of variable chunk length.
    """
    # Concept: document-loader — sentence splitting on ". " preserves prose flow
    raw_sentences = []
    for part in text.split(". "):
        part = part.strip()
        if part:
            raw_sentences.append(part if part.endswith(".") else part + ".")

    chunks: list[str] = []
    current = ""
    for sentence in raw_sentences:
        candidate = (current + " " + sentence).strip() if current else sentence
        if len(candidate) <= target:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks


def chunk_recursive(text: str, size: int = CHUNK_SIZE,
                    overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Recursive character chunking: try to split on paragraph boundaries first,
    then sentence endings, then word boundaries.

    Concept: recursive-chunking — uses the coarsest delimiter that keeps
    chunks within the target size, preserving natural text structure.
    """
    # Concept: chunk-overlap — carry the tail of each chunk into the next
    # to prevent relevant sentences at boundaries from being cut in half
    separators = ["\n\n", "\n", ". ", " "]

    def _split(t: str, seps: list[str]) -> list[str]:
        if not seps or len(t) <= size:
            return [t] if t.strip() else []
        sep = seps[0]
        parts = [p for p in t.split(sep) if p.strip()]
        # If all parts already fit, no need to recurse further
        if all(len(p) <= size for p in parts):
            return parts
        # Some parts are still too large — recurse with next separator
        result = []
        for part in parts:
            if len(part) <= size:
                result.append(part)
            else:
                result.extend(_split(part, seps[1:]))
        return result

    fragments = _split(text, separators)

    # Merge fragments into chunks of target size with overlap
    chunks: list[str] = []
    current = ""
    for fragment in fragments:
        candidate = (current + " " + fragment).strip() if current else fragment
        if len(candidate) <= size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # Carry overlap from the end of the previous chunk
            tail = current[-overlap:].strip() if current else ""
            current = (tail + " " + fragment).strip() if tail else fragment
    if current:
        chunks.append(current)
    return chunks


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def build_collection(chroma_client, client, collection_name: str,
                     all_chunks: list[dict]) -> None:
    """
    (Re)build a ChromaDB collection from a list of chunk dicts.
    Each chunk dict must have 'id', 'text', and 'metadata' keys.
    """
    # Concept: vector-index — each chunk is stored as (id, vector, text, metadata)
    try:
        chroma_client.delete_collection(collection_name)
    except Exception:
        pass  # collection did not exist yet

    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine", "embed_model": EMBED_MODEL},
    )

    texts = [c["text"] for c in all_chunks]
    log.info("Embedding %d chunks for collection '%s'...", len(texts), collection_name)

    # Concept: batch embedding — all chunks embedded in one API call per batch
    vectors = embed_batch(client, texts)

    collection.add(
        ids=[c["id"] for c in all_chunks],
        embeddings=vectors,
        documents=texts,
        metadatas=[c["metadata"] for c in all_chunks],
    )


def docs_to_chunks(docs: list[dict],
                   strategy_fn,
                   strategy_name: str) -> list[dict]:
    """Apply a chunking strategy to all documents and return flat chunk list."""
    all_chunks = []
    for doc in docs:
        chunks = strategy_fn(doc["text"])
        for i, chunk_text in enumerate(chunks):
            all_chunks.append({
                "id": f"{doc['source']}__{strategy_name}__{i:04d}",
                "text": chunk_text,
                "metadata": {
                    "source": doc["source"],
                    "strategy": strategy_name,
                    "chunk_index": i,
                },
            })
    return all_chunks


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare_strategies(chroma_client, client,
                       collections: dict[str, str]) -> None:
    """
    Run COMPARISON_QUERIES against each collection and print top-1 similarity.
    """
    import math

    def cosine_sim(distance: float) -> float:
        # ChromaDB returns cosine distance (1 - similarity)
        return round(1.0 - distance, 4)

    print("\n=== Retrieval comparison ===")

    recursive_wins = 0
    fixed_scores = []
    recursive_scores = []

    for query in COMPARISON_QUERIES:
        print(f"\nQuery: \"{query}\"")
        query_results = {}
        for strategy, name in collections.items():
            coll = chroma_client.get_collection(name)
            # Concept: vector-search — nearest-neighbour query returns top-k chunks
            result = coll.query(
                query_texts=[query],
                n_results=1,
                include=["documents", "distances"],
            )
            top_doc = result["documents"][0][0]
            top_dist = result["distances"][0][0]
            sim = cosine_sim(top_dist)
            preview = top_doc[:65].replace("\n", " ") + "..."
            print(f"  {strategy:<14} top-1 sim={sim:.4f}  \"{preview}\"")
            query_results[strategy] = sim

        if "fixed-size" in query_results and "recursive" in query_results:
            fixed_scores.append(query_results["fixed-size"])
            recursive_scores.append(query_results["recursive"])

    # Validate that recursive outperforms fixed on at least the first query
    # (paragraph-spanning fact — should expose the chunking difference)
    if recursive_scores and fixed_scores:
        first_rec = recursive_scores[0]
        first_fix = fixed_scores[0]
        if first_rec >= first_fix:
            print(
                f"\n✓ recursive top-1 ≥ fixed top-1 for paragraph-spanning query "
                f"({first_rec:.4f} vs {first_fix:.4f})"
            )
        else:
            print(
                f"\n✗ recursive top-1 ({first_rec:.4f}) < fixed top-1 ({first_fix:.4f}) "
                f"on paragraph-spanning query. This can occur with small models — "
                f"try a longer query or a different test sentence."
            )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # Concept: readiness check — verify Ollama serves the embedding model
    assert_ollama_ready(models=[EMBED_MODEL])

    client = build_client()
    chroma = build_chroma_client()

    # --- Load corpus ---
    print(f"\n=== Loading corpus ({CORPUS_DIR.name}/) ===")
    if not CORPUS_DIR.exists():
        log.error("Corpus directory not found: %s", CORPUS_DIR)
        sys.exit(1)

    docs = load_corpus()
    if not docs:
        log.error("No .md files found in %s", CORPUS_DIR)
        sys.exit(1)

    total_chars = sum(len(d["text"]) for d in docs)
    for d in docs:
        print(f"Loaded: {d['source']:<40} ({len(d['text'])} chars)")
    print(f"Total: {total_chars} chars across {len(docs)} documents")

    # --- Build and index each strategy ---
    strategies = [
        ("fixed-size",  lambda t: chunk_fixed(t),    COLLECTION_FIXED),
        ("sentence",    lambda t: chunk_sentence(t),  COLLECTION_SENTENCE),
        ("recursive",   lambda t: chunk_recursive(t), COLLECTION_RECURSIVE),
    ]

    collections: dict[str, str] = {}
    for name, fn, coll_name in strategies:
        print(f"\n=== Strategy: {name} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}) ===")
        chunks = docs_to_chunks(docs, fn, name)

        lengths = [len(c["text"]) for c in chunks]
        avg = sum(lengths) / len(lengths)
        print(f"Chunks produced: {len(chunks)}")
        print(f"Avg chunk length: {avg:.0f} chars  |  "
              f"Min: {min(lengths)}  |  Max: {max(lengths)}")

        build_collection(chroma, client, coll_name, chunks)
        print(f"Indexed {len(chunks)} chunks into collection '{coll_name}'")
        collections[name] = coll_name

        # Validate: all chunks within expected size bounds
        oversized = [c for c in chunks if len(c["text"]) > CHUNK_SIZE + 20]
        if oversized and name == "fixed-size":
            log.warning("%d fixed-size chunks exceed size+20 chars", len(oversized))

    # --- Validate collections are queryable ---
    print("\n--- Querying each collection (smoke test) ---")
    all_ok = True
    for name, coll_name in collections.items():
        try:
            coll = chroma.get_collection(coll_name)
            r = coll.query(query_texts=["test"], n_results=1)
            print(f"✓ '{coll_name}' queryable ({coll.count()} chunks)")
        except Exception as e:
            print(f"✗ '{coll_name}' query failed: {e}")
            all_ok = False

    if all_ok:
        log.info("✓ All 3 collections are queryable")

    # --- Compare retrieval quality ---
    compare_strategies(chroma, client, collections)

    print(
        f"\nDone. The '{COLLECTION_RECURSIVE}' collection is used by "
        "lab-retrieval-playground, lab-query-pipeline, and lab-rag-evaluation."
    )


if __name__ == "__main__":
    main()
