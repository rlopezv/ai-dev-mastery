# Stub tool implementations for ai-agents labs
# Doc reference: docs/ai-agents/single-agent-loop.md
#
# All tools return deterministic output based on input patterns.
# No live network calls — lab outputs are reproducible and failure cases predictable.

# ---------------------------------------------------------------------------
# Stub data
# ---------------------------------------------------------------------------

_SEARCH_RESULTS: dict[str, list[str]] = {
    "transformer": [
        "attention_is_all_you_need — 'Attention Is All You Need': introduces the Transformer architecture.",
        "bert_paper — 'BERT: Pre-training of Deep Bidirectional Transformers': BERT overview.",
        "gpt3_paper — 'GPT-3: Language Models are Few-Shot Learners': scaling laws for transformers.",
    ],
    "rag": [
        "rag_paper — 'Retrieval-Augmented Generation for Knowledge-Intensive Tasks': original RAG paper.",
        "realm_paper — 'REALM: Retrieval-Augmented Language Model Pre-Training': REALM overview.",
    ],
    "agent": [
        "react_paper — 'ReAct: Synergizing Reasoning and Acting in Language Models': ReAct pattern.",
        "toolformer_paper — 'Toolformer: Language Models Can Teach Themselves to Use Tools'.",
    ],
    "default": [
        "survey_llm — 'A Survey of Large Language Models': broad LLM overview.",
    ],
}

_DOCUMENTS: dict[str, str] = {
    "attention_is_all_you_need": (
        "The Transformer model relies entirely on self-attention mechanisms to compute "
        "representations of its input and output without using sequence-aligned RNNs or "
        "convolutions. The encoder maps input tokens to continuous representations. The "
        "decoder generates output tokens one at a time, attending to encoder output and "
        "its own prior outputs. Multi-head attention allows the model to jointly attend "
        "to information from different representation subspaces at different positions. "
        "Key result: achieves 28.4 BLEU on WMT 2014 English-to-German translation, "
        "outperforming all prior models including ensembles, at a fraction of the training cost."
    ),
    "rag_paper": (
        "Retrieval-Augmented Generation combines a pre-trained parametric language model "
        "with a non-parametric memory (a dense vector index over Wikipedia). At query time "
        "the model retrieves relevant documents and uses them as additional context for "
        "generation. Two variants: RAG-Sequence (one set of retrieved docs per sequence) "
        "and RAG-Token (different docs per token). Outperforms parametric-only models on "
        "knowledge-intensive NLP tasks without retraining."
    ),
    "react_paper": (
        "ReAct interleaves reasoning traces (Thought) with task-specific actions (Action) "
        "in an alternating sequence. This allows the model to maintain a dynamic reasoning "
        "chain and take grounded actions that interact with external environments. Evaluation "
        "on HotpotQA and Fever shows ReAct outperforms chain-of-thought alone and action-only "
        "baselines. Interpretable traces enable humans to inspect and correct agent behavior."
    ),
    "default": (
        "This document covers core concepts and implementation details for the requested topic. "
        "Key findings: the approach outperforms baselines on standard benchmarks and generalizes "
        "well across domains."
    ),
}


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def search_web(query: str) -> str:
    """
    Stub: search the web for articles matching the query.
    Returns a numbered list of document IDs and article titles.
    Use a document ID from these results with read_document() to get full content.
    """
    query_lower = query.lower()
    if any(k in query_lower for k in ("transformer", "attention", "bert", "gpt")):
        results = _SEARCH_RESULTS["transformer"]
    elif any(k in query_lower for k in ("rag", "retrieval", "augmented")):
        results = _SEARCH_RESULTS["rag"]
    elif any(k in query_lower for k in ("agent", "react", "tool")):
        results = _SEARCH_RESULTS["agent"]
    else:
        results = _SEARCH_RESULTS["default"]
    return "Search results:\n" + "\n".join(f"  {i+1}. {r}" for i, r in enumerate(results))


def read_document(document_id: str) -> str:
    """
    Stub: read the full content of a document by its ID.
    Use document IDs returned by search_web().
    """
    doc_key = document_id.lower().replace(" ", "_").replace("-", "_")
    for key in _DOCUMENTS:
        if key in doc_key or doc_key in key:
            return _DOCUMENTS[key]
    return _DOCUMENTS["default"]


def calculator(expression: str) -> str:
    """
    Evaluate a simple arithmetic expression.
    Supports +, -, *, / and parentheses. No variables.
    """
    try:
        allowed = set("0123456789+-*/()., ")
        if not all(c in allowed for c in expression):
            return f"Error: expression contains unsupported characters: {expression!r}"
        result = eval(expression, {"__builtins__": {}})  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Error: could not evaluate '{expression}': {e}"


def summarize_stub(text: str, max_sentences: int = 3) -> str:
    """
    Stub: return the first max_sentences sentences of text as a summary.
    """
    sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    summary = ". ".join(sentences[:max_sentences])
    if summary and not summary.endswith("."):
        summary += "."
    return summary or text[:200]
