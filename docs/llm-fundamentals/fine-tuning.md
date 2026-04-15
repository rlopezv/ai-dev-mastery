---
id: "llm-fundamentals-fine-tuning"
title: "Fine-Tuning"
type: "topic"
step: "llm-fundamentals"
path: "docs/llm-fundamentals/fine-tuning.md"
status: "draft"
level: "foundational"
concepts:
  - "fine-tuning"
  - "supervised-fine-tuning"
  - "instruction-tuning"
  - "lora"
prerequisites:
  - "docs/llm-fundamentals/llm-architecture.md"
next:
  - "docs/llm-fundamentals/multimodality.md"
related:
  - "docs/llm-fundamentals/inference-parameters.md"
  - "docs/llm-fundamentals/context-window.md"
implementation_refs: []
validation_refs:
  - "meta/standards/validation/docs-checklist.md"
summary: "Explains what fine-tuning changes in a model's weights, the main approaches, and when fine-tuning is the right choice versus prompt engineering or RAG."
---

## 1. Intuition

A pre-trained LLM is a general-purpose text predictor. Fine-tuning continues its training on a smaller, task-specific dataset to shift its behavior without changing its architecture. The model learns to produce outputs that match the patterns in the training data — consistent formats, domain vocabulary, refusal behaviors — as durable learned patterns in its weights rather than as instructions in every prompt.

Think of it as the difference between training someone and briefing them. A brief (system prompt) works for every individual conversation but must be repeated. Training (fine-tuning) shapes behavior permanently and requires no repeated instruction.

---

## 2. Explanation

### 2.1 Why

Pre-trained models are optimized to predict general text. This makes them broadly capable but inconsistent on specific requirements: a customer support bot may not follow company escalation policies, a code generation tool may not match a team's style conventions, and some behaviors — like reliably refusing specific request categories — are difficult to enforce through prompting alone.

Fine-tuning addresses this by encoding the desired behavior into the model's weights. After fine-tuning, the behavior is present in every generation without requiring it to be specified in the prompt. This matters for three reasons: consistency across calls, reduced prompt length (and therefore reduced cost and context consumption), and behaviors that prompting cannot reliably produce.

That said, fine-tuning is not always the right tool. It is expensive to build, maintain, and upgrade. The decision between fine-tuning, RAG, and prompt engineering depends on what kind of change is needed — not on how sophisticated the solution should appear.

### 2.2 How

**Supervised Fine-Tuning (SFT)**

The most common approach. A dataset of (input, output) pairs is assembled representing the desired model behavior. The model is trained to minimize the cross-entropy loss between its predictions and the target outputs — the same objective as pre-training, but on a small, curated dataset. Updating all model weights requires significant GPU memory. Training time ranges from hours to days depending on model size and dataset size.

**Instruction tuning**

A specific form of SFT where the training data consists of (instruction, response) pairs covering a wide range of tasks. This is how base models — raw next-token predictors — are converted into instruction-following assistants. GPT-4, Claude, and Llama-Instruct are instruction-tuned variants of their respective base models. Instruction tuning requires thousands to hundreds of thousands of examples and is rarely done outside model providers.

**LoRA (Low-Rank Adaptation)**

Instead of updating all model weights, LoRA inserts small trainable matrices alongside the frozen original weight matrices in the attention layers. The original weights are never modified; only the adapter matrices — typically less than 1% of the total parameter count — are trained. This reduces memory requirements by 10–100x relative to full fine-tuning, making adaptation feasible on a single consumer GPU.

LoRA adapters are stored separately from the base model and merged at inference time. A single base model can have multiple LoRA adapters for different tasks, switched at runtime without reloading the base weights.

**RLHF (Reinforcement Learning from Human Feedback)**

A multi-stage process: SFT on demonstration data, followed by training a reward model on human preference comparisons, followed by optimizing the policy model against the reward signal. This approach shapes safety behaviors, preference alignment, and refusal patterns at the frontier. It requires substantial infrastructure and human annotation and is performed by model providers, not application developers.

### 2.3 Code example

Fine-tuning is compute-intensive and performed offline. The example below shows the training data format used for SFT, not a runnable training loop.

```python
# No lab for this topic — concept-only
#
# Example: SFT training data in JSONL format (OpenAI fine-tuning API convention)
# Each line is one training example.
#
# {"messages": [
#     {"role": "system",    "content": "Return only valid JSON. No explanation."},
#     {"role": "user",      "content": "List three European capitals."},
#     {"role": "assistant", "content": "[\"Paris\", \"Berlin\", \"Rome\"]"}
# ]}
#
# Each example encodes one (input → output) mapping.
# 100–10,000 high-quality examples is a typical SFT dataset size.
# Data quality drives outcomes more than data quantity.
```

---

## 3. Choosing Between Fine-Tuning, RAG, and Prompting

| Need | Recommended approach | Reason |
|------|---------------------|--------|
| Consistent output format or style | Fine-tuning (LoRA) | Behavior encoded in weights; no prompt repetition |
| Domain-specific factual knowledge | RAG | Fine-tuning does not reliably improve recall of specific facts |
| New information not in training data | RAG | Weights cannot be updated at inference time |
| Task-specific behavior with low latency | Fine-tuning | No retrieved content to inject; shorter prompts |
| Safety or refusal behavior | SFT or RLHF | Application-layer guardrails also required |
| Fast iteration and experimentation | Prompt engineering | No training infrastructure needed |

**Fine-tuning approaches by resource requirement:**

| Approach | What changes | Hardware | Training time |
|----------|-------------|----------|---------------|
| Full SFT | All model weights | Multi-GPU cluster | Hours to days |
| LoRA | Adapter matrices (~1% of params) | Single GPU | Minutes to hours |
| Instruction tuning | All weights, via instruction-response data | Multi-GPU cluster | Days |
| RLHF | Policy weights via reward model | Multi-GPU + annotators | Days to weeks |

---

## 4. Engineering Implications

**Fine-tuning is an operational commitment, not a one-time cost.** Every base model upgrade — a new provider version, a quantization change, a security patch — requires re-fine-tuning and re-evaluating the adapter. Teams that fine-tune take on a maintenance burden that must be justified by a benefit that prompting cannot provide.

**Fine-tuning does not add factual knowledge reliably.** Training a model on company documents will not make it accurately recall specific facts from those documents at inference time. Fine-tuning shifts behavioral patterns; it does not improve retrieval of specific knowledge. For knowledge retrieval, RAG is the correct tool.

**Data quality dominates data quantity.** 200 high-quality (input, output) pairs with consistent formatting and correct outputs consistently outperform 5,000 noisy examples. Garbage training data produces garbage fine-tuned behavior. Curation is the primary cost in fine-tuning, not compute.

**Fine-tuned models still require application-layer safety.** Fine-tuning can reduce the frequency of unwanted outputs but cannot eliminate them. Jailbreaks, prompt injection, and adversarial inputs can still elicit undesired behavior from fine-tuned models. Safety requires defense in depth — fine-tuning is one layer, not the complete solution.

---

## 5. Implementation Connection

There is no lab for this topic. Fine-tuning requires compute infrastructure beyond the tutorial's local setup.

This topic provides the conceptual foundation for:

- The `frameworks-tools` module, which covers libraries that wrap fine-tuning workflows (Hugging Face `transformers`, LlamaFactory, Unsloth)
- The `evaluation-testing` module, where the behavioral consistency introduced by fine-tuning must be measured systematically against a baseline
- The `safety-guardrails` module, where the limits of fine-tuning as a safety mechanism are examined alongside application-layer alternatives

The decision framework in section 3 directly informs architecture decisions throughout the intermediate and advanced modules.

---

## 6. Failure Modes and Limitations

**Overfitting on small datasets.** A model trained on too few examples memorizes the training data rather than generalizing. Output quality degrades sharply on inputs that differ from the training distribution. Validation loss on a held-out set must be monitored; training loss alone is not sufficient.

**Catastrophic forgetting.** Heavy fine-tuning on a narrow domain can degrade the model's performance on tasks outside that domain. The model becomes more consistent on the target task but worse at everything else. LoRA mitigates this by keeping original weights frozen, but does not eliminate it entirely.

**Data contamination.** If training data overlaps with evaluation data, fine-tuning performance metrics are inflated. Training and evaluation splits must be strictly separated before fine-tuning begins, not after.

**Fine-tuning is not a security boundary.** Models fine-tuned to refuse certain request types remain susceptible to adversarial prompts that reframe those requests. Refusal behavior introduced by fine-tuning is a statistical tendency, not a hard constraint. Application-layer input and output guardrails are required for any security guarantee.

---

## 7. Summary

Fine-tuning shifts a pre-trained model's behavior by continuing its training on task-specific (input, output) pairs, encoding the desired patterns as durable weight updates. The main approaches — SFT, LoRA, instruction tuning, and RLHF — differ in what they update and at what resource cost. The right choice between fine-tuning, RAG, and prompting follows from the type of change needed: behavioral consistency belongs to fine-tuning, factual knowledge retrieval belongs to RAG, and rapid iteration belongs to prompting. Fine-tuning carries real maintenance costs that must be weighed explicitly against prompt-only alternatives before committing.
