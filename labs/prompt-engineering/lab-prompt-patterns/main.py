# Lab: lab-prompt-patterns
# Module: prompt-engineering
# Doc reference: docs/prompt-engineering/prompt-patterns.md

import json
import logging
import os
import re
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from config import assert_ollama_ready, build_client, complete

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pattern 1 — Role prompting
# ---------------------------------------------------------------------------

def build_role_prompt(role: str, domain: str, tone: str, constraint: str, task: str) -> list[dict]:
    """
    Concept: assigning a specific professional identity constrains response
    vocabulary, tone, and assumed knowledge base.
    """
    system = (
        f"You are a {role} with expertise in {domain}. "
        f"Your responses are {tone}. "
        f"You do not {constraint}."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": task},
    ]


# ---------------------------------------------------------------------------
# Pattern 2 — Output format specification
# ---------------------------------------------------------------------------

def build_format_prompt(input_text: str) -> list[dict]:
    """
    Concept: explicit JSON schema in the prompt constrains response structure
    so the output can be parsed programmatically without fragile string extraction.
    """
    return [
        {
            "role": "user",
            "content": (
                f'Analyze the following text and respond in this exact JSON format:\n\n'
                f'{{\n'
                f'  "sentiment": "positive" or "negative" or "neutral",\n'
                f'  "confidence": a number between 0.0 and 1.0,\n'
                f'  "key_phrases": ["phrase1", "phrase2"],\n'
                f'  "summary": "one sentence"\n'
                f'}}\n\n'
                f'Text: {input_text}\n\n'
                f'Respond with valid JSON only. No explanation outside the JSON block.'
            ),
        },
    ]


def extract_json(text: str) -> dict:
    """
    Extract JSON from response text, tolerating prose before/after the block.

    Concept: lenient extraction for format-spec prompts — small models may
    add surrounding text despite the instruction.
    """
    # Try direct parse first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    # Extract first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    raise ValueError(f"No valid JSON found in response: {text[:200]}")


# ---------------------------------------------------------------------------
# Pattern 3 — Step-by-step instruction
# ---------------------------------------------------------------------------

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In build_steps_prompt(), reorder the step numbers in the prompt to 1, 3, 2, 4
# - Observe:
#   * check_steps_present() still returns True — all four labels appear
#   * but content is scrambled: correctness issues under "Step 3", performance under "Step 2"
#   * step numbering enforces section identity, not intended sequence

def build_steps_prompt(code: str) -> list[dict]:
    """
    Concept: prescribing an explicit step sequence ensures all review dimensions
    are covered and each section can be extracted by label.
    """
    return [
        {
            "role": "system",
            "content": "You are a senior software engineer conducting a code review.",
        },
        {
            "role": "user",
            "content": (
                f"Review the following code using this process:\n\n"
                f"Step 1: Describe what the code does (1–2 sentences).\n"
                f"Step 2: List correctness issues (bugs, unhandled edge cases). "
                f"If none, write 'None identified.'\n"
                f"Step 3: List performance concerns. If none, write 'None identified.'\n"
                f"Step 4: State your verdict: approve, request-changes, or reject.\n\n"
                f"Label each step. Follow the order.\n\n"
                f"Code:\n{code}"
            ),
        },
    ]


def check_steps_present(response: str) -> bool:
    """Verify all four labeled steps appear in the response."""
    return all(f"Step {i}" in response for i in range(1, 5))


# ---------------------------------------------------------------------------
# Benchmark harness
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkCase:
    input_data: str
    expected: str  # expected label or key for validation


@dataclass
class BenchmarkResult:
    total: int
    correct: int
    failures: list[dict]

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0


def run_benchmark(name: str, cases: list[BenchmarkCase], build_fn, check_fn) -> BenchmarkResult:
    """
    Concept: offline accuracy validation — run a pattern against known inputs
    before deploying it. Catches regressions when model or pattern changes.
    """
    client = build_client()
    failures = []
    correct = 0
    for case in cases:
        messages = build_fn(case.input_data)
        response = complete(client, messages, temperature=0.0)
        ok = check_fn(response, case.expected)
        if ok:
            correct += 1
        else:
            failures.append({"input": case.input_data[:60], "expected": case.expected,
                              "actual": response[:80]})
    result = BenchmarkResult(total=len(cases), correct=correct, failures=failures)
    log.info("[%s] Accuracy: %d/%d = %.0f%%", name, correct, len(cases), result.accuracy * 100)
    for f in result.failures:
        log.info("  FAIL  input=%r  expected=%r  got=%r", f["input"], f["expected"], f["actual"])
    return result


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

SENTIMENT_CASES = [
    BenchmarkCase("The delivery was fast and the product works perfectly.", "positive"),
    BenchmarkCase("Total waste of money, broke after one use.", "negative"),
    BenchmarkCase("The item arrived on time. Nothing special.", "neutral"),
    BenchmarkCase("Outstanding quality, highly recommend to everyone!", "positive"),
    BenchmarkCase("Disappointed with the customer service response.", "negative"),
]

CODE_SNIPPET = """\
def divide(a, b):
    return a / b

result = divide(10, 0)
print(result)
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready()
    client = build_client()

    # --- Pattern 1: Role prompting ---
    log.info("=== Pattern 1: Role prompting ===")
    messages = build_role_prompt(
        role="senior distributed systems architect",
        domain="microservices and event-driven architecture",
        tone="technical and precise",
        constraint="recommend technologies without explaining the trade-offs",
        task="What are the main risks of using synchronous REST calls between microservices?",
    )
    response = complete(client, messages)
    log.info("Response:\n%s\n", response)

    # --- Pattern 2: Output format specification (benchmark) ---
    log.info("=== Pattern 2: Output format specification ===")

    def check_format(response: str, expected_sentiment: str) -> bool:
        try:
            data = extract_json(response)
            # Concept: check structure and sentiment label
            return (
                "sentiment" in data
                and "confidence" in data
                and "key_phrases" in data
                and "summary" in data
                and data["sentiment"] == expected_sentiment
            )
        except ValueError:
            return False

    run_benchmark(
        "format-spec",
        SENTIMENT_CASES,
        build_format_prompt,
        check_format,
    )

    # --- Pattern 3: Step-by-step instruction ---
    log.info("\n=== Pattern 3: Step-by-step instruction ===")
    messages = build_steps_prompt(CODE_SNIPPET)
    response = complete(client, messages)
    all_steps = check_steps_present(response)
    log.info("Response:\n%s", response)
    log.info("\nAll steps labeled: %s", "✓" if all_steps else "✗ — some steps missing")

    log.info(
        "\nDone. Review the patterns against docs/prompt-engineering/prompt-patterns.md."
    )
