# Lab: lab-inference-parameters
# Module: llm-fundamentals
# Doc reference: docs/llm-fundamentals/inference-parameters.md

import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from client import assert_ready, generate, MODEL

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

NUM_PREDICT = int(os.getenv("NUM_PREDICT", "64"))
RUNS = 3


# ---------------------------------------------------------------------------
# Observation 1 — temperature=0 produces deterministic output
# ---------------------------------------------------------------------------

def observe_determinism(prompt: str) -> None:
    """
    Run the same prompt at temperature=0 multiple times.

    Concept: temperature=0 is greedy decoding — the highest-probability token
    is always selected. Output is deterministic for a fixed model version.
    """
    log.info("=== Observation 1: Determinism at temperature=0 ===")
    log.info("Prompt: %r\n", prompt)

    responses = []
    for i in range(1, RUNS + 1):
        result = generate(prompt, temperature=0.0, num_predict=NUM_PREDICT)
        r = result["response"].strip()
        responses.append(r)
        log.info("  Run %d: %r", i, r[:80])

    if len(set(responses)) == 1:
        log.info("\n  ✓ All %d runs produced identical output", RUNS)
    else:
        log.info("\n  ! Outputs differ — check model version consistency")


# ---------------------------------------------------------------------------
# Observation 2 — high temperature produces output variance
# ---------------------------------------------------------------------------

def observe_variance(prompt: str) -> None:
    """
    Run the same prompt at temperature=1.0 multiple times.

    Concept: temperature=1.0 uses the model's native distribution without
    sharpening. Sampling introduces randomness — each run is an independent draw.
    """
    log.info("\n=== Observation 2: Variance at temperature=1.0 ===")
    log.info("Prompt: %r\n", prompt)

    responses = []
    for i in range(1, RUNS + 1):
        result = generate(prompt, temperature=1.0, num_predict=NUM_PREDICT)
        r = result["response"].strip()
        responses.append(r)
        log.info("  Run %d: %r", i, r[:80])

    unique = len(set(responses))
    log.info("\n  Unique responses: %d / %d", unique, RUNS)
    if unique > 1:
        log.info("  ✓ Output varies as expected at temperature=1.0")
    else:
        log.info("  ! All outputs identical — model may have very peaked distribution for this prompt")


# ---------------------------------------------------------------------------
# Observation 3 — top_k restricts the candidate pool
# ---------------------------------------------------------------------------

def observe_top_k(prompt: str) -> None:
    """
    Compare output at top_k=1 vs top_k=100 with the same temperature.

    Concept: top_k=1 forces greedy selection regardless of temperature.
    Larger top_k widens the pool, making temperature's effect more visible.
    """
    log.info("\n=== Observation 3: top_k effect ===")
    log.info("Prompt: %r\n", prompt)

    for top_k in (1, 10, 100):
        result = generate(prompt, temperature=1.0, top_k=top_k, num_predict=NUM_PREDICT)
        log.info("  top_k=%-4d → %r", top_k, result["response"].strip()[:80])

    log.info("\n  Note: top_k=1 at any temperature is equivalent to greedy decoding")


# ---------------------------------------------------------------------------
# Observation 4 — top_p restricts via cumulative probability threshold
# ---------------------------------------------------------------------------

def observe_top_p(prompt: str) -> None:
    """
    Compare output at top_p=0.1 vs top_p=0.99.

    Concept: top_p selects the smallest set of tokens whose cumulative
    probability reaches p. Low p → very narrow pool; high p → wide pool.
    """
    log.info("\n=== Observation 4: top_p effect ===")
    log.info("Prompt: %r\n", prompt)

    for top_p in (0.1, 0.5, 0.95, 0.99):
        result = generate(prompt, temperature=1.0, top_k=100, top_p=top_p, num_predict=NUM_PREDICT)
        log.info("  top_p=%.2f → %r", top_p, result["response"].strip()[:80])


# ---------------------------------------------------------------------------
# Observation 5 — factual prompt at temperature=0 vs temperature=1.5
# ---------------------------------------------------------------------------

def observe_temperature_on_factual(prompt: str) -> None:
    """
    Apply different temperatures to a factual question.

    Concept: temperature does not affect what the model knows.
    High temperature on a factual prompt increases the chance of selecting
    a wrong token that is merely plausible.
    """
    log.info("\n=== Observation 5: Temperature on a factual prompt ===")
    log.info("Prompt: %r\n", prompt)

    for temp in (0.0, 0.7, 1.5):
        result = generate(prompt, temperature=temp, num_predict=NUM_PREDICT)
        log.info("  temperature=%.1f → %r", temp, result["response"].strip()[:100])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ready()
    log.info("Model: %s | num_predict: %d | runs per observation: %d\n", MODEL, NUM_PREDICT, RUNS)

    creative_prompt  = "Once upon a time in a futuristic city,"
    factual_prompt   = "The capital of Japan is"

    observe_determinism(creative_prompt)
    observe_variance(creative_prompt)
    observe_top_k(creative_prompt)
    observe_top_p(creative_prompt)
    observe_temperature_on_factual(factual_prompt)

    log.info("\nDone. Compare observations with docs/llm-fundamentals/inference-parameters.md §2–§4.")
