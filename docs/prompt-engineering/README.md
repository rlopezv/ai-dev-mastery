---
id: "prompt-engineering-readme"
title: "Prompt Engineering"
type: "step-readme"
step: "prompt-engineering"
path: "docs/prompt-engineering/README.md"
status: "draft"
level: "foundational"

concepts:
  - "prompt-anatomy"
  - "few-shot-prompting"
  - "chain-of-thought"
  - "prompt-patterns"
  - "prompt-pitfalls"

prerequisites:
  - "docs/llm-apis/README.md"
  - "docs/llm-fundamentals/context-window.md"

next:
  - "docs/prompt-engineering/prompt-anatomy.md"

related:
  - "docs/structured-outputs/README.md"
  - "docs/llm-apis/api-patterns.md"

implementation_refs:
  - "labs/prompt-engineering/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Covers how to structure and write prompts that produce reliable, predictable output — from the anatomy of a prompt to few-shot examples, chain-of-thought reasoning, reusable patterns, and common failure modes."
---

## 1. Overview

A prompt is the primary control surface for an LLM. Unlike a function call with a fixed signature, a prompt is a piece of text that implicitly encodes task description, context, constraints, output format, and examples — all at once. Getting reliable output requires understanding what each part of a prompt communicates to the model and how the model interprets it.

This step covers prompt engineering from first principles: what a prompt is made of, how few-shot examples shift model behavior without retraining, how chain-of-thought unlocks multi-step reasoning, what reusable prompt patterns exist, and where prompts reliably break down. Every technique here operates through the API calls established in `llm-apis` — nothing requires a new model or infrastructure.

---

## 2. Scope

**Covered:**
- Prompt anatomy: the structural components and what each communicates to the model
- Few-shot prompting: using examples in the prompt to define task behavior
- Chain-of-thought: eliciting intermediate reasoning steps before the final answer
- Prompt patterns: reusable structural templates for common task types
- Prompt pitfalls: failure modes from over-specification, under-specification, and adversarial input

**Not covered:**
- Structured output formats and schema enforcement (see `structured-outputs`)
- Retrieval-augmented generation — injecting external documents into prompts (see `rag`)
- Prompt versioning and management at production scale (see `observability-mlops`)
- Fine-tuning as an alternative to prompting (see `llm-fundamentals/fine-tuning.md`)

---

## 3. Key Concepts

**Prompt anatomy**
The internal structure of a prompt: the components that constitute a complete input to a model — system instructions, user message, context, examples, and output format specification — and what each one signals to the model.

**Few-shot prompting**
A technique that provides labeled input/output examples inside the prompt to define expected task behavior. The model infers the pattern from examples rather than from explicit instructions.

**Chain-of-thought**
A prompting technique that asks the model to produce intermediate reasoning steps before the final answer. Externalizing the reasoning process improves accuracy on multi-step tasks where direct answers are unreliable.

**Prompt patterns**
Recurring structural templates — role assignment, output format specification, step-by-step instruction — that encode task requirements in a reusable, testable form.

**Prompt pitfalls**
Systematic failure modes in prompt design: ambiguous instructions, over-constrained output formats, conflicting requirements, and prompt injection — the exploitation of prompt structure by adversarial user input.

---

## 4. Concept Map

```
prompt-anatomy ──────────────────────────────────────┐
    │                                                  ▼
    ├── system-prompt                        prompt-patterns
    ├── instruction                              │
    ├── context                                  ├── role-prompting
    ├── examples ──────────► few-shot-prompting  ├── output-format
    └── output-format                            └── step-by-step
                │
                ▼
        chain-of-thought ──► intermediate reasoning steps
                │
                ▼
        prompt-pitfalls ──► injection / over-specification / ambiguity
```

- **Prompt anatomy** defines the vocabulary for all other topics in this step.
- **Few-shot prompting** and **chain-of-thought** are complementary: few-shot defines what to produce, chain-of-thought defines how to reason before producing it.
- **Prompt patterns** are structured applications of anatomy components.
- **Prompt pitfalls** are consequences of misapplying any of the above.

---

## 5. Learning Flow

| Order | Topic | Dependency |
|-------|-------|------------|
| 1 | `prompt-anatomy.md` | llm-apis |
| 2 | `few-shot.md` | prompt-anatomy |
| 3 | `chain-of-thought.md` | prompt-anatomy |
| 4 | `prompt-patterns.md` | few-shot, chain-of-thought |
| 5 | `prompt-pitfalls.md` | prompt-patterns |
| 6 | `architecture.md` | all topics |
| 7 | `implementation-reference.md` | architecture |
| 8 | `validation.md` | all above |

Read topics in this order. `prompt-pitfalls.md` has no lab — read it before running the other labs to understand what can go wrong.

---

## 6. Documentation Structure

```text
docs/prompt-engineering/
├── README.md                    ← this file
├── prompt-anatomy.md            ← structural components of a prompt
├── few-shot.md                  ← in-context learning via examples
├── chain-of-thought.md          ← intermediate reasoning steps
├── prompt-patterns.md           ← reusable structural templates
├── prompt-pitfalls.md           ← failure modes (concept-only)
├── architecture.md              ← system-level view
├── implementation-reference.md  ← bridge to lab execution
└── validation.md                ← completion criteria
```

---

## 7. Labs Overview

| Lab | Type | Purpose |
|-----|------|---------|
| `lab-prompt-anatomy` | observation | Isolate each prompt component and observe its effect on model output |
| `lab-few-shot` | implementation | Build a task classifier using labeled examples in the prompt |
| `lab-chain-of-thought` | implementation | Compare direct answers vs chain-of-thought on multi-step reasoning tasks |
| `lab-prompt-patterns` | implementation | Implement and test three reusable prompt pattern templates |

All labs use the `light` infrastructure profile. Labs run against Ollama by default; any OpenAI-compatible endpoint works without code changes.

---

## 8. How to Use This Step

**Recommended path:**
1. Read this README.
2. Read `prompt-anatomy.md` and run `lab-prompt-anatomy`.
3. Read `few-shot.md` and run `lab-few-shot`.
4. Read `chain-of-thought.md` and run `lab-chain-of-thought`.
5. Read `prompt-patterns.md` and run `lab-prompt-patterns`.
6. Read `prompt-pitfalls.md` — no lab, read before the next step.
7. Read `architecture.md` and `implementation-reference.md`.
8. Complete `validation.md`.

**Optional:** if you already have experience with few-shot prompting, begin at `chain-of-thought.md`. Do not skip `prompt-anatomy.md` entirely — the vocabulary it defines is used in every subsequent topic.

---

## 9. Relationship to Other Steps

| Position | Step | Relationship |
|----------|------|--------------|
| Before | `llm-apis` | API call mechanics and message structure are assumed throughout |
| After | `structured-outputs` | Structured output prompts extend the patterns and format specification techniques established here |
| Later dependency | `rag` | RAG prompts inject retrieved context into the anatomy structure defined here |
| Later dependency | `ai-agents` | Agent system prompts are complex applications of role prompting and step-by-step patterns |

---

## 10. Next Steps

Begin with the first topic:

→ [`docs/prompt-engineering/prompt-anatomy.md`](./prompt-anatomy.md)
