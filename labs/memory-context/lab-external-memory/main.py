# Lab: lab-external-memory
# Module: memory-context
# Doc reference: docs/memory-context/external-memory.md

import sys
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import MODEL, EMBED_MODEL, build_client, assert_ollama_ready
from shared.memory import MemoryStore

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def run_1_write(store: MemoryStore, client) -> None:
    """
    Run 1 — write an episode and a semantic fact.
    Expected: entries stored, count increases.
    """
    log.info("=" * 60)
    log.info("RUN 1 — Write episode and semantic fact")
    log.info("=" * 60)

    # Concept: episodic memory — store a conversation turn with timestamp
    episode_text = (
        "User said: I am building a fraud detection pipeline. "
        "It processes 50,000 transactions per second using a streaming architecture."
    )
    eid = store.add_episode(client, episode_text, episode_id="ep-fraud-pipeline")
    log.info("[episode] stored id=%r | count=%d", eid, store.episode_count())

    # Concept: semantic memory — store a named fact, keyed for upsert
    store.upsert_fact(client, key="user_domain", value="fraud detection, streaming systems")
    log.info("[fact]    stored key='user_domain' | count=%d", store.fact_count())

    # Verify by retrieving immediately
    episodes = store.retrieve_episodes(client, "fraud detection pipeline", n_results=1)
    log.info("[verify]  episode retrieved: distance=%.4f", episodes[0]["distance"])
    assert episodes[0]["distance"] < 0.30, "Episode retrieval failed — distance too high"

    facts = store.retrieve_facts(client, "what domain is the user working in", n_results=1)
    log.info("[verify]  fact retrieved: %r → %r | distance=%.4f",
             facts[0]["key"], facts[0]["value"], facts[0]["distance"])

    log.info("[run 1]   PASS — entries written and immediately retrievable")


def run_2_cross_session_recall(store: MemoryStore, client) -> None:
    """
    Run 2 — retrieve the episode written in run 1 without re-writing it.
    Expected: episode from run 1 retrieved with similarity score >= 0.75 (distance <= 0.25).
    """
    log.info("")
    log.info("=" * 60)
    log.info("RUN 2 — Cross-session recall of episode from run 1")
    log.info("=" * 60)

    # Concept: cross-session recall — ChromaDB PersistentClient data survives process restart
    log.info("[state]   episode_count=%d, fact_count=%d",
             store.episode_count(), store.fact_count())

    if store.episode_count() == 0:
        log.warning("[skip]    No episodes found — run 1 has not been executed yet.")
        log.warning("          Run 'python main.py' twice to see cross-session recall.")
        return

    episodes = store.retrieve_episodes(client, "streaming transaction processing", n_results=1)
    ep = episodes[0]
    log.info("[retrieval] id=%r", ep["id"])
    log.info("[retrieval] distance=%.4f", ep["distance"])
    log.info("[retrieval] text=%r", ep["text"][:120])

    # Concept: retrieve from external memory — distance <= 0.25 means similarity >= 0.75
    if ep["distance"] <= 0.25:
        log.info("[run 2]   PASS — cross-session recall succeeded (distance <= 0.25)")
    else:
        log.warning("[run 2]   distance=%.4f exceeds threshold 0.25 — check embedding model", ep["distance"])


def run_3_upsert_fact(store: MemoryStore, client) -> None:
    """
    Run 3 — update the semantic fact written in run 1.
    Expected: updated fact retrieved instead of original.
    """
    log.info("")
    log.info("=" * 60)
    log.info("RUN 3 — Upsert: update existing semantic fact")
    log.info("=" * 60)

    # Concept: upsert — ChromaDB overwrites the document with the same ID
    original_facts = store.retrieve_facts(client, "what domain is the user working in", n_results=1)
    if original_facts:
        log.info("[before]  key=%r value=%r", original_facts[0]["key"], original_facts[0]["value"])

    store.upsert_fact(
        client,
        key="user_domain",
        value="fraud detection, streaming systems, real-time ML inference",
    )
    log.info("[upsert]  key='user_domain' updated with extended value")

    updated_facts = store.retrieve_facts(client, "what domain is the user working in", n_results=1)
    log.info("[after]   key=%r value=%r", updated_facts[0]["key"], updated_facts[0]["value"])

    if "real-time ml inference" in updated_facts[0]["value"].lower():
        log.info("[run 3]   PASS — updated fact retrieved correctly")
    else:
        log.warning("[run 3]   value does not contain expected update — check upsert logic")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready(models=[MODEL, EMBED_MODEL])
    client = build_client()

    # Concept: PersistentClient — shared store across all three runs in this session
    store = MemoryStore()

    run_1_write(store, client)
    run_2_cross_session_recall(store, client)
    run_3_upsert_fact(store, client)

    log.info("")
    log.info("Run this script a second time to observe true cross-session recall in run 2.")
