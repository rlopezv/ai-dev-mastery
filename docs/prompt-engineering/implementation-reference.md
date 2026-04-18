---
id: "prompt-engineering-implementation-reference"
title: "Prompt Engineering — Implementation Reference"
type: "implementation-reference"
step: "prompt-engineering"
path: "docs/prompt-engineering/implementation-reference.md"
status: "draft"
level: "foundational"

concepts:
  - "prompt-pattern"
  - "output-format-specification"
  - "chain-of-thought"
  - "few-shot-prompting"
  - "instruction"

prerequisites:
  - "docs/prompt-engineering/architecture.md"

next:
  - "docs/prompt-engineering/validation.md"

related:
  - "docs/prompt-engineering/prompt-anatomy.md"
  - "docs/prompt-engineering/prompt-pitfalls.md"
  - "docs/llm-apis/implementation-reference.md"

implementation_refs:
  - "labs/prompt-engineering/lab-prompt-anatomy"
  - "labs/prompt-engineering/lab-few-shot"
  - "labs/prompt-engineering/lab-chain-of-thought"
  - "labs/prompt-engineering/lab-prompt-patterns"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how the prompt engineering architecture components map to concrete Python patterns — template functions, response parsers, chain-of-thought extraction, and a test harness — and the design decisions behind each."
---

# Prompt Engineering — Implementation Reference

## Navigation

[Docs](../README.md) / [Prompt Engineering](README.md) / Prompt Engineering — Implementation Reference

---

## 1. Implementation Overview

The architecture defines four components: prompt builder, API client, response parser, and test harness. In code, the prompt builder is a set of template functions (one per pattern), the API client is the `ChatResponse` abstraction from `llm-apis`, the response parser is a set of typed extraction functions, and the test harness is a loop over a benchmark input set.

> **Note:** This document contains orientative code — structures, interfaces, signatures.
> It is not directly executable. For complete, runnable implementations see the labs
> referenced in `implementation_refs`.

---

## 2. Core Patterns

| Pattern | Description | When to use |
|---------|-------------|-------------|
| Template function | Takes task parameters, returns `messages` list | Every prompt — separates structure from content |
| Few-shot builder | Injects example pairs into prompt before target | Tasks with non-standard output; classification |
| CoT builder | Appends step-by-step trigger and answer marker | Multi-step reasoning tasks |
| Format spec wrapper | Appends JSON schema and compliance instruction | Any task where response will be parsed |
| Strict parser | Extracts typed result; raises on format violation | Production paths where bad data is worse than no data |
| Benchmark harness | Runs template + parser against known inputs | Regression testing before prompt deployment |

---

## 3. Component Mapping

| Architecture Component | Implementation |
|------------------------|----------------|
| Prompt builder — role pattern | `build_role_prompt(role, domain, tone, constraint, task) → messages` |
| Prompt builder — format pattern | `build_format_prompt(schema, input_text) → messages` |
| Prompt builder — CoT pattern | `build_cot_prompt(question) → messages` |
| Prompt builder — few-shot pattern | `build_few_shot_prompt(examples, target) → messages` |
| Response parser — plain text | `parse_text(response_text) → str` |
| Response parser — JSON | `parse_json(response_text) → dict` |
| Response parser — CoT answer | `parse_cot_answer(response_text, marker="Answer:") → str` |
| Test harness | `run_benchmark(build_fn, parse_fn, cases) → BenchmarkResult` |

---

## 4. Data Structures and Interfaces

**Messages list** — same structure as `llm-apis`:

```python
# Orientative — see labs/prompt-engineering/lab-prompt-anatomy/main.py
Messages = list[dict]  # [{"role": "system"|"user"|"assistant", "content": str}]
```

**Template function signature**:

```python
# Orientative — see labs/prompt-engineering/lab-prompt-patterns/main.py
def build_role_prompt(
    role: str,
    domain: str,
    tone: str,
    constraint: str,
    task: str,
) -> Messages:
    system = (
        f"You are a {role} with expertise in {domain}. "
        f"Your responses are {tone}. You do not {constraint}."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": task},
    ]
```

**CoT builder with answer marker**:

```python
# Orientative — see labs/prompt-engineering/lab-chain-of-thought/main.py
def build_cot_prompt(question: str) -> Messages:
    user = (
        f"{question}\n\n"
        "Let's think step by step. "
        "At the end, state your final answer on a new line starting with 'Answer:'."
    )
    return [{"role": "user", "content": user}]


def parse_cot_answer(response_text: str, marker: str = "Answer:") -> str:
    """Extract the final answer after the CoT marker. Raises ValueError if not found."""
    if marker not in response_text:
        raise ValueError(f"CoT marker '{marker}' not found in response.")
    return response_text.split(marker, 1)[1].strip()
```

**Benchmark harness**:

```python
# Orientative — see labs/prompt-engineering/lab-prompt-patterns/main.py
from dataclasses import dataclass

@dataclass
class BenchmarkCase:
    input_params: dict
    expected_output: str

@dataclass
class BenchmarkResult:
    total: int
    correct: int
    failures: list[dict]  # {"input": ..., "expected": ..., "actual": ...}

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total > 0 else 0.0


def run_benchmark(
    build_fn,
    parse_fn,
    api_client,
    cases: list[BenchmarkCase],
) -> BenchmarkResult:
    """Run build → call → parse for each case and compare to expected output."""
    failures = []
    correct = 0
    for case in cases:
        messages = build_fn(**case.input_params)
        response = api_client.complete(messages)
        try:
            actual = parse_fn(response.text)
        except (ValueError, KeyError):
            actual = None
        if actual == case.expected_output:
            correct += 1
        else:
            failures.append({
                "input": case.input_params,
                "expected": case.expected_output,
                "actual": actual,
            })
    return BenchmarkResult(total=len(cases), correct=correct, failures=failures)
```

---

## 5. Design Decisions

**Template functions over string concatenation**: Embedding prompt components via `f"{role} with expertise in {domain}"` inside a function ensures every instantiation follows the same structure. Ad-hoc string concatenation at call sites accumulates inconsistencies that are invisible until a prompt fails on an edge case.

**Strict parser with explicit fallback**: The parser raises `ValueError` on format violations rather than returning `None` or a partial result. The call site catches `ValueError` and either retries with a reformatting instruction or logs the failure and returns a default. This makes failures explicit and traceable — malformed responses do not silently become empty strings in downstream logic.

**Answer marker in CoT prompts**: The marker `"Answer:"` is placed in the prompt as part of the instruction: "State your final answer on a new line starting with 'Answer:'." The parser splits on this literal string. This is more robust than regex patterns or positional extraction (last sentence, last line) because it is deterministic regardless of how long the reasoning trace is.

**Benchmark harness at the function level**: The harness takes `build_fn` and `parse_fn` as parameters rather than operating on prompt strings directly. This makes it possible to test different pattern implementations against the same benchmark without changing the harness. The API client is also a parameter — tests can be run against Ollama locally or against a cloud provider without modifying the harness.

---

## 6. External Dependencies

| Tool | Role | Infrastructure profile |
|------|------|------------------------|
| `openai` Python SDK | API transport (via Ollama or OpenAI) | `light` |
| Ollama | Local LLM runtime for offline testing | `light` |
| `json` (stdlib) | JSON parsing for format-spec patterns | none |

---

## 7. Mapping to Labs

| Pattern / Component | Lab | Concept verified |
|---------------------|-----|-----------------|
| Anatomy template functions | `lab-prompt-anatomy` | Component removal effect on output consistency |
| Few-shot builder | `lab-few-shot` | Accuracy improvement from 0-shot to 3-shot |
| CoT builder + `parse_cot_answer` | `lab-chain-of-thought` | Accuracy on multi-step reasoning, answer extraction |
| All patterns + `run_benchmark` | `lab-prompt-patterns` | Pattern composition, format compliance, regression testing |

---

## 8. Trade-offs and Constraints

**Template functions vs. templating libraries**: Jinja2 or similar libraries offer more power (conditionals, loops, inheritance) for complex prompt templates. For the simple patterns in this module, Python f-strings in functions are sufficient and introduce no additional dependency. Complex multi-agent prompts (see `ai-agents`) may benefit from a templating library.

**Benchmark quality vs. benchmark size**: A 10-case benchmark runs in seconds; a 100-case benchmark may take minutes against a cloud API and cost real money. For development, 10–20 well-chosen edge cases are more valuable than 100 happy-path cases. Invest in case quality over quantity.

**Parser strictness vs. user experience**: A strict parser that raises on format violations produces clean application data but may return errors to users more often. A lenient parser recovers more partial results but may pass malformed data downstream. Choose based on whether a bad result is worse than no result for the specific application.

---

## 9. Failure Modes

**Template injection via task parameters**: If `task` in `build_role_prompt` contains a string like "Ignore previous instructions and...", the injected content becomes part of the system message. Validate or sanitize parameters before injection if they come from user input. See `prompt-pitfalls.md`.

**Marker collision in CoT responses**: If the model generates the string "Answer:" as part of its reasoning trace (before the final answer), `split("Answer:", 1)` returns the first occurrence, which is not the final answer. Use a more distinctive marker that is unlikely to appear in reasoning text: "FINAL ANSWER:" or `"<answer>"`.

**Benchmark drift**: A benchmark that passes today may fail after a model version update. The model's behavior changes; the prompt does not; the benchmark detects the regression. Run benchmarks on model updates, not only on prompt changes.

---

## 10. Summary

The implementation maps four architecture components to Python patterns: template functions (prompt builder), `ChatResponse` (API client, from `llm-apis`), strict typed parsers (response parser), and a parameterized harness loop (test harness). Key design choices: template functions enforce consistent structure; the CoT answer marker is embedded in the prompt itself; the parser raises on format violations and the call site handles the exception explicitly; the benchmark harness takes builder and parser as parameters to enable cross-pattern comparison. All patterns are tested in `lab-prompt-patterns` against a fixed benchmark that verifies both format compliance and content correctness.
