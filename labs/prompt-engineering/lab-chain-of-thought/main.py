# Lab: lab-chain-of-thought
# Module: prompt-engineering
# Doc reference: docs/prompt-engineering/chain-of-thought.md

import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from config import assert_ollama_ready, build_client, complete

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - Change COT_MARKER = "Answer:" to COT_MARKER = "ANSWER:"
# - Observe:
#   * parse_cot_answer raises ValueError for every problem
#   * model writes "Answer:" (mixed case), not "ANSWER:"
#   * CoT correct count drops to 0 — extraction markers must match model output exactly

COT_MARKER = "Answer:"

# ---------------------------------------------------------------------------
# Multi-step reasoning problems with known answers
# ---------------------------------------------------------------------------

PROBLEMS = [
    {
        "question": (
            "A warehouse has 240 boxes. Workers move 3/8 of them to truck A "
            "and 1/4 of the remainder to truck B. How many boxes are left in the warehouse?"
        ),
        "answer": "105",
    },
    {
        "question": (
            "Alice is twice as old as Bob. In 5 years, the sum of their ages will be 49. "
            "How old is Alice now?"
        ),
        "answer": "26",
    },
    {
        "question": (
            "A train travels 120 km at 60 km/h, then 180 km at 90 km/h. "
            "What is the average speed for the entire journey?"
        ),
        "answer": "75",
    },
]


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def build_direct_prompt(question: str) -> list[dict]:
    """
    Concept: direct answer request — model must compress all reasoning into
    the answer token. Fails on multi-step problems.
    """
    return [
        {
            "role": "user",
            "content": f"{question}\n\nAnswer with a number only.",
        },
    ]


def build_cot_prompt(question: str) -> list[dict]:
    """
    Concept: step-by-step elicitation with an extraction marker.
    Each reasoning step becomes context for the next.
    The "Answer:" marker enables reliable final-answer extraction.
    """
    return [
        {
            "role": "user",
            "content": (
                f"{question}\n\n"
                f"Let's think step by step.\n"
                f"At the end, state your final answer on a new line starting with '{COT_MARKER}'"
            ),
        },
    ]


# ---------------------------------------------------------------------------
# Answer extraction
# ---------------------------------------------------------------------------

def parse_cot_answer(response_text: str) -> str:
    """
    Extract the final answer after the CoT marker.

    Concept: strict extraction — raises ValueError if the marker is absent,
    rather than silently returning a wrong or empty result.
    """
    if COT_MARKER not in response_text:
        raise ValueError(
            f"CoT marker '{COT_MARKER}' not found in response:\n{response_text}"
        )
    return response_text.split(COT_MARKER, 1)[1].strip().split("\n")[0].strip()


def normalize_answer(text: str) -> str:
    """Extract the first numeric token from a response for comparison."""
    import re
    match = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
    return match.group().replace(",", "") if match else text.strip()


# ---------------------------------------------------------------------------
# Observation runner
# ---------------------------------------------------------------------------

def run_problem(problem: dict, client) -> None:
    question = problem["question"]
    expected = problem["answer"]

    log.info("  Problem: %s", question)

    # Direct answer
    direct_raw = complete(client, build_direct_prompt(question), temperature=0.0)
    direct_answer = normalize_answer(direct_raw)
    direct_correct = direct_answer == expected
    log.info("  Direct  → %r  (normalized: %s)  %s",
             direct_raw.strip()[:60], direct_answer, "✓" if direct_correct else "✗")

    # Chain-of-thought
    cot_raw = complete(client, build_cot_prompt(question), temperature=0.0)
    try:
        cot_extracted = parse_cot_answer(cot_raw)
        cot_answer = normalize_answer(cot_extracted)
        cot_correct = cot_answer == expected
        log.info("  CoT     → extracted: %r  (normalized: %s)  %s",
                 cot_extracted[:60], cot_answer, "✓" if cot_correct else "✗")
    except ValueError as e:
        log.info("  CoT     → marker not found: %s", e)
        cot_correct = False

    log.info("  Expected: %s", expected)
    return direct_correct, cot_correct


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready()
    client = build_client()

    log.info("=== Chain-of-Thought vs Direct Answering ===\n")

    direct_total, cot_total = 0, 0
    for i, problem in enumerate(PROBLEMS, 1):
        log.info("--- Problem %d ---", i)
        d_correct, c_correct = run_problem(problem, client)
        if d_correct:
            direct_total += 1
        if c_correct:
            cot_total += 1
        log.info("")

    n = len(PROBLEMS)
    log.info("Results:  Direct %d/%d   CoT %d/%d", direct_total, n, cot_total, n)
    log.info(
        "\nExpected: CoT correct ≥ Direct correct. "
        "Review reasoning traces against docs/prompt-engineering/chain-of-thought.md."
    )
