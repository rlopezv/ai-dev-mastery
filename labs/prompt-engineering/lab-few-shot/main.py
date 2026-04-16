# Lab: lab-few-shot
# Module: prompt-engineering
# Doc reference: docs/prompt-engineering/few-shot.md

import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from config import assert_ollama_ready, build_client, complete

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Test dataset — topic classification (4 classes)
# ---------------------------------------------------------------------------

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - Change some EXAMPLES labels to use inconsistent casing:
#     "economics" → "Economics", "sports" → "Sports" in 2–3 entries
# - Observe:
#   * model mirrors inconsistent casing from examples
#   * predicted == expected fails for capitalized outputs despite correct classification
#   * accuracy drops even though semantic classification is correct — label format drift
#     causes evaluation failures

EXAMPLES = [
    ("The central bank raised interest rates by 50 basis points.", "economics"),
    ("The championship match ended in a penalty shootout.", "sports"),
    ("A new vulnerability was found in the popular open-source library.", "technology"),
    ("The senate passed the infrastructure spending bill.", "politics"),
    ("The team signed a record-breaking transfer deal.", "sports"),
    ("Researchers unveiled a new large language model architecture.", "technology"),
]

TEST_CASES = [
    ("The stock market fell sharply after the Fed announcement.", "economics"),
    ("The striker scored a hat-trick in the final ten minutes.", "sports"),
    ("The company released a patch to fix the remote code execution flaw.", "technology"),
    ("The prime minister announced early elections.", "politics"),
    ("Inflation data showed prices rising faster than expected.", "economics"),
    ("The team won the league title for the third consecutive year.", "sports"),
    ("A critical zero-day exploit was discovered in widely used software.", "technology"),
    ("Lawmakers debated the new immigration bill in a late-night session.", "politics"),
]

CLASSES = "economics, sports, technology, or politics"


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def build_zero_shot(text: str) -> list[dict]:
    """
    Concept: instruction only — no examples. Model relies entirely on training.
    """
    return [
        {
            "role": "system",
            "content": "You are a topic classifier.",
        },
        {
            "role": "user",
            "content": (
                f"Classify the following text into one of these categories: {CLASSES}.\n\n"
                f"Text: {text}\n\n"
                f"Respond with the category name only."
            ),
        },
    ]


def build_few_shot(text: str, n_shots: int) -> list[dict]:
    """
    Concept: n labeled examples anchor the output pattern before the target input.
    The model infers label format and class boundaries from the examples.
    """
    shots = EXAMPLES[:n_shots]
    examples_block = "\n\n".join(
        f"Text: {inp}\nCategory: {label}" for inp, label in shots
    )
    return [
        {
            "role": "system",
            "content": "You are a topic classifier.",
        },
        {
            "role": "user",
            "content": (
                f"Classify text into one of these categories: {CLASSES}.\n\n"
                f"{examples_block}\n\n"
                f"Text: {text}\n"
                f"Category:"
            ),
        },
    ]


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate(mode: str, build_fn, test_cases: list[tuple]) -> None:
    """Run all test cases and print per-case result and overall accuracy."""
    client = build_client()
    correct = 0
    log.info("\n--- %s ---", mode)
    for text, expected in test_cases:
        raw = complete(client, build_fn(text), temperature=0.0)
        # Concept: normalize — model may return "Technology" or "technology"
        predicted = raw.strip().lower().split()[0].rstrip(".,")
        match = predicted == expected
        if match:
            correct += 1
        status = "✓" if match else "✗"
        log.info(
            "  %s  expected=%-12s  got=%r",
            status, expected, raw.strip()[:40],
        )
    accuracy = correct / len(test_cases)
    log.info("Accuracy: %d/%d = %.0f%%", correct, len(test_cases), accuracy * 100)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready()

    log.info("=== Few-Shot Prompting — Topic Classification ===")
    log.info("Test set: %d items   Classes: %s\n", len(TEST_CASES), CLASSES)

    # Concept: compare zero-shot, one-shot, and three-shot accuracy
    evaluate("Zero-shot (0 examples)", lambda t: build_zero_shot(t), TEST_CASES)
    evaluate("One-shot  (1 example) ", lambda t: build_few_shot(t, 1), TEST_CASES)
    evaluate("Few-shot  (3 examples)", lambda t: build_few_shot(t, 3), TEST_CASES)

    log.info(
        "\nExpected: accuracy increases with shot count. "
        "Review against docs/prompt-engineering/few-shot.md."
    )
