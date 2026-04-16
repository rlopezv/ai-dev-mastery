# Lab: lab-query-pipeline
# Module: rag
# Doc reference: docs/rag/context-assembly.md

import logging
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import (
    CONTEXT_WINDOW,
    EMBED_MODEL,
    GENERATION_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    assert_ollama_ready,
    assemble_context,
    build_chroma_client,
    build_client,
    count_tokens,
    embed,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COLLECTION_NAME = "chunks_recursive"   # built by lab-chunking-strategies

# Concept: prompt-context-block — framing instructs the model to reason
# from the retrieved content rather than from parametric memory
SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the question using only the information "
    "in the Context section below. Cite the source numbers [N] when you use "
    "information from a specific context entry. "
    "If the context does not contain enough information to answer the question, "
    "respond with exactly: \"I don't have enough information in the provided "
    "context to answer that question.\""
)

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - Change MIN_SIMILARITY_THRESHOLD = 0.50 to MIN_SIMILARITY_THRESHOLD = 0.0
# - Observe:
#   * out-of-scope queries are no longer flagged (threshold never triggers)
#   * the model receives irrelevant context and may fabricate an answer
#   * ✓ Out-of-scope query correctly declined disappears or flips to ✗
#   * similarity score is still printed but no longer gates the pipeline

# Minimum similarity threshold — queries where all retrieved chunks score
# below this are treated as out-of-scope
MIN_SIMILARITY_THRESHOLD = 0.50

# Deduplication threshold — chunks with cosine similarity above this to an
# already-selected chunk are considered near-duplicates and dropped
DEDUP_THRESHOLD = 0.92

TOP_K = 5

# Test queries: mix of in-scope (answerable from corpus) and out-of-scope
QUERIES = [
    {
        "text": "What is the difference between top-k and top-p sampling?",
        "expected": "in-scope",
        "expected_source": "llm-inference.md",
    },
    {
        "text": "How does LoRA reduce the number of trainable parameters?",
        "expected": "in-scope",
        "expected_source": "llm-fine-tuning.md",
    },
    {
        "text": "Why does the embedding model need to be the same at index and query time?",
        "expected": "in-scope",
        "expected_source": "text-embeddings.md",
    },
    {
        "text": "What is the capital of France?",
        "expected": "out-of-scope",
        "expected_source": None,
    },
]


# ---------------------------------------------------------------------------
# Cosine similarity (for deduplication)
# ---------------------------------------------------------------------------

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot  = sum(x * y for x, y in zip(a, b))
    na   = math.sqrt(sum(x * x for x in a))
    nb   = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def retrieve(chroma_client, client, query: str,
             top_k: int = TOP_K) -> list[dict]:
    """
    Embed the query and retrieve top-k chunks from the vector store.
    Returns list of dicts with 'text', 'metadata', 'similarity', 'vector' keys.
    """
    # Concept: dense-retrieval — nearest-neighbour query against the vector index
    collection = chroma_client.get_collection(COLLECTION_NAME)
    query_vec = embed(client, query)

    results = collection.query(
        query_embeddings=[query_vec],
        n_results=top_k,
        include=["documents", "distances", "metadatas", "embeddings"],
    )

    return [
        {
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "similarity": round(1.0 - results["distances"][0][i], 4),
            "vector": results["embeddings"][0][i],
        }
        for i in range(len(results["ids"][0]))
    ]


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def deduplicate(chunks: list[dict],
                threshold: float = DEDUP_THRESHOLD) -> list[dict]:
    """
    Remove near-duplicate chunks by cosine similarity between their vectors.
    A chunk is dropped if its similarity to any already-selected chunk
    exceeds the threshold.

    Concept: chunk-deduplication — prevents the same passage from filling
    multiple context slots
    """
    selected: list[dict] = []
    for candidate in chunks:
        is_duplicate = any(
            cosine_similarity(candidate["vector"], kept["vector"]) >= threshold
            for kept in selected
        )
        if not is_duplicate:
            selected.append(candidate)
    return selected


# ---------------------------------------------------------------------------
# Context assembly
# ---------------------------------------------------------------------------

def build_context_block(chunks: list[dict]) -> tuple[str, list[dict]]:
    """
    Select chunks within the token budget and format as a numbered context block.
    Returns (context_block_string, selected_chunks).

    Concept: token-budget — prevents the assembled prompt from exceeding
    the model's context window
    """
    # Concept: assemble_context from shared config handles budget calculation
    raw_block = assemble_context(chunks, "", SYSTEM_PROMPT)

    # Re-assemble with numbering for source attribution
    selected: list[dict] = []
    used_tokens = 0
    framing_overhead = 100
    budget = (
        CONTEXT_WINDOW
        - count_tokens(SYSTEM_PROMPT)
        - MAX_TOKENS
        - framing_overhead
    )

    for chunk in chunks:
        t = count_tokens(chunk["text"])
        if used_tokens + t <= budget:
            selected.append(chunk)
            used_tokens += t

    lines = [
        f"[{i + 1}] {c['text']}"
        for i, c in enumerate(selected)
    ]
    return "\n\n".join(lines), selected


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def generate(client, query: str, context_block: str) -> str:
    """
    Call the LLM with the assembled context block and return the response text.

    Concept: prompt-context-block — system prompt + numbered context + question
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context_block}\n\nQuestion: {query}",
        },
    ]
    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def rag_query(chroma_client, client, query: str) -> dict:
    """
    Run the full RAG query pipeline for a single query.
    Returns a dict with all intermediate results for inspection.
    """
    # Step 1: retrieve
    candidates = retrieve(chroma_client, client, query)
    max_sim = candidates[0]["similarity"] if candidates else 0.0

    # Step 2: deduplicate
    deduped = deduplicate(candidates)

    # Step 3: assemble context
    context_block, selected = build_context_block(deduped)
    context_tokens = count_tokens(context_block)

    # Step 4: generate
    answer = generate(client, query, context_block)

    return {
        "query": query,
        "candidates": candidates,
        "deduped": deduped,
        "selected": selected,
        "context_block": context_block,
        "context_tokens": context_tokens,
        "max_similarity": max_sim,
        "answer": answer,
        "is_out_of_scope": max_sim < MIN_SIMILARITY_THRESHOLD,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    assert_ollama_ready(models=[EMBED_MODEL, GENERATION_MODEL])

    client = build_client()
    chroma = build_chroma_client()

    try:
        chroma.get_collection(COLLECTION_NAME)
    except Exception:
        log.error(
            "Collection '%s' not found. Run lab-chunking-strategies first.",
            COLLECTION_NAME,
        )
        sys.exit(1)

    # Print budget summary once
    framing = 100
    budget = CONTEXT_WINDOW - count_tokens(SYSTEM_PROMPT) - MAX_TOKENS - framing
    print("\n=== RAG Query Pipeline ===")
    print(f"Embedding model : {EMBED_MODEL}")
    print(f"Generation model: {GENERATION_MODEL}")
    print(f"Context window  : {CONTEXT_WINDOW} tokens")
    print(f"Token budget    : {budget} tokens available for context")

    out_of_scope_correct = 0
    in_scope_cited = 0

    for i, query_def in enumerate(QUERIES, start=1):
        query    = query_def["text"]
        expected = query_def["expected"]
        exp_src  = query_def["expected_source"]

        print(f"\n--- Query {i} ({expected}) ---")
        print(f"Q: {query}")

        result = rag_query(chroma, client, query)

        n_cand   = len(result["candidates"])
        n_dedup  = len(result["deduped"])
        n_sel    = len(result["selected"])
        ctx_tok  = result["context_tokens"]

        print(
            f"\nRetrieved {n_cand} chunks | "
            f"After dedup: {n_dedup} | "
            f"Selected: {n_sel} ({ctx_tok} tokens)"
        )

        # Concept: token-budget — validate we stayed within the budget
        if ctx_tok <= budget:
            print("Context block fits within budget ✓")
        else:
            print(f"Context block exceeds budget ✗ ({ctx_tok} > {budget})")

        if result["is_out_of_scope"]:
            print(
                f"Highest similarity: {result['max_similarity']:.4f} "
                f"— below threshold ({MIN_SIMILARITY_THRESHOLD})"
            )

        print(f"\nAnswer:\n{result['answer']}")

        # Print sources used
        sources = list({
            c["metadata"].get("source", "?") for c in result["selected"]
        })
        if sources and not result["is_out_of_scope"]:
            print(f"\nSources used: {', '.join(sorted(sources))}")

        # Validation
        if expected == "out-of-scope":
            decline_phrases = [
                "don't have enough information",
                "cannot answer",
                "not enough information",
                "no information",
            ]
            if any(p in result["answer"].lower() for p in decline_phrases):
                print("✓ Out-of-scope query correctly declined")
                out_of_scope_correct += 1
            else:
                print("✗ Out-of-scope query was not declined — model may have hallucinated")

        elif expected == "in-scope" and exp_src:
            if any(
                c["metadata"].get("source") == exp_src
                for c in result["selected"]
            ):
                print(f"✓ Expected source '{exp_src}' present in context")
                in_scope_cited += 1
            else:
                print(f"✗ Expected source '{exp_src}' not in top-{TOP_K} results")

    # Final summary
    total_in_scope = sum(1 for q in QUERIES if q["expected"] == "in-scope")
    total_oos      = sum(1 for q in QUERIES if q["expected"] == "out-of-scope")

    print(f"\n{'='*50}")
    print(f"In-scope source match : {in_scope_cited}/{total_in_scope}")
    print(f"Out-of-scope declined : {out_of_scope_correct}/{total_oos}")
    print("\nDone. Proceed to lab-rag-evaluation.")


if __name__ == "__main__":
    main()
