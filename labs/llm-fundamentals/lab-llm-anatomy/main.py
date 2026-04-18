# Lab: lab-llm-anatomy
# Module: llm-fundamentals
# Doc reference: docs/llm-fundamentals/llm-architecture.md

import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from client import assert_ready, generate, list_models, MODEL

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

NUM_PREDICT = int(os.getenv("NUM_PREDICT", "128"))


# ---------------------------------------------------------------------------
# Observation 1 — available models
# ---------------------------------------------------------------------------

def observe_model_list() -> None:
    """Print all models Ollama knows about."""
    log.info("=== Observation 1: Available models ===")
    for model in list_models():
        size_mb = model.get("size", 0) // (1024 * 1024)
        log.info("  name=%-30s  size=%d MB", model["name"], size_mb)


# ---------------------------------------------------------------------------
# Observation 2 — single generation with full metadata
# ---------------------------------------------------------------------------

def observe_generation(prompt: str) -> dict:
    """
    Send one prompt and print the complete response plus metadata.

    Concept: the response contains both the generated text and pipeline
    telemetry — token counts and timing — produced by the autoregressive loop.
    """
    log.info("\n=== Observation 2: Single generation ===")
    log.info("Model:  %s", MODEL)
    log.info("Prompt: %r", prompt)

    result = generate(prompt, temperature=0.0, num_predict=NUM_PREDICT)

    log.info("\n--- Response ---")
    log.info("%s", result["response"])

    log.info("\n--- Metadata ---")
    log.info("  prompt_eval_count (input tokens):  %d", result.get("prompt_eval_count", -1))
    log.info("  eval_count        (output tokens): %d", result.get("eval_count", -1))
    log.info("  total_duration    (nanoseconds):   %d", result.get("total_duration", -1))
    log.info("  model:                             %s", result.get("model", "unknown"))

    return result


# ---------------------------------------------------------------------------
# Observation 3 — prompt_eval_count is stable for a fixed input
# ---------------------------------------------------------------------------

def observe_token_count_stability(prompt: str, runs: int = 3) -> None:
    """
    Run the same prompt multiple times and confirm prompt_eval_count is identical.

    Concept: the tokenizer encodes text deterministically; the same input always
    produces the same number of input tokens, regardless of how many times it is sent.
    """
    log.info("\n=== Observation 3: Token count stability (%d runs) ===", runs)
    counts = []
    for i in range(1, runs + 1):
        result = generate(prompt, temperature=0.0, num_predict=1)
        count = result.get("prompt_eval_count", -1)
        counts.append(count)
        log.info("  Run %d: prompt_eval_count = %d", i, count)

    if len(set(counts)) == 1:
        log.info("  ✓ Stable — all runs report %d input tokens", counts[0])
    else:
        log.info("  ✗ Unstable — counts varied: %s", counts)


# ---------------------------------------------------------------------------
# Observation 4 — eval_count scales with num_predict
# ---------------------------------------------------------------------------

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In observe_output_token_scaling(), add 1 to the limits list:
#   for limit in (1, 8, 32, 128)
# - Observe:
#   * eval_count=1 for all prompts — loop stops after a single token
#   * Response is always a single token fragment, never a complete sentence
#   * Shows num_predict is a hard ceiling: generation stops immediately when reached

def observe_output_token_scaling() -> None:
    """
    Request different num_predict values and confirm eval_count reflects them.

    Concept: the autoregressive loop runs until num_predict tokens are generated
    or a stop token is hit, whichever comes first.
    """
    log.info("\n=== Observation 4: Output token scaling ===")
    prompt = "List the planets in the solar system:"
    for limit in (8, 32, 128):
        result = generate(prompt, temperature=0.0, num_predict=limit)
        log.info(
            "  num_predict=%-4d → eval_count=%-4d  response=%r",
            limit,
            result.get("eval_count", -1),
            result["response"][:60],
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ready()
    observe_model_list()
    prompt = "The transformer architecture processes tokens by computing self-attention"
    observe_generation(prompt)
    observe_token_count_stability(prompt)
    observe_output_token_scaling()
    log.info("\nDone. Review the metadata fields above against docs/llm-fundamentals/llm-architecture.md.")
