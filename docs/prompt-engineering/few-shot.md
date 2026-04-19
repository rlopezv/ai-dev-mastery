---
id: "prompt-engineering-few-shot"
title: "Few-Shot Prompting"
type: "topic"
step: "prompt-engineering"
path: "docs/prompt-engineering/few-shot.md"
status: "draft"
level: "foundational"

concepts:
  - "few-shot-prompting"
  - "in-context-learning"
  - "zero-shot-prompting"
  - "shot"

prerequisites:
  - "docs/prompt-engineering/prompt-anatomy.md"

next:
  - "docs/prompt-engineering/chain-of-thought.md"

related:
  - "docs/prompt-engineering/prompt-patterns.md"
  - "docs/prompt-engineering/chain-of-thought.md"

implementation_refs:
  - "labs/prompt-engineering/lab-few-shot"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how providing labeled input/output examples inside the prompt causes the model to infer and replicate task behavior without explicit instructions — and when this is more reliable than instruction alone."
---

# Few-Shot Prompting

## Navigation

[Docs](../README.md) / [Prompt Engineering](README.md) / Few-Shot Prompting

---

## 1. Intuition

Telling a model what to do is often less effective than showing it. When you include two or three labeled examples of the task you want performed, the model infers the pattern from those examples and applies it to the new input — even if you never explicitly stated the rule. This is few-shot prompting: teaching by demonstration rather than specification.

---

## 2. Explanation

### 2.1 Why

Instruction-only (zero-shot) prompts rely on the model's ability to correctly interpret a natural language description of the task. For well-defined, common tasks — "translate this text to French" — this works reliably. For tasks with a specific output format, a non-standard classification scheme, or domain-specific conventions, zero-shot interpretation diverges from intent.

Few-shot prompting sidesteps the interpretation problem: instead of describing the task in words, you demonstrate it. The model observes the input/output pattern across multiple examples and extrapolates to the new input. This is reliable for tasks where the pattern is consistent and the examples are representative.

### 2.2 How

Each example in a few-shot prompt is a pair: an input (the same kind of input you will ask the model to process) and an output (the exact response you would want for that input). The examples are placed in the prompt before the target input — the one you actually want the model to answer.

The number of examples is a "shot count":
- **Zero-shot**: no examples — instruction only
- **One-shot**: one example
- **Few-shot**: two to five examples (most common)
- **Many-shot**: ten or more examples (token cost grows proportionally)

```python
# See: labs/prompt-engineering/lab-few-shot/main.py
system = "You are a sentiment classifier."

user = """Classify the sentiment of each review as positive, negative, or neutral.

Review: "Absolutely love this product, works perfectly."
Sentiment: positive

Review: "Terrible quality, broke after one day."
Sentiment: negative

Review: "It arrived on time. Does what it says."
Sentiment: neutral

Review: "The screen is bright but the battery drains fast."
Sentiment:"""
# The model continues the pattern: "negative" or "mixed" depending on its interpretation
```

The final `Sentiment:` with no answer is the target. The model completes the sequence by continuing the established pattern.

### 2.3 Example quality and selection

| Example property | Effect on output |
|-----------------|-----------------|
| Representative of the task range | Model handles edge cases correctly |
| Consistent output format across all examples | Output format is stable |
| Balanced across classes (for classification) | No label bias toward majority class |
| Ordered randomly | Less sensitive to recency bias |
| Containing the target input's features | Generalizes correctly to target |

---

## 3. Table

| Approach | When to use | Token cost | Reliability |
|----------|-------------|------------|-------------|
| Zero-shot | Simple, well-defined tasks; standard formats | Lowest | Variable |
| One-shot | When output format is non-standard | Low | Moderate |
| Few-shot (2–5) | Custom classification; domain-specific formats | Medium | High |
| Many-shot (10+) | Complex tasks needing broad coverage | High | Very high |

---

## 4. Engineering Implications

Each example consumes tokens — both the input part and the output part. For a classification task with 50-token inputs and 1-token outputs, five examples cost approximately 255 tokens per request, every request. In high-volume applications, example token cost is a fixed overhead that must be accounted for in context budget planning.

Examples are re-sent on every API call because the API is stateless. In a system that processes thousands of requests, the same five examples are transmitted thousands of times. This is the correct behavior, but it has a direct cost implication and affects prompt caching strategies (covered in `performance-optimization`).

The position of examples relative to the target input matters. Always place examples immediately before the target — not at the beginning of a long prompt with many intervening tokens. Models with limited context attend more strongly to recent tokens; examples far from the target may have reduced influence.

---

## 5. Implementation Connection

`lab-few-shot` builds a topic classifier that assigns incoming text to one of four categories. It runs each classification task in three modes — zero-shot, one-shot, and three-shot — and prints the accuracy across a fixed test set. The observable outcome is the accuracy difference between modes: zero-shot typically underperforms on ambiguous inputs that the examples would disambiguate.

---

## 6. Failure Modes and Limitations

**Label leakage in examples**: If all examples happen to have the same output label (e.g. all "positive"), the model learns to always output that label regardless of input. Select examples that represent the full output space.

**Format inconsistency across examples**: If one example outputs `"Sentiment: positive"` and another outputs `"positive"`, the model may alternate between formats unpredictably. All examples must use identical output format.

**Example-target mismatch**: If the target input is qualitatively different from all examples — longer, in a different domain, or in a different language — few-shot performance degrades. The model extrapolates pattern, but far from the examples, extrapolation fails.

**Token budget exhaustion**: At large example counts, examples can consume most of the context budget, leaving too little for long target inputs. Measure example token cost and set an upper bound on shot count for the input size range expected in production.

---

## 7. Summary

Few-shot prompting replaces explicit task description with demonstrated examples. The model infers the intended pattern from two to five input/output pairs and applies it to the target input. It is more reliable than zero-shot for tasks with non-standard output formats or domain-specific conventions. The cost is token overhead proportional to the number of examples, and that overhead is paid on every request. Example quality — representativeness, format consistency, label balance — determines whether few-shot delivers its reliability benefit or fails silently.
