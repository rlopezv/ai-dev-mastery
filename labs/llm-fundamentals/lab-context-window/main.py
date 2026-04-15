# Lab: lab-context-window
# Module: llm-fundamentals
# Doc reference: docs/llm-fundamentals/context-window.md

import logging
import os
import sys

import tiktoken

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from client import assert_ready, generate, MODEL

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

ENCODING_NAME  = "cl100k_base"
NUM_PREDICT    = int(os.getenv("NUM_PREDICT", "64"))
MAX_FILL_TOKENS = int(os.getenv("MAX_FILL_TOKENS", "512"))

# Context limits by model family (approximate). Ollama does not expose the
# limit in the /api/tags response; these values are for budget calculations.
CONTEXT_LIMITS = {
    "llama3.2":  128_000,
    "llama3":    8_192,
    "mistral":   8_192,
    "gemma2":    8_192,
}


def get_context_limit(model: str) -> int:
    """Return the approximate context window size for a known model."""
    for key, limit in CONTEXT_LIMITS.items():
        if key in model:
            return limit
    return 4_096  # conservative default


# ---------------------------------------------------------------------------
# Observation 1 — token cost per prompt component
# ---------------------------------------------------------------------------

def observe_component_costs(enc: tiktoken.Encoding) -> int:
    """
    Measure the token cost of each prompt component individually.

    Concept: all components share the same context budget.
    Each component's token cost is subtracted from the available window.
    """
    log.info("=== Observation 1: Token cost per component ===")

    system   = "You are a helpful assistant. Be concise."
    history  = "User: What is a transformer?\nAssistant: A transformer is a neural network architecture that uses self-attention to process sequences in parallel."
    user     = "What is the difference between tokenization and embedding?"

    system_tokens  = len(enc.encode(system))
    history_tokens = len(enc.encode(history))
    user_tokens    = len(enc.encode(user))
    total_input    = system_tokens + history_tokens + user_tokens
    total          = total_input + NUM_PREDICT

    log.info("  System prompt:       %4d tokens", system_tokens)
    log.info("  Conversation history:%4d tokens", history_tokens)
    log.info("  User message:        %4d tokens", user_tokens)
    log.info("  ─────────────────────────────")
    log.info("  Total input:         %4d tokens", total_input)
    log.info("  Max output:          %4d tokens", NUM_PREDICT)
    log.info("  Grand total:         %4d tokens", total)

    return total_input


# ---------------------------------------------------------------------------
# Observation 2 — verify API token count matches pre-send estimate
# ---------------------------------------------------------------------------

def observe_estimate_accuracy(enc: tiktoken.Encoding) -> None:
    """
    Send a prompt to Ollama and compare prompt_eval_count with the pre-send estimate.

    Concept: the context assembler uses the same tokenization to count tokens.
    The estimate and the API-reported count should agree within a small margin
    (difference stems from chat template framing added by Ollama).
    """
    log.info("\n=== Observation 2: Estimate vs API token count ===")

    prompt = "Explain what self-attention is in one sentence."
    estimated = len(enc.encode(prompt))

    log.info("  Estimated (tiktoken):  %d tokens", estimated)

    result = generate(prompt, temperature=0.0, num_predict=NUM_PREDICT)
    reported = result.get("prompt_eval_count", -1)

    log.info("  Reported (Ollama):     %d tokens", reported)
    delta = abs(estimated - reported)
    log.info("  Delta:                 %d tokens", delta)

    if delta <= 10:
        log.info("  ✓ Estimates agree within 10 tokens (chat template overhead expected)")
    else:
        log.info("  ! Large delta — different tokenizer or model framing adds overhead")


# ---------------------------------------------------------------------------
# Observation 3 — progressive context fill
# ---------------------------------------------------------------------------

def observe_progressive_fill(enc: tiktoken.Encoding, context_limit: int) -> None:
    """
    Build progressively longer prompts and observe how token counts grow.

    Concept: each additional word consumes tokens from the fixed budget.
    The rate of consumption depends on the content type.
    """
    log.info("\n=== Observation 3: Progressive context fill (limit: %d) ===", context_limit)

    base_sentence = "The transformer architecture uses self-attention to process all tokens simultaneously. "
    tokens_per_sentence = len(enc.encode(base_sentence))
    log.info("  Tokens per appended sentence: %d", tokens_per_sentence)

    prompt = ""
    step = 0
    while True:
        prompt += base_sentence
        step += 1
        total_tokens = len(enc.encode(prompt))
        budget_used_pct = (total_tokens / context_limit) * 100

        if step <= 3 or total_tokens > MAX_FILL_TOKENS - tokens_per_sentence:
            log.info(
                "  Step %3d — %5d tokens  (%5.1f%% of %d-token limit)",
                step, total_tokens, budget_used_pct, context_limit,
            )

        # Concept: context truncation is silent — stop before exceeding limit
        if total_tokens + NUM_PREDICT + tokens_per_sentence > MAX_FILL_TOKENS:
            log.info("  → Stopping fill at %d tokens to stay within MAX_FILL_TOKENS=%d",
                     total_tokens, MAX_FILL_TOKENS)
            break

    log.info("  Final prompt: %d tokens", len(enc.encode(prompt)))
    result = generate(prompt + " Summarize the above in one word:", temperature=0.0, num_predict=NUM_PREDICT)
    log.info("  prompt_eval_count (API): %d", result.get("prompt_eval_count", -1))
    log.info("  Response: %r", result["response"][:80])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ready()
    enc = tiktoken.get_encoding(ENCODING_NAME)
    context_limit = get_context_limit(MODEL)
    log.info("Model: %s  |  Approximate context limit: %d tokens\n", MODEL, context_limit)

    observe_component_costs(enc)
    observe_estimate_accuracy(enc)
    observe_progressive_fill(enc, context_limit)

    log.info("\nDone. Review docs/llm-fundamentals/context-window.md §3 for use-case benchmarks.")
