---
id: "prompt-engineering-architecture"
title: "Prompt Engineering — Architecture"
type: "architecture"
step: "prompt-engineering"
path: "docs/prompt-engineering/architecture.md"
status: "draft"
level: "foundational"

concepts:
  - "prompt-anatomy"
  - "prompt-pattern"
  - "chain-of-thought"
  - "few-shot-prompting"
  - "output-format-specification"

prerequisites:
  - "docs/prompt-engineering/README.md"
  - "docs/prompt-engineering/prompt-anatomy.md"
  - "docs/prompt-engineering/few-shot.md"
  - "docs/prompt-engineering/chain-of-thought.md"
  - "docs/prompt-engineering/prompt-patterns.md"
  - "docs/prompt-engineering/prompt-pitfalls.md"

next:
  - "docs/prompt-engineering/implementation-reference.md"

related:
  - "docs/llm-apis/architecture.md"
  - "docs/structured-outputs/README.md"

implementation_refs:
  - "labs/prompt-engineering/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes the system-level architecture of a prompt engineering layer — the components that construct, execute, parse, and test prompts — and how they integrate with the API client layer from llm-apis."
---

# Prompt Engineering — Architecture

## Navigation

[Docs](../README.md) / [Prompt Engineering](README.md) / Prompt Engineering — Architecture

---

## 1. System Overview

The prompt engineering layer sits between application logic and the LLM API client established in `llm-apis`. Its job is to translate a task requirement into a well-formed API request and translate the model's response back into structured application data. The layer has four components: prompt builder, API client (from `llm-apis`), response parser, and prompt test harness.

This is not a framework or library — it is a set of application-owned functions and data structures that form a consistent interface between intent (what the application needs) and execution (what the API receives and returns).

---

## 2. Core Components

| Component | Role | Responsibility |
|-----------|------|----------------|
| Prompt builder | Construction | Assembles system prompt, examples, context, and format spec into a message list |
| API client | Transport | Sends the assembled prompt to the provider and returns the raw response (from `llm-apis`) |
| Response parser | Extraction | Extracts the application-relevant data from the model's text response |
| Prompt test harness | Validation | Runs a prompt template against a benchmark input set and reports accuracy |

---

## 3. Component Interactions

Application logic provides the task parameters (input data, desired output type) to the prompt builder. The builder applies the relevant pattern template and produces a `messages` list. The API client sends the request and returns a `ChatResponse`. The parser extracts the structured result. The test harness operates offline, running the builder and parser against known inputs to validate prompt correctness before deployment.

```
Application logic
    │
    ▼
Prompt builder ──► pattern template + task parameters → messages list
    │
    ▼
API client (llm-apis) ──► ChatResponse
    │
    ▼
Response parser ──► structured result (str, dict, dataclass)
    │
    ▼
Application logic
```

---

## 4. Data Flow

**Standard call path:**

```text
Task parameters (input_text, task_type)
  │
  ▼
Prompt builder: select pattern → inject parameters → produce messages[]
  │
  ▼
API client: POST /v1/chat/completions → ChatResponse(text, tokens, stop_reason)
  │
  ▼
Response parser: extract structured data from ChatResponse.text
  │
  ▼
Application: receives typed result
```

**Chain-of-thought call path:**

```text
Task parameters
  │
  ▼
Prompt builder: adds "Let's think step by step. Answer: " to prompt
  │
  ▼
API client: returns reasoning trace + "Answer: <value>"
  │
  ▼
Response parser: splits on "Answer:", returns text after marker
  │
  ▼
Application: receives final answer only (reasoning trace discarded or logged)
```

**Test harness path:**

```text
Benchmark inputs (input, expected_output)[]
  │
  ▼
For each input: prompt builder → API client → response parser
  │
  ▼
Compare parsed output to expected_output
  │
  ▼
Accuracy report: correct/total, failures with actual vs expected
```

---

## 5. Execution Flow

1. Application calls `prompt_builder.build(pattern, task_params)`
2. Builder selects the pattern template, injects parameters, assembles `messages`
3. Application calls `api_client.complete(messages)` → `ChatResponse`
4. Application calls `parser.parse(response.text, expected_type)`
5. Parser returns typed result or raises `ParseError`
6. On `ParseError`: application retries with a clarifying follow-up message or falls back to a default

Decision point at step 5: if parsing fails, the application has two options — retry the full call with an adjusted prompt, or call the API with the failed response as context asking "Please reformat your answer as: ___". The second approach uses one additional call but avoids regenerating a long response.

---

## 6. Integration Points

| System | Integration point | Direction |
|--------|-------------------|-----------|
| API client layer (`llm-apis`) | `ChatResponse` input to parser | Upstream |
| Application logic | Task parameters in, typed result out | Bidirectional |
| `structured-outputs` module | Schema-enforced parsing replaces string parser | Downstream extension |
| `rag` module | Retrieved context injected into prompt builder | Upstream data |
| `prompt-versioning` (`observability-mlops`) | Pattern templates stored with version metadata | Governance |

---

## 7. Trade-offs and Design Decisions

**Prompt builder as a function vs. a class**: A function that takes pattern and parameters is simpler and easier to test. A class that holds pattern state is useful when the same pattern is used many times with different parameters in the same session. The labs use functions; production systems with many patterns may benefit from a class that encapsulates pattern validation.

**Parser strictness**: A strict parser raises an exception on any deviation from the expected format. A lenient parser applies heuristics to recover partial results. Strict parsing fails loudly and is easier to debug; lenient parsing silently accepts malformed output and may pass incorrect data to the application. The labs use strict parsing with an explicit fallback call — not lenient parsing.

**Test harness as offline validation**: Running the test harness in CI before deploying a prompt change catches regressions before they reach production. The cost is maintaining a benchmark input set. The alternative — testing prompts only in production — converts silent failures into user-visible bugs.

---

## 8. Mapping to Labs

| Component | Lab |
|-----------|-----|
| Prompt builder — anatomy components | `lab-prompt-anatomy` |
| Prompt builder — few-shot pattern | `lab-few-shot` |
| Prompt builder — CoT pattern + response parser | `lab-chain-of-thought` |
| Prompt builder — all three patterns + test harness | `lab-prompt-patterns` |

---

## 9. Limitations and Boundaries

This architecture covers single-model, single-call prompt patterns with optional chain-of-thought. It does not address:

- Multi-turn conversation prompt management (see `memory-context`)
- Tool use and function calling (see `structured-outputs`)
- Retrieval context injection (see `rag`)
- Prompt optimization and automatic improvement (see `performance-optimization`)
- Adversarial input defense beyond prompt-level measures (see `safety-guardrails`)

---

## 10. Summary

The prompt engineering layer has four components: prompt builder (constructs messages from templates), API client (from `llm-apis`, handles transport), response parser (extracts structured data from text), and test harness (offline accuracy validation). Data flows from task parameters through builder, client, and parser to a typed application result. Chain-of-thought adds a reasoning trace that the parser splits from the final answer. The critical design decision is parser strictness: fail loudly on malformed output rather than silently accepting partial results.
