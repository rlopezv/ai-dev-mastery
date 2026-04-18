# Lab: lab-structured-outputs
# Module: structured-outputs
# Doc reference: docs/structured-outputs/structured-outputs.md

import json
import logging
import sys
from typing import Literal

from pydantic import BaseModel, Field

sys.path.insert(0, ".")
from shared.config import (  # noqa: E402
    MAX_TOKENS,
    OLLAMA_MODEL,
    assert_ollama_ready,
    build_client,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In ReviewSummary, change sentiment type from Literal["positive", "neutral", "negative"] to str
# - Observe:
#   * parse success stays 5/5 — Pydantic still returns a typed object
#   * sentiment may contain non-standard values: "mixed", "somewhat negative", "mostly positive"
#   * vocabulary bounds are lost — the three-way classification is no longer enforced
#   * evaluation logic comparing against "positive"/"neutral"/"negative" fails despite correct classification

# ---------------------------------------------------------------------------
# Schema Registry: Pydantic model as the single source of schema truth
# Concept: pydantic-model — one declaration drives both the API schema and
#          application-side validation
# ---------------------------------------------------------------------------
class ReviewSummary(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    score: int = Field(ge=1, le=5, description="Rating 1 (worst) to 5 (best)")
    key_issues: list[str] = Field(
        default_factory=list,
        description="List of problems mentioned. Empty if none.",
    )


SYSTEM_PROMPT = (
    "You are a review analyst. Extract a structured summary from the customer review."
)

# Five inputs: simple, adversarial (prose + JSON), missing data, long, special chars
TEST_REVIEWS = [
    "Great product, fast delivery! Exactly what I needed.",
    "The item was okay but shipping took forever and the packaging was completely damaged.",
    "Meh.",
    (
        "I've been using this for three months now. "
        "Initially I was impressed by the build quality, but over time I noticed "
        "the battery life degraded significantly. Customer support was unhelpful "
        "when I raised the issue. The product does what it advertises, but barely."
    ),
    "¡Excelente! 5/5 ★★★★★ — no issues at all.",
]


# ---------------------------------------------------------------------------
# Observation 1: Prompt-only JSON
# Concept: structured-output — format instruction without API enforcement
# ---------------------------------------------------------------------------
def run_prompt_only(client) -> int:
    print("\n=== Observation 1: Prompt-only JSON ===")
    successes = 0
    for i, review in enumerate(TEST_REVIEWS, 1):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Review: {review}\n\n"
                    'Respond ONLY with a JSON object with keys "sentiment" '
                    '("positive"|"neutral"|"negative"), "score" (1-5 int), '
                    '"key_issues" (list of strings).'
                ),
            },
        ]
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=0.1,
        )
        raw = response.choices[0].message.content or ""
        # Attempt to extract JSON from the raw response
        try:
            # Strip potential prose before/after the JSON block
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("no JSON object found")
            data = json.loads(raw[start:end])
            # Verify required keys present
            if not all(k in data for k in ("sentiment", "score", "key_issues")):
                raise ValueError("missing required keys")
            successes += 1
            print(f"  Input {i}: OK — sentiment={data['sentiment']}, score={data['score']}")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"  Input {i}: FAIL — {e}")
            print(f"    raw snippet: {raw[:120]!r}")
    print(f"Prompt-only parse success: {successes}/{len(TEST_REVIEWS)}")
    return successes


# ---------------------------------------------------------------------------
# Observation 2: JSON mode
# Concept: json-mode — syntactic validity guaranteed, shape unconstrained
# ---------------------------------------------------------------------------
def run_json_mode(client) -> int:
    print("\n=== Observation 2: JSON mode ===")
    successes = 0
    schema_compliant = 0
    for i, review in enumerate(TEST_REVIEWS, 1):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Review: {review}\n\n"
                    'Respond with a JSON object with keys "sentiment", "score", "key_issues".'
                ),
            },
        ]
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=0.1,
            # Concept: json-mode — API enforces valid JSON syntax
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or ""
        try:
            data = json.loads(raw)
            successes += 1
            # Check if it actually conforms to our expected schema
            conforms = all(k in data for k in ("sentiment", "score", "key_issues"))
            if conforms:
                schema_compliant += 1
            print(f"  Input {i}: valid JSON={True}, schema-compliant={conforms}")
        except json.JSONDecodeError as e:
            print(f"  Input {i}: FAIL — {e}")

    print(f"JSON mode parse success: {successes}/{len(TEST_REVIEWS)}")
    print(f"Schema compliant (manual check): {schema_compliant}/{len(TEST_REVIEWS)}")
    return successes


# ---------------------------------------------------------------------------
# Observation 3: Schema enforcement via Pydantic
# Concept: response-format + pydantic-model — typed object returned by SDK
# ---------------------------------------------------------------------------
def run_schema_enforcement(client) -> int:
    print("\n=== Observation 3: Schema enforcement (Pydantic) ===")
    successes = 0
    for i, review in enumerate(TEST_REVIEWS, 1):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Review: {review}"},
        ]
        response = client.beta.chat.completions.parse(
            model=OLLAMA_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=0.1,
            # Concept: response-format — schema attached to request, enforcement at API level
            response_format=ReviewSummary,
        )
        # Concept: pydantic-model — message.parsed is the typed ReviewSummary instance
        result: ReviewSummary | None = response.choices[0].message.parsed
        if result is None:
            print(f"  Input {i}: FAIL — model did not conform to schema")
        else:
            successes += 1
            print(
                f"  Input {i}: ReviewSummary("
                f"sentiment={result.sentiment!r}, "
                f"score={result.score}, "
                f"key_issues={result.key_issues})"
            )

    print(f"Schema enforcement parse success: {successes}/{len(TEST_REVIEWS)}")
    if successes == len(TEST_REVIEWS):
        print("All typed objects. No manual json.loads needed.")
    return successes


if __name__ == "__main__":
    assert_ollama_ready()
    client = build_client()

    obs1 = run_prompt_only(client)
    obs2 = run_json_mode(client)
    obs3 = run_schema_enforcement(client)

    print("\n=== Summary ===")
    print(f"  Prompt-only:        {obs1}/{len(TEST_REVIEWS)} parsed")
    print(f"  JSON mode:          {obs2}/{len(TEST_REVIEWS)} valid JSON")
    print(f"  Schema enforcement: {obs3}/{len(TEST_REVIEWS)} typed objects")
    print("\nExpected: reliability increases from observation 1 → 3.")
