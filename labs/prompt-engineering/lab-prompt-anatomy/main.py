# Lab: lab-prompt-anatomy
# Module: prompt-engineering
# Doc reference: docs/prompt-engineering/prompt-anatomy.md

import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from config import OLLAMA_MODEL, assert_ollama_ready, build_client, complete

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

INPUT_TEXT = "The new framework promises faster builds but the migration guide is incomplete."
RUNS = 5


# ---------------------------------------------------------------------------
# Prompt configurations — one per observation
# ---------------------------------------------------------------------------

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In build_complete_prompt(), remove the enumerated options from the format spec:
#     change "Respond with one word only: positive, negative, or neutral."
#     to     "Respond with one word only."
# - Observe:
#   * model invents its own category labels ("mixed", "ambivalent", "critical")
#   * unique response count increases even for Observation 1
#   * format spec must enumerate valid outputs — open-ended instructions allow vocabulary drift

def build_complete_prompt(text: str) -> list[dict]:
    """
    All five components present: system, instruction, context, output format.

    Concept: a complete prompt produces consistent, parseable output.
    """
    return [
        {
            "role": "system",
            "content": "You are a sentiment classifier.",
        },
        {
            "role": "user",
            "content": (
                f"Classify the sentiment of the following text.\n\n"
                f"Text: {text}\n\n"
                f"Respond with one word only: positive, negative, or neutral."
            ),
        },
    ]


def build_no_format_prompt(text: str) -> list[dict]:
    """
    Output format specification removed.

    Concept: without explicit format, the model chooses its own —
    producing prose, explanations, or varying labels across runs.
    """
    return [
        {
            "role": "system",
            "content": "You are a sentiment classifier.",
        },
        {
            "role": "user",
            "content": f"Classify the sentiment of the following text.\n\nText: {text}",
        },
    ]


def build_no_instruction_prompt(text: str) -> list[dict]:
    """
    Instruction removed — only context and output format remain.

    Concept: without an explicit task directive, the model guesses
    what to do with the context.
    """
    return [
        {
            "role": "system",
            "content": "You are a sentiment classifier.",
        },
        {
            "role": "user",
            "content": (
                f"Text: {text}\n\n"
                f"Respond with one word only: positive, negative, or neutral."
            ),
        },
    ]


def build_no_system_prompt(text: str) -> list[dict]:
    """
    System prompt removed — no role, no behavioral constraint.

    Concept: without a system prompt, the model may answer in any register
    or produce explanations rather than a constrained classification.
    """
    return [
        {
            "role": "user",
            "content": (
                f"Classify the sentiment of the following text.\n\n"
                f"Text: {text}\n\n"
                f"Respond with one word only: positive, negative, or neutral."
            ),
        },
    ]


# ---------------------------------------------------------------------------
# Observation runner
# ---------------------------------------------------------------------------

def run_observation(label: str, messages: list[dict], runs: int = RUNS) -> list[str]:
    """Run the same prompt N times and collect responses."""
    client = build_client()
    responses = []
    for i in range(1, runs + 1):
        text = complete(client, messages, temperature=0.3)
        responses.append(text.strip())
        log.info("  Run %d: %r", i, text.strip())
    unique = set(r.lower() for r in responses)
    log.info("  Unique responses: %d / %d  → %s", len(unique), runs, sorted(unique))
    return responses


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready()
    log.info("Model: %s\nInput: %r\n", OLLAMA_MODEL, INPUT_TEXT)

    log.info("=== Observation 1: Complete prompt (all components) ===")
    run_observation("complete", build_complete_prompt(INPUT_TEXT))

    log.info("\n=== Observation 2: No output format specification ===")
    run_observation("no_format", build_no_format_prompt(INPUT_TEXT))

    log.info("\n=== Observation 3: No instruction ===")
    run_observation("no_instruction", build_no_instruction_prompt(INPUT_TEXT))

    log.info("\n=== Observation 4: No system prompt ===")
    run_observation("no_system", build_no_system_prompt(INPUT_TEXT))

    log.info(
        "\nExpected: Obs 1 has fewest unique responses; "
        "Obs 2 has the most variation in format. "
        "Review against docs/prompt-engineering/prompt-anatomy.md."
    )
