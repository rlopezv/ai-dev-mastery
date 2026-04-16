# Lab: lab-embeddings
# Module: rag
# Doc reference: docs/rag/embeddings-and-vector-search.md

import logging
import math
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import (
    EMBED_MODEL,
    assert_ollama_ready,
    build_client,
    embed,
    embed_batch,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Query used in observations 2 and 3
QUERY = "How does the transformer attention mechanism work?"

# Texts for Observation 2: cosine similarity comparison
# Manually categorised so the score gap is observable regardless of model version
RELATED_TEXTS = [
    (
        "Self-attention allows each token to attend to all other tokens in the "
        "sequence, computing a weighted sum of Value vectors based on Query-Key "
        "dot-product similarity."
    ),
    (
        "The transformer architecture uses multi-head self-attention layers "
        "followed by feed-forward networks to process sequences in parallel."
    ),
]
UNRELATED_TEXTS = [
    "The weather in Madrid is sunny today with temperatures around 24 degrees.",
    "Recipe: mix flour, eggs, and sugar to make a classic sponge cake batter.",
]

# Similarity thresholds — from docs/rag/embeddings-and-vector-search.md
RELATED_MIN_THRESHOLD = 0.75
UNRELATED_MAX_THRESHOLD = 0.55

# Corpus directory (shared across all rag labs)
CORPUS_DIR = pathlib.Path(__file__).parent.parent / "corpus"


# ---------------------------------------------------------------------------
# Cosine similarity
# ---------------------------------------------------------------------------

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Concept: cosine similarity — measures angle between embedding vectors,
    capturing semantic proximity independent of vector magnitude.
    """
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# Corpus loading
# ---------------------------------------------------------------------------

def load_corpus_snippets(corpus_dir: pathlib.Path,
                          max_chars: int = 300) -> list[dict]:
    """
    Load the first max_chars characters from each corpus file as a snippet.
    Returns list of dicts with 'source' and 'text' keys.
    """
    snippets: list[dict] = []
    for md_file in sorted(corpus_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8").strip()
        # Take first paragraph (up to max_chars) as the snippet
        snippet = text[:max_chars].rsplit(" ", 1)[0]  # break at word boundary
        snippets.append({"source": md_file.name, "text": snippet})
    return snippets


# ---------------------------------------------------------------------------
# Observations
# ---------------------------------------------------------------------------

def observation_1_single_embedding(client) -> None:
    """
    Observation 1: Embed a single text and inspect the returned vector.

    Concept: the embedding API returns a fixed-dimension dense vector
    regardless of input length (up to the model's context limit).
    """
    print("\n=== Observation 1: Single text embedding ===")

    sample_text = "The transformer architecture uses self-attention mechanisms."
    # Concept: single text embedding — one API call produces one vector
    vector = embed(client, sample_text)

    print(f"Model       : {EMBED_MODEL}")
    print(f"Vector dim  : {len(vector)}")
    print(f"First 5 dims: {[round(v, 4) for v in vector[:5]]}")

    assert len(vector) > 0, "Embedding returned an empty vector."
    log.info("✓ Embedding returned a vector of dimension %d", len(vector))


# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In RELATED_TEXTS, replace both entries with texts from a different domain
#   (e.g., cooking recipes, sports news)
# - Observe:
#   * related avg drops below 0.75 — the ✓ threshold check flips to ✗
#   * semantic gap collapses — related and unrelated scores converge
#   * example quality, not just category membership, drives the observable gap

def observation_2_cosine_similarity(client) -> None:
    """
    Observation 2: Compare cosine similarity scores for semantically
    related vs. unrelated texts against a fixed query.

    Concept: semantic gap — related texts score ≥ 0.75,
    unrelated texts score ≤ 0.55.
    """
    print(f"\n=== Observation 2: Cosine similarity ===")
    print(f"Query: \"{QUERY[:70]}...\"\n")

    # Concept: batch embedding — all texts embedded in one API call
    all_texts = [QUERY] + RELATED_TEXTS + UNRELATED_TEXTS
    vectors = embed_batch(client, all_texts)

    query_vec = vectors[0]
    related_vecs = vectors[1 : 1 + len(RELATED_TEXTS)]
    unrelated_vecs = vectors[1 + len(RELATED_TEXTS) :]

    related_scores: list[float] = []
    for text, vec in zip(RELATED_TEXTS, related_vecs):
        sim = cosine_similarity(query_vec, vec)
        related_scores.append(sim)
        label = text[:55] + "..."
        print(f"  [related]    \"{label}\"  similarity={sim:.4f}")

    print()
    unrelated_scores: list[float] = []
    for text, vec in zip(UNRELATED_TEXTS, unrelated_vecs):
        sim = cosine_similarity(query_vec, vec)
        unrelated_scores.append(sim)
        label = text[:55] + "..."
        print(f"  [unrelated]  \"{label}\"  similarity={sim:.4f}")

    related_avg = sum(related_scores) / len(related_scores)
    unrelated_avg = sum(unrelated_scores) / len(unrelated_scores)
    gap = related_avg - unrelated_avg
    print(f"\nSemantic gap (related avg − unrelated avg): {gap:.2f}")

    # Validate thresholds
    if related_avg >= RELATED_MIN_THRESHOLD:
        print(f"✓ related avg ({related_avg:.2f}) ≥ threshold ({RELATED_MIN_THRESHOLD})")
    else:
        print(
            f"✗ related avg ({related_avg:.2f}) is below expected threshold "
            f"({RELATED_MIN_THRESHOLD}). Model may differ from nomic-embed-text."
        )

    if unrelated_avg <= UNRELATED_MAX_THRESHOLD:
        print(f"✓ unrelated avg ({unrelated_avg:.2f}) ≤ threshold ({UNRELATED_MAX_THRESHOLD})")
    else:
        print(
            f"✗ unrelated avg ({unrelated_avg:.2f}) is above expected threshold "
            f"({UNRELATED_MAX_THRESHOLD}). Check that unrelated texts are truly off-topic."
        )


def observation_3_batch_ranking(client) -> None:
    """
    Observation 3: Batch-embed corpus snippets and rank by similarity to query.

    Concept: retrieval as ranking — cosine similarity scores determine
    the order in which texts are returned to the caller.
    """
    print(f"\n=== Observation 3: Batch ranking ===")
    print(f"Query: \"{QUERY[:70]}...\"\n")

    if not CORPUS_DIR.exists():
        log.error("Corpus directory not found: %s", CORPUS_DIR)
        log.error("Expected: labs/rag/corpus/*.md")
        return

    snippets = load_corpus_snippets(CORPUS_DIR)
    if not snippets:
        log.error("No .md files found in %s", CORPUS_DIR)
        return

    texts = [s["text"] for s in snippets]
    print(f"Embedding {len(texts)} corpus snippets (batch)...")

    t_start = time.perf_counter()
    # Concept: batch embedding — all corpus texts embedded in one request
    all_vecs = embed_batch(client, [QUERY] + texts)
    t_elapsed = time.perf_counter() - t_start

    query_vec = all_vecs[0]
    corpus_vecs = all_vecs[1:]

    # Rank snippets by cosine similarity to query
    ranked = sorted(
        zip(snippets, corpus_vecs),
        key=lambda pair: cosine_similarity(query_vec, pair[1]),
        reverse=True,
    )

    print(f"Ranked corpus ({len(ranked)} texts, highest similarity first):\n")
    for rank, (snippet, vec) in enumerate(ranked, start=1):
        sim = cosine_similarity(query_vec, vec)
        preview = snippet["text"][:60].replace("\n", " ") + "..."
        print(f"  #{rank:<2} sim={sim:.4f}  {snippet['source']}  \"{preview}\"")

    print(f"\nBatch embedding time: {t_elapsed:.2f}s for {len(texts)} texts")
    log.info("✓ Batch ranking complete — top result: %s", ranked[0][0]["source"])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # Concept: readiness check — verify Ollama is reachable before any work
    assert_ollama_ready(models=[EMBED_MODEL])
    client = build_client()

    observation_1_single_embedding(client)
    observation_2_cosine_similarity(client)
    observation_3_batch_ranking(client)

    print("\nDone. Proceed to lab-chunking-strategies.")


if __name__ == "__main__":
    main()
