# Lab: lab-schema-design
# Module: structured-outputs
# Doc reference: docs/structured-outputs/schema-design.md

import logging
import sys
from dataclasses import dataclass, field
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

# ---------------------------------------------------------------------------
# Unconstrained schema: all strings, all required, no enum constraints
# Concept: json-schema — absence of constraints is the baseline failure mode
# ---------------------------------------------------------------------------
class ContactUnconstrained(BaseModel):
    name: str
    email: str
    phone: str
    company: str
    role: str  # free string — no enum constraint


# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In ContactConstrained, change role from Literal["engineer", "manager", "executive", "unknown"]
#   to str | None = None
# - Observe:
#   * enum_violations stays 0 — there is no enum to violate
#   * non-standard values ("director", "CEO", "developer") pass through unchecked
#   * constrained schema no longer enforces vocabulary bounds on role
#   * enum_violations metric becomes meaningless as a comparison signal between schemas

# ---------------------------------------------------------------------------
# Constrained schema: enums, nullable optionals, bounded fields
# Concept: schema-constraints + pydantic-model — single source for constraints
# ---------------------------------------------------------------------------
class ContactConstrained(BaseModel):
    name: str = Field(max_length=100)
    # Concept: field-selection — optional fields return None when absent
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    # Concept: schema-constraints — Literal maps to JSON Schema enum
    role: Literal["engineer", "manager", "executive", "unknown"] = "unknown"


# ---------------------------------------------------------------------------
# Test set: covers normal inputs and adversarial edge cases
# ---------------------------------------------------------------------------
TEST_INPUTS = [
    "Email John Smith at john@acme.com about the project.",
    "Call the office at 555-1234 for support.",
    "Contact Sarah Johnson, CTO at TechCorp, at sarah@tech.com or +1-555-9876.",
    "Reach out to the team.",  # adversarial: no specific contact info
    "Hi, I'm Alex.",  # adversarial: name only, no other details
    "Send a message to manager@example.com.",  # email only, no name
    "Ing. Carlos López, Director de Ingeniería. carlos@empresa.es",  # non-English
    "Please contact our CEO.",  # role hint, no specific person
    "Jane Doe — jdoe@corp.com — Software Engineer",  # different separator style
    "bob",  # minimal: single word, no structure
]

SYSTEM_PROMPT = "Extract contact information from the text."


@dataclass
class SchemaResult:
    parse_successes: int = 0
    enum_violations: int = 0
    hallucinated_optionals: int = 0
    failures: list[str] = field(default_factory=list)


VALID_ROLES = {"engineer", "manager", "executive", "unknown"}


def is_hallucinated_optional(value, input_text: str, keywords: list[str]) -> bool:
    """Detect a non-None value on a field whose keywords are absent from input."""
    if value is None or value == "":
        return False
    return not any(kw.lower() in input_text.lower() for kw in keywords)


# ---------------------------------------------------------------------------
# Run unconstrained schema
# ---------------------------------------------------------------------------
def run_unconstrained(client) -> SchemaResult:
    print("\n--- Unconstrained schema ---")
    result = SchemaResult()

    for i, text in enumerate(TEST_INPUTS, 1):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]
        try:
            response = client.beta.chat.completions.parse(
                model=OLLAMA_MODEL,
                messages=messages,
                response_format=ContactUnconstrained,
                max_tokens=MAX_TOKENS,
                temperature=0.1,
            )
            parsed = response.choices[0].message.parsed
            if parsed is None:
                result.failures.append(f"Input {i}: model did not conform")
                print(f"  Input {i}: FAIL — model did not conform")
                continue

            result.parse_successes += 1

            # Check enum violation: role should be one of the valid values
            if parsed.role.lower() not in VALID_ROLES:
                result.enum_violations += 1
                violation_note = f" ← enum violation: {parsed.role!r}"
            else:
                violation_note = ""

            # Detect hallucinated email/phone (model guessed when not in input)
            hallucinated = []
            if is_hallucinated_optional(parsed.email, text, ["@", ".com", ".org", ".net"]):
                hallucinated.append(f"email={parsed.email!r}")
                result.hallucinated_optionals += 1
            if is_hallucinated_optional(parsed.phone, text, ["555", "+", "tel", "phone", "call"]):
                hallucinated.append(f"phone={parsed.phone!r}")
                result.hallucinated_optionals += 1

            hallucinated_note = f" ← hallucinated: {hallucinated}" if hallucinated else ""
            print(
                f"  Input {i}: name={parsed.name!r}, email={parsed.email!r}, "
                f"role={parsed.role!r}{violation_note}{hallucinated_note}"
            )

        except Exception as e:
            result.failures.append(f"Input {i}: {e}")
            print(f"  Input {i}: EXCEPTION — {e}")

    print(
        f"Unconstrained — parse success: {result.parse_successes}/{len(TEST_INPUTS)} | "
        f"enum violations: {result.enum_violations} | "
        f"hallucinated optionals: {result.hallucinated_optionals}"
    )
    return result


# ---------------------------------------------------------------------------
# Run constrained schema
# Concept: schema-constraints — enum + nullable fields produce better reliability
# ---------------------------------------------------------------------------
def run_constrained(client) -> SchemaResult:
    print("\n--- Constrained schema ---")
    result = SchemaResult()

    for i, text in enumerate(TEST_INPUTS, 1):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]
        try:
            response = client.beta.chat.completions.parse(
                model=OLLAMA_MODEL,
                messages=messages,
                # Concept: response-format — Pydantic model declares constraints
                response_format=ContactConstrained,
                max_tokens=MAX_TOKENS,
                temperature=0.1,
            )
            parsed = response.choices[0].message.parsed
            if parsed is None:
                result.failures.append(f"Input {i}: model did not conform")
                print(f"  Input {i}: FAIL — model did not conform")
                continue

            result.parse_successes += 1

            # Literal constraint: role must be in the enum
            if parsed.role not in VALID_ROLES:
                result.enum_violations += 1
                violation_note = f" ← enum violation: {parsed.role!r}"
            else:
                violation_note = ""

            # Nullable fields should return None when info is absent
            hallucinated = []
            if is_hallucinated_optional(parsed.email, text, ["@", ".com", ".org", ".net"]):
                hallucinated.append(f"email={parsed.email!r}")
                result.hallucinated_optionals += 1
            if is_hallucinated_optional(parsed.phone, text, ["555", "+", "tel", "phone", "call"]):
                hallucinated.append(f"phone={parsed.phone!r}")
                result.hallucinated_optionals += 1

            hallucinated_note = f" ← hallucinated: {hallucinated}" if hallucinated else ""
            print(
                f"  Input {i}: name={parsed.name!r}, email={parsed.email!r}, "
                f"role={parsed.role!r}{violation_note}{hallucinated_note}"
            )

        except Exception as e:
            result.failures.append(f"Input {i}: {e}")
            print(f"  Input {i}: EXCEPTION — {e}")

    print(
        f"Constrained — parse success: {result.parse_successes}/{len(TEST_INPUTS)} | "
        f"enum violations: {result.enum_violations} | "
        f"hallucinated optionals: {result.hallucinated_optionals}"
    )
    return result


if __name__ == "__main__":
    assert_ollama_ready()
    client = build_client()

    print("=== Schema comparison: ContactExtraction ===")
    unconstrained = run_unconstrained(client)
    constrained = run_constrained(client)

    print("\n=== Summary ===")
    print(
        f"  Unconstrained: {unconstrained.parse_successes}/{len(TEST_INPUTS)} parses | "
        f"{unconstrained.enum_violations} enum violations | "
        f"{unconstrained.hallucinated_optionals} hallucinated optionals"
    )
    print(
        f"  Constrained:   {constrained.parse_successes}/{len(TEST_INPUTS)} parses | "
        f"{constrained.enum_violations} enum violations | "
        f"{constrained.hallucinated_optionals} hallucinated optionals"
    )

    improvements = []
    if constrained.enum_violations < unconstrained.enum_violations:
        improvements.append(
            f"enum violations reduced "
            f"{unconstrained.enum_violations} → {constrained.enum_violations}"
        )
    if constrained.hallucinated_optionals < unconstrained.hallucinated_optionals:
        improvements.append(
            f"hallucinated optionals reduced "
            f"{unconstrained.hallucinated_optionals} → {constrained.hallucinated_optionals}"
        )
    if improvements:
        print(f"\n  Improvements: {'; '.join(improvements)}")
    else:
        print("\n  No measurable improvement — model may handle both schemas equally well.")
        print("  Try a larger model (OLLAMA_MODEL=llama3.2:7b) or more adversarial inputs.")
