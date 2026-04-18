---
id: "prompt-engineering-validation"
title: "Prompt Engineering — Validation"
type: "validation"
step: "prompt-engineering"
path: "docs/prompt-engineering/validation.md"
status: "draft"
level: "foundational"

concepts:
  - "prompt-anatomy"
  - "few-shot-prompting"
  - "chain-of-thought"
  - "prompt-pattern"
  - "prompt-injection"
  - "output-format-specification"

prerequisites:
  - "docs/prompt-engineering/implementation-reference.md"

next:
  - "docs/structured-outputs/README.md"

related:
  - "docs/prompt-engineering/README.md"
  - "docs/prompt-engineering/prompt-pitfalls.md"

implementation_refs:
  - "labs/prompt-engineering/lab-prompt-anatomy"
  - "labs/prompt-engineering/lab-few-shot"
  - "labs/prompt-engineering/lab-chain-of-thought"
  - "labs/prompt-engineering/lab-prompt-patterns"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"
  - "meta/standards/validation/labs-checklist.md"

summary: "Defines the conceptual, practical, and lab-level criteria that confirm a learner can write reliable prompts using anatomy components, few-shot examples, chain-of-thought, and reusable patterns."
---

# Prompt Engineering — Validation

## Navigation

[Docs](../README.md) / [Prompt Engineering](README.md) / Prompt Engineering — Validation

---

## 1. Validation Overview

This step is complete when the learner can diagnose a failing prompt by identifying which component is missing or malformed, apply few-shot and chain-of-thought techniques correctly, and implement reusable prompt patterns with measurable accuracy. Validation is practical: it is demonstrated through lab execution and the ability to fix a broken prompt given only its symptoms.

---

## 2. Conceptual Validation

| Concept | Validation Method |
|---------|------------------|
| Prompt anatomy | Name the five components and explain what each communicates to the model |
| System prompt scope | Explain why the system prompt is re-sent on every API call and what this costs |
| Zero-shot vs few-shot | Explain when few-shot is more reliable than zero-shot and why |
| In-context learning | Explain how the model infers task behavior from examples without weight updates |
| Chain-of-thought mechanism | Explain why externalizing reasoning steps improves multi-step accuracy |
| CoT answer extraction | Describe two approaches to extracting the final answer from a CoT response |
| Prompt patterns | Describe role prompting, output format specification, and step-by-step instruction and when each applies |
| Under-specification | Give an example of an underspecified prompt and the fix |
| Instruction conflict | Explain how to detect and resolve a conflict between system prompt and user message |
| Prompt injection | Explain why prompt-level defenses are insufficient as the sole protection |

---

## 3. Practical Validation

```text
Task 1: Diagnose a broken prompt
Given: a prompt that produces inconsistent sentiment classification output
Expected: identify which anatomy component is missing (output format spec),
          add it, and confirm output becomes consistent across 5 runs

Task 2: Implement a 3-shot classifier
Given: a classification task with four output classes
Expected: write a few-shot prompt with 3 examples (one per class minimum),
          test against 10 inputs, achieve ≥80% accuracy

Task 3: Apply chain-of-thought to a multi-step problem
Given: a 3-step arithmetic word problem
Expected: zero-shot answer is wrong; CoT answer is correct;
          final answer is extracted cleanly using a marker

Task 4: Implement a role + format + steps composite pattern
Given: a code review task
Expected: role is specific and constraining; output is parseable JSON;
          all step results are present in the response

Task 5: Identify the pitfall
Given: three prompts with known failures (one under-specified, one over-specified,
       one with an injection attempt in the input)
Expected: correctly identify the pitfall type in each case and state the fix
```

---

## 4. Lab Validation

| Lab | Validation Criteria |
|-----|---------------------|
| `lab-prompt-anatomy` | Component removal produces measurably less consistent output; adding output format spec stabilizes response structure across 5 runs |
| `lab-few-shot` | 3-shot achieves higher accuracy than 0-shot on the test set; example format is consistent across all examples |
| `lab-chain-of-thought` | Direct answer is incorrect on at least one multi-step problem where CoT is correct; CoT answer is extracted cleanly using the "Answer:" marker |
| `lab-prompt-patterns` | All three patterns produce format-compliant responses on the test set; benchmark harness reports accuracy ≥80% |

---

## 5. Integration Validation

At this point in the roadmap, the learner should be able to reason across module boundaries:

- **From `llm-fundamentals`**: Prompt components consume tokens. A system prompt with 300 tokens re-sent on every turn of a 20-turn conversation costs 6,000 prompt tokens in total. Context window budget applies to prompt content.
- **From `llm-apis`**: Few-shot examples and chain-of-thought output are assembled into the `messages` list. The message accumulation pattern from `api-patterns.md` carries conversation history; the same list carries few-shot examples in a single-turn prompt.
- **To `structured-outputs`**: Output format specification via prompt instruction is the precursor to schema-enforced structured outputs. The format pattern here becomes a function call schema in the next module.
- **To `rag`**: The context component of a prompt is where RAG injects retrieved documents. The anatomy structure defined here is the container for that content.

A learner who cannot explain how `prompt_tokens` in a few-shot prompt relates to example count has not integrated the concepts across modules.

---

## 6. Failure Detection

**Common misconceptions:**

- *"More constraints make prompts more reliable"*: Over-specification creates incompatible constraints. Each constraint should be necessary; if it can be removed without affecting output quality, remove it.
- *"Chain-of-thought always improves accuracy"*: CoT adds latency and cost. On simple tasks, it produces longer output with no accuracy gain. Reserve it for multi-step reasoning.
- *"Prompt injection can be prevented by telling the model to ignore it"*: The instruction to ignore injection is itself subject to injection. Application-layer defenses are required.
- *"Few-shot examples carry over between API calls"*: Each call is stateless. Examples must be included in every request that needs them.

**Incorrect implementations to watch for:**

- Placing output format specification before context (reduces compliance — put it last)
- Using inconsistent output format across few-shot examples
- Splitting on `"Answer:"` without checking if the marker exists in the response
- Writing role prompts with vague roles ("be helpful") that provide no real behavioral constraint

---

## 7. Completion Criteria

This step is complete when:
- All four labs execute correctly and meet the accuracy thresholds in section 4
- Conceptual questions in section 2 can be answered without consulting the documentation
- Practical tasks in section 3 can be completed from memory given an API client
- Integration reasoning in section 5 can be articulated for at least two module boundaries

---

## 8. Self-Assessment Checklist

```text
- [ ] I can name and describe all five prompt anatomy components
- [ ] I can write a few-shot prompt with consistent example format and correct label balance
- [ ] I can add chain-of-thought to a prompt and extract the final answer reliably
- [ ] I can implement role prompting, output format specification, and step-by-step instruction
- [ ] I can identify under-specification, over-specification, and instruction conflict by their symptoms
- [ ] I can explain why prompt injection cannot be fully prevented at the prompt level
- [ ] I understand how example token cost relates to context budget
- [ ] I can build a benchmark harness and use it to test a prompt before deployment
```

---

## 9. Next Steps

**If validation passes:** Proceed to `structured-outputs`. Output format specification via prompt is the foundation; structured outputs adds schema enforcement and function calling to make format compliance a hard guarantee rather than a best-effort instruction.

**If conceptual gaps remain:** Re-read the relevant topic. The most common gaps are CoT answer extraction mechanics (`chain-of-thought.md`) and the over-specification failure mode (`prompt-pitfalls.md`).

**If labs fail to produce expected accuracy:** Check example quality in `lab-few-shot` — label imbalance and format inconsistency are the most common causes. For `lab-chain-of-thought`, confirm the answer marker appears in the prompt and the parser splits on the correct string.
