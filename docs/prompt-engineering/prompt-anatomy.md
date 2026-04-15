---
id: "prompt-engineering-prompt-anatomy"
title: "Prompt Anatomy"
type: "topic"
step: "prompt-engineering"
path: "docs/prompt-engineering/prompt-anatomy.md"
status: "draft"
level: "foundational"

concepts:
  - "prompt-anatomy"
  - "instruction"
  - "context"
  - "output-format"
  - "zero-shot-prompting"

prerequisites:
  - "docs/llm-apis/openai-api.md"
  - "docs/llm-fundamentals/context-window.md"

next:
  - "docs/prompt-engineering/few-shot.md"

related:
  - "docs/prompt-engineering/prompt-patterns.md"
  - "docs/llm-apis/anthropic-api.md"

implementation_refs:
  - "labs/prompt-engineering/lab-prompt-anatomy"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes the structural components of a prompt — instruction, context, examples, and output format — and explains what each communicates to the model and how their arrangement affects output."
---

## 1. Intuition

A prompt is not a single piece of text — it is a composition of distinct functional components. Changing one component while holding others constant produces predictably different output. Understanding which component does what is the prerequisite to writing prompts that work reliably rather than by trial and error.

---

## 2. Explanation

### 2.1 Why

When a prompt fails to produce the intended output, the cause is almost always structural: a component is missing, ambiguous, or in the wrong position. Without a model of what a prompt is made of, debugging is guesswork. With it, failures map to specific components — a missing output format, a conflicting instruction, an underspecified context — and fixes become targeted.

The API call structure (system + messages) from `llm-apis` provides slots for these components, but it does not define what belongs in each slot. Prompt anatomy answers that question.

### 2.2 How

A well-formed prompt has up to five components. Not every prompt needs all five, but omitting one that is needed produces unreliable output.

**System prompt**
Sets the model's role, behavioral constraints, and persistent instructions. Evaluated before every user message. Changes here affect all subsequent turns. In the OpenAI API, this is `role: "system"`; in Anthropic, it is the top-level `system` field.

**Instruction**
The explicit task directive. Tells the model what to do: classify, summarize, translate, extract, generate. The instruction should be unambiguous about the action and the expected output shape.

**Context**
Background information the model needs to complete the task but does not already know. For a classification task, context is the text to be classified. For a code review task, context is the code. Context consumes the most tokens in most practical prompts.

**Examples**
Labeled input/output pairs that demonstrate the expected behavior. Covered in detail in `few-shot.md`. When present, examples anchor the model's output pattern more reliably than instruction alone.

**Output format**
An explicit specification of how the response should be structured — JSON, bullet list, single word, a specific template. Without this, the model chooses its own format, which varies across calls and models.

```python
# See: labs/prompt-engineering/lab-prompt-anatomy/main.py
system = "You are a sentiment classifier. Respond with a single word: positive, negative, or neutral."

user = """
Classify the sentiment of the following review.

Review: "The product arrived on time but the packaging was damaged."

Respond with one word only.
"""
# Components present: system (role + constraint), instruction ("classify"),
# context (the review), output format ("one word only")
```

### 2.3 Component order and placement

The model processes the token sequence from top to bottom. Component placement matters:

| Position | Effect |
|----------|--------|
| System prompt | Highest weight on behavior; applies to all turns |
| Early in user message | Establishes task frame before context |
| Context block | Provides the material to operate on |
| Examples (if any) | Immediately before the target input |
| Output format instruction | At the end — last thing the model reads before generating |

Placing the output format instruction at the very end reduces drift: the model's generation starts immediately after seeing the constraint.

---

## 3. Table

| Component | What it communicates | Token cost | Required |
|-----------|---------------------|------------|----------|
| System prompt | Role, persistent rules, safety constraints | Low–medium | Recommended |
| Instruction | The action to perform | Low | Yes |
| Context | The input material for the task | Medium–high | Task-dependent |
| Examples | The expected pattern (few-shot) | Medium per example | Optional |
| Output format | Response structure and constraints | Low | Recommended |

---

## 4. Engineering Implications

Every component consumes tokens. A system prompt that grows to 500 tokens on every call adds 500 tokens to every request — including short ones where most of the instructions are irrelevant. Prompt anatomy enables budgeting: count tokens per component, identify what is essential vs. decorative, and trim accordingly.

The system prompt is evaluated once per API call, not once per session. In a multi-turn conversation, the system prompt is re-sent on every request. Long system prompts in long conversations are expensive and may compete with conversation history for context budget.

A prompt with only an instruction and no output format specification is a zero-shot prompt. Zero-shot works for well-defined, simple tasks. For anything that requires a specific structure, explicit output format specification is not optional — it is the difference between parsing the response reliably and writing fragile string extraction code.

---

## 5. Implementation Connection

`lab-prompt-anatomy` isolates each component by removing it from an otherwise complete prompt and measuring the effect on output consistency. It runs the same task five times with different component configurations and prints the results side by side. The goal is direct observation: see what happens when the output format is omitted, when the instruction is ambiguous, when context is missing.

---

## 6. Failure Modes and Limitations

**Missing output format**: Without an explicit format, the model may answer in prose one time and bullet points the next. Application code that parses the response will break on the less common format.

**Conflicting instructions**: A system prompt that says "be concise" and a user message that says "explain in detail" produces inconsistent output — sometimes following one, sometimes the other. Resolve conflicts explicitly rather than hoping the model will pick the right interpretation.

**Context position**: Placing the instruction after a large context block can cause the model to partially ignore the instruction, especially for smaller models. Keep instructions before or alongside context, not buried after it.

**Zero-shot as default**: Many prompts work zero-shot during development but fail on edge cases that examples would have covered. The absence of examples is a design choice, not a default — consider whether the task needs them.

---

## 7. Summary

A prompt is composed of five functional components: system prompt, instruction, context, examples, and output format. Each communicates a distinct signal to the model. Missing or mispositioned components produce inconsistent output. Understanding anatomy transforms prompt debugging from guesswork into targeted fixes: identify which component is absent or ambiguous, and address it directly. All techniques in this module — few-shot, chain-of-thought, patterns — are structured applications of these five components.
