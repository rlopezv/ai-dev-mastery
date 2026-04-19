---
id: "prompt-engineering-chain-of-thought"
title: "Chain-of-Thought"
type: "topic"
step: "prompt-engineering"
path: "docs/prompt-engineering/chain-of-thought.md"
status: "draft"
level: "foundational"

concepts:
  - "chain-of-thought"
  - "intermediate-reasoning-steps"
  - "scratchpad"

prerequisites:
  - "docs/prompt-engineering/prompt-anatomy.md"

next:
  - "docs/prompt-engineering/prompt-patterns.md"

related:
  - "docs/prompt-engineering/few-shot.md"
  - "docs/prompt-engineering/prompt-patterns.md"

implementation_refs:
  - "labs/prompt-engineering/lab-chain-of-thought"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains why asking a model to reason step-by-step before answering improves accuracy on multi-step tasks, and how to elicit and use intermediate reasoning steps in application code."
---

# Chain-of-Thought

## Navigation

[Docs](../README.md) / [Prompt Engineering](README.md) / Chain-of-Thought

---

## 1. Intuition

An LLM generates one token at a time. When asked a complex question directly, it must compress the entire reasoning chain into the probability distribution for a single answer token — and that compression loses information. Asking it to write out its reasoning first gives the model a scratchpad: each reasoning step becomes input to the next, and the final answer is drawn from a much richer context.

---

## 2. Explanation

### 2.1 Why

Multi-step reasoning tasks — arithmetic, logic puzzles, code debugging, multi-hop questions — require the model to maintain intermediate state. But the model has no internal memory between tokens; all it can attend to is the tokens already generated. When the model generates an answer directly, the answer token must encode the entire reasoning process implicitly. For simple tasks this works; for tasks requiring three or more inferential steps, direct answering fails because the model cannot hold all intermediate results in its generation probability simultaneously.

Chain-of-thought works because it externalizes intermediate state. Each reasoning step is written as output tokens, which immediately become available as input context for the next step. The model is not reasoning in a hidden internal state — it is reading back its own reasoning from the generated text.

### 2.2 How

Chain-of-thought is elicited by prompting the model to show its work before giving the final answer. Two forms are common:

**Zero-shot chain-of-thought**: append "Let's think step by step." to the prompt. This single phrase is sufficient to elicit intermediate reasoning on most models.

**Few-shot chain-of-thought**: include examples where the answer is preceded by a worked reasoning trace.

```python
# See: labs/prompt-engineering/lab-chain-of-thought/main.py

# Direct (zero-shot) — often fails on multi-step reasoning
direct_prompt = """
A store has 48 apples. They sell 3/4 of them in the morning and receive
a delivery of 12 more in the afternoon. How many apples do they have now?
Answer with a number only.
"""

# Chain-of-thought — elicits step-by-step reasoning
cot_prompt = """
A store has 48 apples. They sell 3/4 of them in the morning and receive
a delivery of 12 more in the afternoon. How many apples do they have now?

Let's think step by step.
"""
# Expected reasoning: 48 × 0.75 = 36 sold → 48 - 36 = 12 remaining → 12 + 12 = 24
```

**Extracting the final answer**: when using chain-of-thought, the response contains both the reasoning trace and the answer. Application code must separate them. Common approaches:
- Ask the model to end with a specific format: "Therefore, the answer is: ___"
- Use a two-step call: first elicit the reasoning, then ask "Based on your reasoning above, what is the final answer?"
- Parse the last sentence or a structured marker from the response

```python
# See: labs/prompt-engineering/lab-chain-of-thought/main.py
# Two-step approach: reasoning first, then extract answer
cot_with_extraction = """
...problem statement...

Let's think step by step. At the end, state your final answer on a new line
starting with "Answer:".
"""
```

### 2.3 When chain-of-thought helps

| Task type | Direct answer | Chain-of-thought |
|-----------|--------------|-----------------|
| Multi-step arithmetic | Unreliable | Reliable |
| Logical deduction (3+ steps) | Unreliable | Reliable |
| Simple factual recall | Works | Unnecessary overhead |
| Sentiment classification | Works | Unnecessary overhead |
| Code debugging | Works | Better — traces through execution |
| Single-step extraction | Works | Unnecessary overhead |

---

## 3. Table

| CoT form | How to trigger | Token overhead | Best for |
|----------|---------------|---------------|----------|
| Zero-shot CoT | Append "Let's think step by step." | Medium | Quick improvement with no example cost |
| Few-shot CoT | Provide 2–3 examples with full reasoning traces | High | Highest accuracy on complex tasks |
| Structured CoT | Explicit step format + "Answer:" marker | Medium | When final answer must be parsed reliably |

---

## 4. Engineering Implications

Chain-of-thought increases output token count significantly. A task that would produce a 5-token direct answer may produce a 200-token reasoning trace followed by the answer. This has two consequences: higher cost per call (more completion tokens) and higher latency (more tokens to generate). For tasks that do not require reasoning, chain-of-thought adds cost without benefit.

In streaming mode, the reasoning trace appears first. If the UI displays the stream directly to the user, they see the thinking process. This is sometimes desirable (transparency) and sometimes not (cluttered output). Design the answer extraction step based on what the UI should show.

The reasoning trace is not guaranteed to be correct. The model can write a plausible-looking reasoning trace that leads to a wrong answer. Chain-of-thought improves accuracy but does not eliminate errors — especially on tasks that require precise arithmetic or formal logic. Always validate the final answer against constraints where possible.

---

## 5. Implementation Connection

`lab-chain-of-thought` runs a fixed set of multi-step reasoning problems in two modes — direct and chain-of-thought — and compares answer accuracy. It also demonstrates the answer extraction pattern using the "Answer:" marker. The observable outcome is the accuracy difference between modes; chain-of-thought consistently improves performance on problems with three or more inferential steps.

---

## 6. Failure Modes and Limitations

**Plausible but wrong reasoning**: The model can generate a coherent-looking reasoning trace that contains a factual or logical error. The final answer derived from that trace will also be wrong, and the trace makes the error harder to spot because it appears justified.

**Reasoning trace length explosion**: For open-ended tasks, "think step by step" can produce very long reasoning traces that consume most of the context budget. Add a constraint: "In at most 5 steps, think through the problem."

**Extraction failure**: If the prompt does not specify a consistent answer format, the final answer may be embedded anywhere in the reasoning trace. Without a reliable extraction marker ("Answer:", "Therefore:", a final JSON block), application code cannot reliably parse the answer.

**Degradation on simple tasks**: Appending chain-of-thought to a simple task adds latency and cost with no accuracy gain. Reserve chain-of-thought for tasks that actually require multi-step reasoning.

---

## 7. Summary

Chain-of-thought prompting asks the model to produce intermediate reasoning steps before answering. This works because each step becomes context for the next — the model reads back its own reasoning, allowing multi-step inference that direct answering cannot support. Zero-shot CoT ("Let's think step by step.") is the simplest form; few-shot CoT with full reasoning examples achieves the highest accuracy. The trade-off is increased output token count and latency. Application code must extract the final answer from the reasoning trace using a structured marker or a second API call.
