# Lab: lab-integration
# Module: rag
# Doc reference: docs/rag/architecture.md

import logging
import math
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import (
    CONTEXT_WINDOW,
    EMBED_MODEL,
    GENERATION_MODEL,
    MAX_TOKENS,
    assemble_context,
    assert_ollama_ready,
    build_chroma_client,
    build_client,
    count_tokens,
    embed,
    embed_batch,
    load_corpus,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COLLECTION_NAME = "rag_integration"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
TOP_K = 5
DEDUP_THRESHOLD = 0.92   # similarity above which two chunks are considered duplicates
MIN_SIMILARITY = 0.50    # minimum top-1 similarity to attempt generation

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the question using only the information "
    "in the provided Context. If the context does not contain the answer, "
    "say 'I don't have enough information to answer that.'"
)

DEMO_QUERIES = [
    "How does the KV cache reduce inference cost during autoregressive decoding?",
    "What is the difference between top-k and top-p sampling?",
    "How does LoRA reduce the number of trainable parameters?",
    "What is cosine similarity and how is it used in retrieval?",
    "What is the capital of France?",          # out-of-scope query
]


# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - Replace SYSTEM_PROMPT with a generic "You are a helpful assistant."
#   (remove the "using only the information in the provided Context" constraint)
# - Observe:
#   * Out-of-scope query ("What is the capital of France?") is answered from
#     parametric memory instead of being declined — confident but ungrounded
#   * In-scope answers may blend retrieved context with model training knowledge,
#     making source citations unreliable
#   * Pipeline summary shows 0 declined queries, hiding the retrieval failure


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def cosine_similarity(a: list[float], b: list[float]) -> float:
    # Concept: cosine similarity — angle-based distance between embedding vectors
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def recursive_chunk(text: str,
                    chunk_size: int = CHUNK_SIZE,
                    overlap: int = CHUNK_OVERLAP) -> list[str]:
    # Concept: recursive character chunking — paragraph → sentence → word priority
    separators = ["\n\n", "\n", ". ", " ", ""]
    chosen_sep = ""
    chosen_parts = list(text)
    for sep in separators:
        parts = text.split(sep) if sep else list(text)
        if parts and max(len(p) for p in parts) <= chunk_size:
            chosen_sep = sep
            chosen_parts = parts
            break

    chunks: list[str] = []
    current = ""
    for part in chosen_parts:
        if not part:
            continue
        candidate = current + chosen_sep + part if current else part
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = current[-overlap:] + chosen_sep + part if current else part
    if current:
        chunks.append(current)
    return [c for c in chunks if c.strip()]


# ---------------------------------------------------------------------------
# Ingestion phase
# ---------------------------------------------------------------------------

def build_index(client, chroma):
    """
    Load corpus → chunk → embed → persist to ChromaDB.

    Concept: document ingestion pipeline — offline phase that runs once per corpus.
    Returns the ChromaDB collection ready for querying.
    """
    log.info("=== Ingestion phase ===")

    # Concept: document loader — reads source files and extracts clean text
    docs = load_corpus()
    log.info("Loaded %d corpus documents", len(docs))

    all_chunks: list[dict] = []
    for doc in docs:
        chunks = recursive_chunk(doc["text"])
        for i, chunk_text in enumerate(chunks):
            all_chunks.append({
                "id": f"{doc['source']}__chunk{i}",
                "text": chunk_text,
                "metadata": {"source": doc["source"], "chunk_index": i},
            })

    log.info(
        "Chunked %d documents → %d chunks (size=%d, overlap=%d)",
        len(docs), len(all_chunks), CHUNK_SIZE, CHUNK_OVERLAP,
    )

    # Concept: batch embedding — amortizes API round-trip overhead during ingestion
    t0 = time.perf_counter()
    vectors = embed_batch(client, [c["text"] for c in all_chunks])
    log.info("Embedded %d chunks in %.1fs using %s",
             len(all_chunks), time.perf_counter() - t0, EMBED_MODEL)

    # Concept: vector store — persists (id, vector, text, metadata) for cosine retrieval
    try:
        chroma.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = chroma.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", "embedding_model": EMBED_MODEL},
    )
    collection.add(
        ids=[c["id"] for c in all_chunks],
        embeddings=vectors,
        documents=[c["text"] for c in all_chunks],
        metadatas=[c["metadata"] for c in all_chunks],
    )
    log.info("Indexed %d chunks into collection '%s' ✓", len(all_chunks), COLLECTION_NAME)
    return collection


# ---------------------------------------------------------------------------
# Query phase
# ---------------------------------------------------------------------------

def run_query(client, collection, query: str) -> dict:
    """
    Full query pipeline: embed → retrieve → deduplicate → assemble → generate.

    Concept: query pipeline — online phase that runs on every user request.
    """
    log.info("\n--- Query ---")
    log.info("Q: %s", query)

    # Concept: query embedding — must use same model as ingestion for compatible vectors
    query_vec = embed(client, query)

    # Concept: dense retrieval — nearest-neighbor search over the vector store
    results = collection.query(
        query_embeddings=[query_vec],
        n_results=TOP_K,
        include=["documents", "metadatas", "distances", "embeddings"],
    )
    candidates = [
        {
            "text": doc,
            "metadata": meta,
            "similarity": 1.0 - dist,  # ChromaDB returns cosine distance (1 - similarity)
            "embedding": emb,
        }
        for doc, meta, dist, emb in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
            results["embeddings"][0],
        )
    ]

    # Concept: chunk deduplication — remove near-duplicate chunks before assembly
    selected: list[dict] = []
    for candidate in candidates:
        is_dup = any(
            cosine_similarity(candidate["embedding"], s["embedding"]) >= DEDUP_THRESHOLD
            for s in selected
        )
        if not is_dup:
            selected.append(candidate)

    best_sim = candidates[0]["similarity"] if candidates else 0.0
    log.info(
        "Retrieved %d | After dedup: %d | Best similarity: %.4f",
        len(candidates), len(selected), best_sim,
    )

    # Concept: out-of-scope detection — decline when retrieval quality is below threshold
    if not selected or best_sim < MIN_SIMILARITY:
        answer = "I don't have enough information in the provided context to answer that question."
        log.info("Out-of-scope: declined ✓")
        return {"answer": answer, "sources": [], "out_of_scope": True}

    # Concept: token budget guard — select chunks within context window budget
    context_block = assemble_context(selected, query, SYSTEM_PROMPT)
    budget = CONTEXT_WINDOW - count_tokens(SYSTEM_PROMPT) - count_tokens(query) - MAX_TOKENS - 100
    log.info("Context block: %d tokens (budget: %d) ✓", count_tokens(context_block), budget)

    # Concept: prompt context block — numbered chunks framed with retrieval instructions
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context_block}\n\nQuestion: {query}",
        },
    ]

    # Concept: grounded generation — model reasons from retrieved context
    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
    )
    answer = response.choices[0].message.content.strip()
    sources = sorted({c["metadata"]["source"] for c in selected})

    preview = answer[:100] + ("..." if len(answer) > 100 else "")
    log.info("Answer: %s", preview)
    log.info("Sources: %s", ", ".join(sources))

    return {"answer": answer, "sources": sources, "out_of_scope": False}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    assert_ollama_ready(models=[EMBED_MODEL, GENERATION_MODEL])

    client = build_client()
    chroma = build_chroma_client()

    # Phase 1: offline ingestion
    collection = build_index(client, chroma)

    # Phase 2: online query pipeline
    log.info("\n=== Query phase ===")
    log.info("Embedding model : %s", EMBED_MODEL)
    log.info("Generation model: %s", GENERATION_MODEL)
    log.info("Context window  : %d tokens", CONTEXT_WINDOW)

    all_results = [run_query(client, collection, q) for q in DEMO_QUERIES]

    # Phase 3: pipeline summary
    in_scope = [r for r in all_results if not r["out_of_scope"]]
    declined = [r for r in all_results if r["out_of_scope"]]

    log.info("\n=== Pipeline summary ===")
    log.info("Total queries   : %d", len(all_results))
    log.info("In-scope        : %d", len(in_scope))
    log.info("Declined (OOS)  : %d ✓", len(declined))
    log.info("\nFull RAG pipeline complete ✓")


if __name__ == "__main__":
    main()
