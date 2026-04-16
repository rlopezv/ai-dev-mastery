# Lab: lab-conversation-history
# Module: memory-context
# Doc reference: docs/memory-context/conversation-history.md

import sys
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import MODEL, build_client, assert_ollama_ready
from shared.history import HistoryManager

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

SYSTEM_PROMPT = "You are a helpful assistant. Answer concisely in one or two sentences."

TURNS = [
    "What is a transformer model?",
    "How does the attention mechanism work?",
    "What is positional encoding and why is it needed?",
    "Explain the difference between encoder and decoder architectures.",
    "What is the purpose of layer normalization in transformers?",
    "How does beam search differ from greedy decoding?",
    "What is temperature in language model sampling?",
    "Explain top-k and top-p (nucleus) sampling.",
    "What are the trade-offs between model size and inference speed?",
    "How does quantization reduce memory requirements?",
    "What is fine-tuning and when is it preferred over prompting?",
    "Explain LoRA fine-tuning.",
    "What is RLHF and how does it align model behavior?",
    "What is a system prompt?",
    "How does context length affect model capabilities?",
    "What is token streaming in API responses?",
    "Explain the difference between chat and completion endpoints.",
    "What is few-shot prompting?",
    "How does chain-of-thought prompting improve reasoning?",
    "What is retrieval-augmented generation?",
    "How does a vector database support RAG?",
    "What is cosine similarity in embedding search?",
    "Explain the difference between sparse and dense retrieval.",
    "What is a re-ranker in a retrieval pipeline?",
    "How are embeddings different from one-hot encodings?",
    "What is semantic chunking in document processing?",
    "Explain the sliding window approach to chunking.",
    "What is the role of metadata in a vector store?",
    "How does hybrid search combine BM25 and dense retrieval?",
    "What is a knowledge graph and how does it complement RAG?",
    "How is structured output enforced in LLM APIs?",
    "What is JSON schema validation for LLM outputs?",
    "Explain function calling in the OpenAI API.",
    "What is an AI agent?",
    "How does tool use differ from RAG?",
    "What is ReAct prompting?",
    "Explain the plan-and-execute agent pattern.",
    "What is memory in the context of AI agents?",
    "How do multi-agent systems coordinate?",
    "What is the role of an orchestrator agent?",
    "Explain how LangChain handles tool definitions.",
    "What is LlamaIndex and how does it differ from LangChain?",
    "What is Ollama and why is it useful for local development?",
    "How does the OpenAI-compatible API simplify model switching?",
    "What is a context window and how does it limit conversation length?",
    "Explain how token budgets prevent API errors in long conversations.",
    "What is the difference between session memory and long-term memory?",
    "How does summarization-based compression preserve context?",
    "What is the write-retrieve-inject pattern?",
    "How does ChromaDB store and retrieve embeddings?",
]


# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In run_conversation(), comment out the if manager.at_ceiling: block
# - Observe:
#   * token count grows unbounded — no pairs are ever dropped
#   * the model eventually returns openai.BadRequestError when context exceeds the API limit
#   * the script raises before completing all 50 turns
#   * shows why the budget ceiling guard is required for long-running conversations

def run_conversation(client) -> None:
    """
    Concept: conversation history — accumulate turns, track tokens, enforce budget ceiling.
    """
    manager = HistoryManager()
    log.info("Starting 50-turn conversation loop")
    log.info("Budget: %d tokens", manager.budget)
    log.info("-" * 60)

    for i, user_msg in enumerate(TURNS, start=1):
        # Concept: budget ceiling — enforce hard limit before sending
        if manager.at_ceiling:
            # Drop oldest pair to stay within budget
            trimmed = manager.history[2:]
            manager.replace(trimmed)
            log.info("[turn %02d] BUDGET CEILING: oldest turn pair dropped", i)

        manager.add_user(user_msg)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + manager.history
        response = client.chat.completions.create(model=MODEL, messages=messages)
        reply = response.choices[0].message.content
        manager.add_assistant(reply)

        # Concept: token counting — log count after every turn
        log.info("[turn %02d] %s", i, manager.status_line())

    log.info("-" * 60)
    log.info("Conversation complete: %d turns, final token count: %d", len(TURNS), manager.token_count)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready(models=[MODEL])
    client = build_client()
    run_conversation(client)
