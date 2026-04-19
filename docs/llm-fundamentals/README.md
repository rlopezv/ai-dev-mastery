---
id: "llm-fundamentals-readme"
title: "LLM Fundamentals"
type: "step-readme"
step: "llm-fundamentals"
path: "docs/llm-fundamentals/README.md"
status: "final"
level: "foundational"
concepts:
  - "large-language-model"
  - "transformer-architecture"
  - "tokenization"
  - "context-window"
  - "inference-parameters"
  - "fine-tuning"
  - "multimodality"
prerequisites: []
next:
  - "docs/llm-fundamentals/llm-architecture.md"
related:
  - "docs/llm-apis/README.md"
implementation_refs:
  - "labs/llm-fundamentals/"
validation_refs:
  - "meta/standards/validation/docs-checklist.md"
summary: "Introduces the mechanical foundations of large language models — how they process text, generate output, and can be adapted — establishing the conceptual basis for every subsequent module."
---

# LLM Fundamentals

## Navigation

[Docs](../README.md) / LLM Fundamentals

---

## 1. Overview

LLMs are probabilistic text completion engines built on the transformer architecture. Before writing a single prompt or API call, an architect must understand what an LLM actually does: it converts text to tokens, processes those tokens through attention layers, and produces a probability distribution over the next token. Every engineering decision downstream — prompt design, context sizing, API selection, RAG retrieval — is a consequence of this mechanism.

This step establishes that mechanical understanding. It covers how transformers process input, why tokenization affects both cost and behavior, how context windows impose a hard memory limit, how inference parameters shape output distribution, and what fine-tuning means architecturally. Two additional topics — fine-tuning and multimodality — are covered conceptually because they appear frequently in architecture discussions even when not directly implemented.

---

## 2. Scope

**Covered:**
- Transformer architecture at the conceptual level (attention, feed-forward layers, residual connections)
- Tokenization mechanics and their engineering consequences (cost, truncation, language bias)
- Context window: what it is, how it is consumed, and why it imposes a hard limit
- Inference parameters: temperature, top-k, top-p, and their effect on output distribution
- Fine-tuning: what changes in the model weights and when it is the right choice
- Multimodality: how non-text inputs are encoded and integrated

**Not covered:**
- Training from scratch or pre-training mechanics
- Mathematical derivations of attention (softmax, QKV matrices)
- GPU memory management or inference optimization (see `performance-optimization`)
- Benchmarking or evaluation of specific models (see `evaluation-testing`)
- API-level usage patterns for specific providers (see `llm-apis`)

---

## 3. Key Concepts

**Large language model (LLM)**
A neural network trained on large text corpora to predict the next token. Its behavior at inference time is determined by weights established during training, not by runtime logic.

**Transformer architecture**
The neural network design underlying modern LLMs. Its core mechanism — self-attention — allows each token to attend to every other token in the context, enabling the model to represent long-range dependencies in parallel.

**Tokenization**
The process of converting raw text into the integer token IDs that the model processes. Token boundaries do not align with word boundaries, which has direct consequences for prompt cost, context budgeting, and behavior across languages.

**Context window**
The maximum number of tokens an LLM can process in a single forward pass, covering both input and output. Once the limit is reached, earlier content is not accessible to the model.

**Inference parameters**
Numeric controls applied at generation time that shape the probability distribution from which output tokens are sampled. Temperature, top-k, and top-p are the most common and have predictable, testable effects.

**Fine-tuning**
The process of continuing model training on a task-specific dataset to shift the model's behavior without changing its architecture. Fine-tuning modifies weights; prompting does not.

**Multimodality**
The ability of a model to process non-text inputs — images, audio, video — by encoding them into the same token space used for text, enabling unified cross-modal reasoning.

---

## 4. Concept Map

```
tokenization ──────────────► context-window
                                    │
transformer-architecture ──────────►│◄── inference-parameters
                                    │
                           large-language-model
                                    │
                    ┌───────────────┴───────────────┐
               fine-tuning                    multimodality
```

- **Tokenization** determines how text consumes the context window.
- **Transformer architecture** defines the model's internal capacity and how input tokens are processed.
- **Inference parameters** control how the model samples from the output distribution at generation time.
- **Fine-tuning** and **multimodality** are architectural extensions of the base model concept rather than runtime mechanisms.

---

## 5. Learning Flow

Read topics in this sequence. Each topic depends on the one before it.

| Order | Topic | Dependency |
|-------|-------|------------|
| 1 | `llm-architecture.md` | none |
| 2 | `tokenization.md` | llm-architecture |
| 3 | `context-window.md` | tokenization |
| 4 | `inference-parameters.md` | llm-architecture |
| 5 | `fine-tuning.md` | llm-architecture |
| 6 | `multimodality.md` | llm-architecture |
| 7 | `architecture.md` | all topics |
| 8 | `implementation-reference.md` | architecture |
| 9 | `validation.md` | all above |

Labs are designed to run alongside topics 1–4. Run each lab immediately after reading its corresponding topic.

---

## 6. Documentation Structure

```text
docs/llm-fundamentals/
├── README.md                    ← this file
├── llm-architecture.md          ← transformer internals
├── tokenization.md              ← token encoding and consequences
├── context-window.md            ← input budget and truncation
├── inference-parameters.md      ← temperature, top-k, top-p
├── fine-tuning.md               ← weight adaptation (concept-only)
├── multimodality.md             ← non-text input encoding (concept-only)
├── architecture.md              ← system-level view of this step
├── implementation-reference.md  ← bridge to lab execution
└── validation.md                ← completion criteria
```

---

## 7. Labs Overview

| Lab | Type | Purpose |
|-----|------|---------|
| `lab-llm-anatomy` | observation | Inspect LLM internals by querying model metadata via the Ollama API |
| `lab-tokenization` | observation | Observe how the same text tokenizes differently across models and languages |
| `lab-context-window` | observation | Test context limits by progressively filling the window and observing truncation behavior |
| `lab-inference-parameters` | observation | Compare generation outputs across temperature, top-k, and top-p settings |

All labs use the `foundational` infrastructure profile (Ollama + API). No vector database is required.

---

## 8. How to Use This Step

**Recommended path:**
1. Read this README to orient yourself.
2. Read each topic in the sequence defined in section 5.
3. Run the corresponding lab immediately after each topic that has one.
4. Read `architecture.md` after completing all topics.
5. Read `implementation-reference.md` for setup context before running labs.
6. Complete `validation.md` to confirm your understanding before moving to `llm-apis`.

**Optional path:**
If you already have a working understanding of transformer architecture, skip `llm-architecture.md` and begin with `tokenization.md`. Do not skip the labs — observation reinforces conceptual knowledge that is easy to misremember.

---

## 9. Relationship to Other Steps

| Position | Step | Relationship |
|----------|------|--------------|
| Before | — | This is the first step. No prerequisites. |
| After | `llm-apis` | API usage patterns assume the context window, tokenization, and inference parameter concepts established here. |
| Later dependency | `prompt-engineering` | Prompt structure decisions are directly constrained by tokenization and context window mechanics. |
| Later dependency | `rag` | RAG is a strategy for working around context window limits — understanding that motivation requires this step. |

---

## 10. Next Steps

Begin with the first topic:

→ [`docs/llm-fundamentals/llm-architecture.md`](./llm-architecture.md)

---

## 11. Engineering Takeaways

### What This Adds

A mechanical understanding of how LLMs process text, generate output, and respond to runtime controls. This is the conceptual prerequisite for every subsequent engineering decision — prompt structure, API usage, context sizing, retrieval, and agent design all depend on understanding what happens inside the model.

### Engineering Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Temperature 0 for determinism | Reproducible outputs, easier testing | Loses variance; may miss valid phrasings |
| Larger context window | More history, richer retrieval context | Higher cost per call, higher memory pressure |
| Fine-tuning vs prompting | Consistent behavior without prompt overhead | Training cost, dataset curation, retraining on changes |

### When NOT to Use This

- When the problem has a deterministic solution expressible in code — an LLM adds cost and unpredictability without benefit.
- When the data is structured and the task is classification or extraction with a finite label set — rule-based or ML classifiers are more reliable and cheaper.
- When output correctness must be verifiable and exact — LLM outputs are probabilistic and require validation layers.

### Common Failure Modes

- **Failure:** Context window overflow causes silent truncation.
  **Cause:** History or documents grow past the model's token limit without length checks.
  **Signal:** Model appears to "forget" earlier parts of the conversation.

- **Failure:** Unexpected token costs in production.
  **Cause:** Token count is underestimated because words and tokens do not align.
  **Signal:** Billing spikes; prompts hitting limits at different lengths than expected.

- **Failure:** Inconsistent output on repeated identical prompts.
  **Cause:** Temperature or sampling parameters set too high for production use.
  **Signal:** Same input produces structurally different outputs across runs.

### What Changes vs Traditional Systems

LLMs do not execute logic — they complete text. Behavior is shaped by input (the prompt), not by runtime control flow. The primary control surface moves from code to text. Testing shifts from pass/fail assertions to output distribution checks. Non-determinism is not a bug — it is a design constraint that must be accounted for.

### Minimal Adoption Heuristic

**Use this when:**
- The task requires reasoning over unstructured text, language generation, or pattern inference that is impractical to encode as rules.
- You need to evaluate whether AI is the right tool before committing to any framework or provider.

**Avoid this when:**
- The problem is well-defined and solvable with deterministic logic.
- You cannot tolerate probabilistic behavior without additional validation layers.
