# Lab: lab-context-management
# Module: memory-context
# Doc reference: docs/memory-context/context-management.md

import sys
import pathlib
import logging
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import MODEL, build_client, assert_ollama_ready, HISTORY_BUDGET
from shared.history import HistoryManager
from shared.context import apply_truncation, apply_sliding_window, compress_history, assemble_messages

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

SYSTEM_PROMPT = "You are a helpful assistant. Answer concisely in one or two sentences."

# Anchor fact planted at turn 3 — used for recall accuracy measurement
ANCHOR_TURN = 3
ANCHOR_FACT = "The project is called Nighthawk and it runs on a 16-node Kubernetes cluster."
ANCHOR_QUESTION = "What is the project name and how many nodes does the cluster have?"

# 25 filler turns covering distributed systems topics
# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In FILLER_TURNS, move ANCHOR_FACT from index 2 (turn 3) to index 22 (turn 23)
# - Observe:
#   * all three strategies retain the anchor fact — it falls within the recent window for all
#   * all three strategies PASS recall — the PASS/FAIL distinction collapses
#   * the lab no longer demonstrates that only summarization preserves early-context facts

FILLER_TURNS = [
    "What is a service mesh?",
    "How does Istio handle mTLS between services?",
    ANCHOR_FACT,  # turn 3: anchor planted
    "Explain blue-green deployments.",
    "What is a canary release strategy?",
    "How does a circuit breaker pattern prevent cascading failures?",
    "Explain the bulkhead pattern in microservices.",
    "What is a sidecar proxy?",
    "How does distributed tracing work?",
    "What is OpenTelemetry?",
    "Explain the difference between logs, metrics, and traces.",
    "What is a health check endpoint?",
    "How does a readiness probe differ from a liveness probe in Kubernetes?",
    "What is a StatefulSet in Kubernetes?",
    "How does persistent volume claiming work?",
    "What is a ConfigMap and when should you use a Secret instead?",
    "Explain horizontal pod autoscaling.",
    "What is a Helm chart?",
    "How does GitOps differ from traditional CI/CD?",
    "What is ArgoCD?",
    "Explain the operator pattern in Kubernetes.",
    "What is a custom resource definition?",
    "How does rate limiting protect API services?",
    "What is API gateway aggregation?",
    "Explain the saga pattern for distributed transactions.",
]

RECALL_TURN = 25


def run_strategy(client, strategy_name: str) -> dict:
    """
    Run 25 turns using the named strategy, then ask the recall question.
    Returns a dict with strategy name, recall reply, and event log.
    """
    log.info("")
    log.info("=" * 60)
    log.info("STRATEGY: %s", strategy_name.upper())
    log.info("=" * 60)

    manager = HistoryManager()
    events: list[str] = []

    for i, user_msg in enumerate(FILLER_TURNS, start=1):
        manager.add_user(user_msg)

        # Concept: compression threshold — apply strategy when threshold is reached
        if manager.at_threshold:
            t_start = time.monotonic()

            if strategy_name == "truncation":
                # Concept: truncation — drop oldest pairs until within budget
                manager.replace(apply_truncation(manager.history, manager.budget))
                elapsed = time.monotonic() - t_start
                event = f"[turn {i:02d}] TRUNCATION applied | latency: {elapsed*1000:.1f}ms"

            elif strategy_name == "sliding_window":
                # Concept: sliding window — keep last N pairs
                manager.replace(apply_sliding_window(manager.history, window_pairs=8))
                elapsed = time.monotonic() - t_start
                event = f"[turn {i:02d}] SLIDING WINDOW applied | latency: {elapsed*1000:.1f}ms"

            elif strategy_name == "summarization":
                # Concept: summarization — compress older turns, keep recent verbatim
                manager.replace(compress_history(client, manager.history, keep_recent_pairs=4))
                elapsed = time.monotonic() - t_start
                event = f"[turn {i:02d}] SUMMARIZATION applied | latency: {elapsed*1000:.1f}ms"

            log.info(event)
            events.append(event)

        messages = assemble_messages(SYSTEM_PROMPT, manager.history)
        response = client.chat.completions.create(model=MODEL, messages=messages)
        reply = response.choices[0].message.content
        manager.add_assistant(reply)

        log.info("[turn %02d] %s", i, manager.status_line())

    # Recall question at turn 25
    log.info("-" * 60)
    log.info("[recall] %s", ANCHOR_QUESTION)
    manager.add_user(ANCHOR_QUESTION)
    messages = assemble_messages(SYSTEM_PROMPT, manager.history)
    response = client.chat.completions.create(model=MODEL, messages=messages)
    recall_reply = response.choices[0].message.content
    log.info("[reply]  %s", recall_reply)

    return {
        "strategy": strategy_name,
        "reply": recall_reply,
        "events": events,
    }


def score_recall(reply: str) -> bool:
    """
    Concept: recall accuracy — returns True if both anchor terms are present.
    Simple keyword check; sufficient for this demonstration.
    """
    reply_lower = reply.lower()
    return "nighthawk" in reply_lower and "16" in reply_lower


def print_summary(results: list[dict]) -> None:
    log.info("")
    log.info("=" * 60)
    log.info("RECALL ACCURACY SUMMARY")
    log.info("=" * 60)
    log.info("Anchor fact (stated at turn 3): %r", ANCHOR_FACT)
    log.info("Recall question (asked at turn 25): %r", ANCHOR_QUESTION)
    log.info("-" * 60)
    for r in results:
        passed = score_recall(r["reply"])
        status = "PASS" if passed else "FAIL"
        log.info("%-20s %s", r["strategy"], status)
        log.info("  reply:  %s", r["reply"])
    log.info("-" * 60)
    log.info("Expected: summarization recall >= truncation recall")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready(models=[MODEL])
    client = build_client()

    results = []
    for strategy in ("truncation", "sliding_window", "summarization"):
        results.append(run_strategy(client, strategy))

    print_summary(results)
