# Lab: lab-integration
# Module: memory-context
# Doc reference: docs/memory-context/architecture.md

import sys
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import MODEL, EMBED_MODEL, build_client, assert_ollama_ready
from shared.history import HistoryManager
from shared.context import compress_history, assemble_messages
from shared.memory import MemoryStore

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful assistant with long-term memory. "
    "Use any context provided from memory to give consistent, personalized answers."
)

# 30 turns covering a realistic multi-session use case
TURNS = [
    "Hi, my name is Jordan and I'm building an AI assistant for legal document review.",
    "The main challenge is that legal documents can be very long — sometimes 200 pages.",
    "We're using a RAG pipeline with a local embedding model to handle the length.",
    "What chunking strategy would you recommend for long legal contracts?",
    "How do we handle cross-references between sections in the same document?",
    "Our embedding model is nomic-embed-text. Is that a good choice for legal text?",
    "We want to support multi-language documents — English and Spanish initially.",
    "What are the trade-offs between semantic and fixed-size chunking?",
    "How would you handle tables and structured data inside PDFs?",
    "We're considering using GPT-4 for extraction but want a fallback to a local model.",
    "Can you summarize what we've discussed about the RAG pipeline so far?",
    "Now I want to talk about the evaluation strategy for the retrieval component.",
    "What metrics should we track for retrieval quality?",
    "How do we create a ground-truth evaluation set for legal retrieval?",
    "We have 500 annotated document-question pairs from our legal team.",
    "What is a good MRR target for a legal retrieval system?",
    "How does precision@k differ from recall@k and when does each matter?",
    "We want to detect when the model is hallucinating a legal clause.",
    "What techniques exist for hallucination detection in legal AI?",
    "Our target latency for a retrieval + generation pipeline is under 3 seconds.",
    "How do we cache embeddings to reduce latency on repeated document queries?",
    "We are using FastAPI for the API layer and Redis for caching.",
    "What is the best way to handle user session state in a FastAPI service?",
    "Should conversation history live in Redis or in a vector store?",
    "How do we handle context window limits when a user asks about a specific clause?",
    "We plan to add a user feedback loop — thumbs up/down on each answer.",
    "How do we use that feedback signal to improve retrieval over time?",
    "Can you remind me: what is my name and what project am I building?",
    "What was the first technical challenge I mentioned at the start of our conversation?",
    "What is our target latency and what caching strategy did we decide on?",
]


def run_integration(client) -> None:
    """
    Concept: memory-aware conversational application — combines HistoryManager,
    summarization-based compression, and external memory into a single loop.
    """
    manager = HistoryManager()
    store = MemoryStore()

    log.info("Starting 30-turn memory-aware conversation")
    log.info("Budget: %d tokens | Episodes in store: %d", manager.budget, store.episode_count())
    log.info("-" * 60)

    for i, user_msg in enumerate(TURNS, start=1):
        # Concept: retrieve from external memory — inject relevant episodes before each turn
        memory_context: str | None = None
        if store.episode_count() > 0:
            episodes = store.retrieve_episodes(client, user_msg, n_results=2)
            relevant = [ep for ep in episodes if ep["distance"] <= 0.35]
            if relevant:
                memory_context = store.format_for_injection(relevant)

        # Concept: compression threshold — apply summarization when threshold is reached
        if manager.at_threshold:
            manager.replace(compress_history(client, manager.history, keep_recent_pairs=4))
            log.info("[turn %02d] SUMMARIZATION applied | tokens after: %d", i, manager.token_count)

        manager.add_user(user_msg)

        messages = assemble_messages(SYSTEM_PROMPT, manager.history, memory_context=memory_context)
        response = client.chat.completions.create(model=MODEL, messages=messages)
        reply = response.choices[0].message.content
        manager.add_assistant(reply)

        # Concept: write to external memory — store each turn as an episode (simulated async)
        episode_text = f"User: {user_msg}\nAssistant: {reply}"
        store.add_episode(client, episode_text)

        injected = f" [memory injected]" if memory_context else ""
        log.info("[turn %02d] %s%s", i, manager.status_line(), injected)

    log.info("-" * 60)
    log.info("Conversation complete: %d turns | episodes stored: %d", len(TURNS), store.episode_count())

    # Validation: check recall turns (28, 29, 30)
    log.info("")
    log.info("RECALL VALIDATION (turns 28–30)")
    log.info("-" * 60)
    recall_questions = TURNS[27:30]
    # Replay history to extract the last 3 replies
    history = manager.history
    # The last 6 messages in history correspond to turns 28, 29, 30 (3 pairs)
    last_six = history[-6:]
    for j, (msg, question) in enumerate(zip(last_six[1::2], recall_questions), start=28):
        log.info("[turn %02d Q] %s", j, question)
        log.info("[turn %02d A] %s", j, msg["content"])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready(models=[MODEL, EMBED_MODEL])
    client = build_client()
    run_integration(client)
