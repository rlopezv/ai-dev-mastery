# Lab: lab-memory-types
# Module: memory-context
# Doc reference: docs/memory-context/memory-types.md

import sys
import pathlib
import logging
import chromadb

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import (
    MODEL,
    EMBED_MODEL,
    build_client,
    embed,
    assert_ollama_ready,
    count_tokens,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Demo configuration
# ---------------------------------------------------------------------------

# Concept: token budget — intentionally small to trigger in-context overflow
DEMO_CONTEXT_WINDOW = 800
DEMO_OUTPUT_RESERVATION = 150
DEMO_SYSTEM_TOKENS = 20
DEMO_HISTORY_BUDGET = DEMO_CONTEXT_WINDOW - DEMO_OUTPUT_RESERVATION - DEMO_SYSTEM_TOKENS

ANCHOR_FACT = "My name is Alex and I am working on a project called Falcon."
ANCHOR_QUESTION = "What is my name and what project am I working on?"

FILLER_TURNS = [
    ("What is a consensus algorithm?", None),
    ("How does the Raft protocol handle leader election?", None),
    ("Explain eventual consistency in distributed systems.", None),
    ("What is a distributed hash table?", None),
    ("How does vector clocks work?", None),
    ("Explain the CAP theorem.", None),
    ("What is a two-phase commit?", None),
    ("How does consistent hashing distribute load?", None),
    ("What are the trade-offs of optimistic vs pessimistic locking?", None),
    ("Explain the difference between sharding and partitioning.", None),
]

SYSTEM_PROMPT = "You are a helpful assistant. Answer concisely."


# ---------------------------------------------------------------------------
# Shared: simple turn-based chat with token tracking
# ---------------------------------------------------------------------------

def chat_turn(client, history: list[dict], user_msg: str) -> tuple[str, list[dict]]:
    """Send one turn and append both messages to history. Return (reply, updated_history)."""
    history = history + [{"role": "user", "content": user_msg}]
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
    )
    reply = response.choices[0].message.content
    history = history + [{"role": "assistant", "content": reply}]
    return reply, history


def drop_oldest_pair(history: list[dict]) -> list[dict]:
    """
    Concept: truncation — remove the oldest user+assistant pair when budget is exceeded.
    Always removes two messages to preserve role alternation.
    """
    if len(history) >= 2:
        return history[2:]
    return history


# ---------------------------------------------------------------------------
# Observation 1: in-context memory overflows, anchor fact is lost
# ---------------------------------------------------------------------------

def observation_1_in_context_overflow(client) -> None:
    log.info("=" * 60)
    log.info("OBSERVATION 1 — In-context memory overflow")
    log.info("=" * 60)
    log.info("Anchor fact stated at turn 1: %r", ANCHOR_FACT)
    log.info("Budget: %d tokens  |  Window: %d tokens", DEMO_HISTORY_BUDGET, DEMO_CONTEXT_WINDOW)
    log.info("-" * 60)

    history: list[dict] = []

    # Turn 1: state the anchor fact
    reply, history = chat_turn(client, history, ANCHOR_FACT)
    tokens = count_tokens(history)
    log.info("[turn 1] anchor fact stated | tokens: %d / %d", tokens, DEMO_HISTORY_BUDGET)

    # Filler turns: fill context until truncation is needed
    for i, (question, _) in enumerate(FILLER_TURNS, start=2):
        tokens = count_tokens(history)
        if tokens > DEMO_HISTORY_BUDGET:
            # Concept: truncation — oldest turn pair dropped to make room
            history = drop_oldest_pair(history)
            log.info("[turn %d] *** TRUNCATION: oldest turn pair dropped ***", i)

        reply, history = chat_turn(client, history, question)
        tokens = count_tokens(history)
        log.info("[turn %d] tokens: %d / %d", i, tokens, DEMO_HISTORY_BUDGET)

    # Final question: can the model recall the anchor fact?
    log.info("-" * 60)
    log.info("[recall] %s", ANCHOR_QUESTION)
    reply, history = chat_turn(client, history, ANCHOR_QUESTION)
    log.info("[reply]  %s", reply)
    log.info("")
    log.info("Expected: model CANNOT recall 'Alex' or 'Falcon' — fact was truncated out.")
    log.info("")


# ---------------------------------------------------------------------------
# Observation 2: external memory preserves anchor fact across overflow
# ---------------------------------------------------------------------------

def observation_2_external_memory_recall(client) -> None:
    log.info("=" * 60)
    log.info("OBSERVATION 2 — External memory preserves fact across overflow")
    log.info("=" * 60)
    log.info("Anchor fact: %r", ANCHOR_FACT)
    log.info("Strategy: write to ChromaDB at turn 1, retrieve and inject before recall")
    log.info("-" * 60)

    # Concept: external memory — ChromaDB EphemeralClient for in-memory storage (no Docker)
    chroma = chromadb.EphemeralClient()
    collection = chroma.create_collection("facts")

    history: list[dict] = []

    # Turn 1: state anchor fact AND write it to external memory
    reply, history = chat_turn(client, history, ANCHOR_FACT)
    tokens = count_tokens(history)
    log.info("[turn 1] anchor fact stated | tokens: %d / %d", tokens, DEMO_HISTORY_BUDGET)

    # Concept: write to external memory — embed and store the anchor fact
    fact_embedding = embed(client, ANCHOR_FACT)
    collection.add(
        documents=[ANCHOR_FACT],
        embeddings=[fact_embedding],
        ids=["anchor-fact"],
    )
    log.info("[memory] anchor fact written to ChromaDB collection")

    # Filler turns (identical to observation 1, including truncation)
    for i, (question, _) in enumerate(FILLER_TURNS, start=2):
        tokens = count_tokens(history)
        if tokens > DEMO_HISTORY_BUDGET:
            history = drop_oldest_pair(history)
            log.info("[turn %d] *** TRUNCATION: oldest turn pair dropped ***", i)

        reply, history = chat_turn(client, history, question)
        tokens = count_tokens(history)
        log.info("[turn %d] tokens: %d / %d", i, tokens, DEMO_HISTORY_BUDGET)

    # Before the recall question: retrieve relevant memory and inject into system prompt
    log.info("-" * 60)
    query_embedding = embed(client, ANCHOR_QUESTION)

    # Concept: retrieve from external memory — similarity search over stored facts
    results = collection.query(query_embeddings=[query_embedding], n_results=1)
    retrieved_facts = results["documents"][0]
    similarity_distances = results["distances"][0]

    log.info("[retrieval] top result: %r", retrieved_facts[0])
    log.info("[retrieval] distance: %.4f (lower = more similar)", similarity_distances[0])

    # Concept: inject retrieved memory — prepend facts to system prompt before generation
    augmented_system = (
        SYSTEM_PROMPT
        + "\n\nRelevant context from memory:\n"
        + "\n".join(f"- {fact}" for fact in retrieved_facts)
    )

    # Final question with augmented system prompt
    log.info("[recall] %s", ANCHOR_QUESTION)
    history_with_question = history + [{"role": "user", "content": ANCHOR_QUESTION}]
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": augmented_system}] + history_with_question,
    )
    reply = response.choices[0].message.content
    log.info("[reply]  %s", reply)
    log.info("")
    log.info("Expected: model correctly recalls 'Alex' and 'Falcon' via injected memory.")
    log.info("")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready(models=[MODEL, EMBED_MODEL])
    client = build_client()

    observation_1_in_context_overflow(client)
    observation_2_external_memory_recall(client)
