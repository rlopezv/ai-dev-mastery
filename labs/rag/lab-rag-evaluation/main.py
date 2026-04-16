# Lab: lab-rag-evaluation
# Module: rag
# Doc reference: docs/rag/rag-evaluation-and-metrics.md

import logging
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import (
    EMBED_MODEL,
    GENERATION_MODEL,
    JUDGE_MODEL,
    MAX_TOKENS,
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

COLLECTION_NAME = "chunks_recursive"

# System prompt — same as lab-query-pipeline for consistency
SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the question using only the information "
    "in the Context section below. Cite the source numbers [N] when you use "
    "information from a specific context entry. "
    "If the context does not contain enough information to answer the question, "
    "respond with exactly: \"I don't have enough information in the provided "
    "context to answer that question.\""
)

# ---------------------------------------------------------------------------
# Evaluation dataset
# Concept: evaluation-dataset — fixed (query, relevant_source) pairs.
# Ground truth is at source-file level: a chunk is relevant if its 'source'
# metadata matches the expected source for the question.
# ---------------------------------------------------------------------------

EVAL_SET = [
    # transformer-architecture.md (4 questions)
    {
        "query": "What are Query, Key, and Value vectors used for in attention?",
        "relevant_source": "transformer-architecture.md",
    },
    {
        "query": "How does multi-head attention differ from single-head attention?",
        "relevant_source": "transformer-architecture.md",
    },
    {
        "query": "What role do residual connections play in deep transformers?",
        "relevant_source": "transformer-architecture.md",
    },
    {
        "query": "How does RoPE encode positional information differently from sinusoidal encodings?",
        "relevant_source": "transformer-architecture.md",
    },
    # text-embeddings.md (4 questions)
    {
        "query": "Why does the embedding model need to stay the same between indexing and querying?",
        "relevant_source": "text-embeddings.md",
    },
    {
        "query": "What does cosine similarity measure and what is its range?",
        "relevant_source": "text-embeddings.md",
    },
    {
        "query": "What is the difference between mean pooling and CLS token pooling?",
        "relevant_source": "text-embeddings.md",
    },
    {
        "query": "How many dimensions does nomic-embed-text produce?",
        "relevant_source": "text-embeddings.md",
    },
    # information-retrieval.md (4 questions)
    {
        "query": "What is the saturation function in BM25 and why is it needed?",
        "relevant_source": "information-retrieval.md",
    },
    {
        "query": "How does Reciprocal Rank Fusion merge two ranked lists?",
        "relevant_source": "information-retrieval.md",
    },
    {
        "query": "What is the difference between Precision@k and Recall@k?",
        "relevant_source": "information-retrieval.md",
    },
    {
        "query": "Why can a cross-encoder reranker not run over an entire index?",
        "relevant_source": "information-retrieval.md",
    },
    # llm-fine-tuning.md (4 questions)
    {
        "query": "What is catastrophic forgetting and how is it mitigated?",
        "relevant_source": "llm-fine-tuning.md",
    },
    {
        "query": "How does LoRA reduce trainable parameters compared to full fine-tuning?",
        "relevant_source": "llm-fine-tuning.md",
    },
    {
        "query": "When is fine-tuning a better choice than RAG?",
        "relevant_source": "llm-fine-tuning.md",
    },
    {
        "query": "Why is data quality more important than data quantity in supervised fine-tuning?",
        "relevant_source": "llm-fine-tuning.md",
    },
    # llm-inference.md (4 questions)
    {
        "query": "How does the KV cache reduce inference cost from O(n²) to O(n)?",
        "relevant_source": "llm-inference.md",
    },
    {
        "query": "What is the difference between time to first token and inter-token latency?",
        "relevant_source": "llm-inference.md",
    },
    {
        "query": "How does temperature affect the token probability distribution?",
        "relevant_source": "llm-inference.md",
    },
    {
        "query": "How much VRAM does a 7B model at 4-bit quantisation require?",
        "relevant_source": "llm-inference.md",
    },
]

# Subset used for LLM-as-judge faithfulness evaluation (first 10)
FAITHFULNESS_SUBSET = EVAL_SET[:10]


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def retrieve_top_k(chroma_client, client, query: str,
                   top_k: int) -> list[dict]:
    """Retrieve top-k chunks for a query. Returns list with 'text','metadata','similarity'."""
    collection = chroma_client.get_collection(COLLECTION_NAME)
    query_vec = embed(client, query)
    results = collection.query(
        query_embeddings=[query_vec],
        n_results=top_k,
        include=["documents", "distances", "metadatas"],
    )
    return [
        {
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "similarity": round(1.0 - results["distances"][0][i], 4),
        }
        for i in range(len(results["ids"][0]))
    ]


def generate_answer(client, query: str, chunks: list[dict]) -> str:
    """Generate a grounded answer for use in faithfulness evaluation."""
    context_block = assemble_context(chunks, query, SYSTEM_PROMPT)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",
         "content": f"Context:\n{context_block}\n\nQuestion: {query}"},
    ]
    resp = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=0.0,   # deterministic for evaluation
    )
    return resp.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Retrieval metrics
# ---------------------------------------------------------------------------

def evaluate_retrieval(chroma_client, client,
                       eval_set: list[dict],
                       top_k: int) -> dict:
    """
    Compute Precision@k, Recall@k, and MRR for a given top_k.

    Concept: retrieval-precision — fraction of retrieved chunks whose source
    matches the expected source.
    Concept: retrieval-recall — whether the expected source appears at all
    in the top-k results.
    """
    precisions, recalls, reciprocal_ranks = [], [], []

    for item in eval_set:
        results = retrieve_top_k(chroma_client, client, item["query"], top_k)
        expected = item["relevant_source"]

        # A retrieved chunk is "relevant" if its source matches the expected source
        relevant_flags = [
            r["metadata"].get("source") == expected for r in results
        ]
        tp = sum(relevant_flags)

        precisions.append(tp / top_k)
        recalls.append(1.0 if tp > 0 else 0.0)

        # MRR: reciprocal rank of first relevant result
        first_relevant = next(
            (i + 1 for i, flag in enumerate(relevant_flags) if flag), None
        )
        reciprocal_ranks.append(1.0 / first_relevant if first_relevant else 0.0)

    n = len(eval_set)
    return {
        "precision_at_k": round(sum(precisions) / n, 4),
        "recall_at_k":    round(sum(recalls) / n, 4),
        "mrr":            round(sum(reciprocal_ranks) / n, 4),
        "top_k":          top_k,
    }


# ---------------------------------------------------------------------------
# LLM-as-judge faithfulness
# ---------------------------------------------------------------------------

JUDGE_PROMPT_TEMPLATE = """You are an evaluation assistant. You will be given a Context and an Answer.
Determine whether every factual claim in the Answer is supported by the Context.

Respond with only one of:
- FAITHFUL — every claim in the answer can be traced to the context
- NOT_FAITHFUL — the answer contains at least one claim not supported by the context

Context:
{context}

Answer:
{answer}

Verdict:"""


def judge_faithfulness(client, context: str, answer: str) -> bool:
    """
    Use the judge model to assess whether the answer is faithful to the context.
    Returns True if faithful, False otherwise.

    Concept: answer-faithfulness — LLM-as-judge checks every claim against context
    """
    prompt = JUDGE_PROMPT_TEMPLATE.format(context=context[:2000], answer=answer)
    resp = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
        temperature=0.0,
    )
    verdict = resp.choices[0].message.content.strip().upper()
    return "FAITHFUL" in verdict and "NOT_FAITHFUL" not in verdict


def evaluate_faithfulness(chroma_client, client,
                          eval_subset: list[dict],
                          top_k: int = 5) -> dict:
    """
    Generate answers for each item in eval_subset and score faithfulness.
    Returns dict with 'faithful_count', 'total', 'mean_score'.
    """
    faithful_count = 0
    total = len(eval_subset)

    for i, item in enumerate(eval_subset, start=1):
        chunks = retrieve_top_k(chroma_client, client, item["query"], top_k)
        answer = generate_answer(client, item["query"], chunks)
        context_block = assemble_context(chunks, item["query"], SYSTEM_PROMPT)

        is_faithful = judge_faithfulness(client, context_block, answer)
        if is_faithful:
            faithful_count += 1

        label = "✓ faithful" if is_faithful else "✗ not faithful"
        q_preview = item["query"][:60] + "..."
        log.info("  [%d/%d] %s  Q: %s", i, total, label, q_preview)

    mean_score = round(faithful_count / total, 4) if total > 0 else 0.0
    return {
        "faithful_count": faithful_count,
        "total": total,
        "mean_score": mean_score,
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

    print("\n=== RAG Evaluation ===")
    print(f"Corpus       : 5 documents")
    print(f"Eval set     : {len(EVAL_SET)} questions")
    print(f"Collection   : {COLLECTION_NAME}")

    # --- Retrieval metrics at top_k=5 ---
    print("\n--- Retrieval metrics (top_k=5) ---")
    log.info("Running retrieval evaluation (top_k=5)...")
    metrics_5 = evaluate_retrieval(chroma, client, EVAL_SET, top_k=5)
    print(f"Precision@5 : {metrics_5['precision_at_k']}")
    print(f"Recall@5    : {metrics_5['recall_at_k']}")
    print(f"MRR         : {metrics_5['mrr']}")

    # --- Retrieval metrics at top_k=10 ---
    print("\n--- Retrieval metrics (top_k=10) ---")
    log.info("Running retrieval evaluation (top_k=10)...")
    metrics_10 = evaluate_retrieval(chroma, client, EVAL_SET, top_k=10)
    print(f"Precision@5 : {metrics_10['precision_at_k']}")
    print(f"Recall@5    : {metrics_10['recall_at_k']}")
    print(f"MRR         : {metrics_10['mrr']}")

    # Validate recall improves with larger top_k
    # Concept: retrieval-recall — more candidates means the correct source
    # is more likely to appear somewhere in the retrieved set
    if metrics_10["recall_at_k"] >= metrics_5["recall_at_k"]:
        print(
            f"\n✓ Recall@5 (top_k=10) ≥ Recall@5 (top_k=5): "
            f"{metrics_10['recall_at_k']} ≥ {metrics_5['recall_at_k']}"
        )
    else:
        print(
            f"\n✗ Recall@5 did not improve with top_k=10. "
            f"This is unexpected — check that the collection was built correctly."
        )

    # --- LLM-as-judge faithfulness ---
    print(f"\n--- Faithfulness (LLM-as-judge, {len(FAITHFULNESS_SUBSET)} answers) ---")
    log.info("Running faithfulness evaluation...")
    faith = evaluate_faithfulness(chroma, client, FAITHFULNESS_SUBSET, top_k=5)
    print(f"Scored     : {faith['total']} answers")
    print(f"Faithful   : {faith['faithful_count']} / {faith['total']}")
    print(f"Mean score : {faith['mean_score']}")

    if faith["mean_score"] >= 0.70:
        print("✓ Mean faithfulness ≥ 0.70")
    else:
        print(
            "✗ Mean faithfulness below 0.70. Check that SYSTEM_PROMPT includes "
            "'answer only from context' instruction, and consider a larger model."
        )

    # --- Summary ---
    print(f"\n{'='*50}")
    print("=== Summary ===")
    print(f"Retrieval precision (top_k=5)  : {metrics_5['precision_at_k']}")
    print(f"Retrieval recall    (top_k=5)  : {metrics_5['recall_at_k']}")
    print(f"Retrieval recall    (top_k=10) : {metrics_10['recall_at_k']}")
    print(f"Faithfulness mean              : {faith['mean_score']}")
    print("\nDone. Proceed to docs/rag/validation.md.")


if __name__ == "__main__":
    main()
