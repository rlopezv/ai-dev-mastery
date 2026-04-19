---
id: "llm-fundamentals-inference-parameters"
title: "Inference Parameters"
type: "topic"
step: "llm-fundamentals"
path: "docs/llm-fundamentals/inference-parameters.md"
status: "final"
level: "foundational"
concepts:
  - "inference-parameters"
  - "temperature"
  - "top-k-sampling"
  - "top-p-sampling"
  - "greedy-decoding"
prerequisites:
  - "docs/llm-fundamentals/llm-architecture.md"
next:
  - "docs/llm-fundamentals/fine-tuning.md"
related:
  - "docs/llm-fundamentals/tokenization.md"
  - "docs/llm-fundamentals/context-window.md"
implementation_refs:
  - "labs/llm-fundamentals/lab-inference-parameters"
validation_refs:
  - "meta/standards/validation/docs-checklist.md"
summary: "Explains how temperature, top-k, and top-p control the probability distribution from which output tokens are sampled, and the engineering trade-offs of each setting."
---

# Inference Parameters

## Navigation

[Docs](../README.md) / [LLM Fundamentals](README.md) / Inference Parameters

---

## 1. Intuition

The transformer's output layer produces a probability distribution over every token in the vocabulary — tens of thousands of candidates, each with an assigned probability. The model does not decide what to say; it computes probabilities, and a sampling algorithm picks the next token from that distribution. Inference parameters are controls on that sampling step, not on the model's internal reasoning.

Think of it as a biased coin flip for each token. Temperature determines how biased the coin is. Top-k and top-p determine which outcomes are even eligible to be flipped.

---

## 2. Explanation

### 2.1 Why

Without sampling controls, generation would be greedy: always pick the highest-probability token. Greedy decoding is deterministic and fast but produces repetitive, formulaic output. In open-ended generation, always choosing the most probable word leads to the same sentence structures and vocabulary appearing repeatedly.

Sampling uniformly from the full distribution solves repetition but introduces incoherence — low-probability tokens such as rare characters, grammatically wrong words, or off-topic terms appear frequently. The output becomes random rather than useful.

Inference parameters navigate the middle ground. The goal is output that is varied enough to be useful and constrained enough to remain coherent. The correct trade-off depends on the task: code generation tolerates almost no variance (there is a correct answer), creative writing benefits from higher variance, and factual Q&A sits in between.

### 2.2 How

**Temperature**

Temperature rescales the raw output scores (logits) before the softmax that produces the final probability distribution:

```
scaled_logit[i] = logit[i] / temperature
```

- **Temperature > 1.0** — divides by a number greater than 1, reducing the contrast between high and low scores. The distribution flattens: lower-probability tokens become relatively more likely.
- **Temperature < 1.0** — divides by a fraction, amplifying the contrast. The distribution sharpens: the highest-probability token becomes even more dominant.
- **Temperature = 0** — equivalent to argmax selection (greedy decoding). The token with the highest score is always chosen. Output is deterministic for a fixed model version.

**Top-k sampling**

Top-k restricts the sampling pool to exactly the k tokens with the highest post-temperature probabilities. All other tokens are set to zero probability before re-normalization. This prevents any very-low-probability token from being selected regardless of temperature.

`k=1` is greedy decoding. `k=40` to `k=100` are common defaults. Top-k is applied after temperature scaling.

**Top-p (nucleus) sampling**

Top-p selects the smallest set of tokens whose cumulative probability sum reaches or exceeds p, then samples from that set. Unlike top-k, the pool size adapts to the distribution's shape:

- When the model is confident — one token has probability 0.95 — top-p at 0.9 selects only that token.
- When the model is uncertain — no token exceeds 0.05 — top-p at 0.9 keeps many candidates.

This makes top-p more robust than top-k across tasks with varying certainty levels.

**Application order**

In most implementations, parameters are applied in sequence: temperature rescales the logits → top-k truncates the pool → top-p further restricts it → one token is sampled from the remaining candidates.

### 2.3 Code example

```python
# See: labs/llm-fundamentals/lab-inference-parameters/main.py
import requests

def generate(prompt, temperature=1.0, top_k=40, top_p=0.9):
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
        },
    })
    return response.json()["response"]

# Deterministic — greedy decoding
print(generate("The capital of France is", temperature=0))

# High variance — creative task
print(generate("Once upon a time", temperature=1.2, top_k=100, top_p=0.95))
```

---

## 3. Inference Parameter Reference

| Parameter | Controls | Typical range | Effect at extremes |
|-----------|----------|---------------|--------------------|
| `temperature` | Width of the probability distribution | 0.0–2.0 | 0 = deterministic; 2.0 = near-random |
| `top_k` | Maximum number of candidate tokens | 1–100+ | 1 = greedy; 100+ = wide pool |
| `top_p` | Cumulative probability threshold for the candidate pool | 0.1–1.0 | 1.0 = no restriction; 0.1 = very narrow pool |
| `max_tokens` | Hard cap on completion length | 1–model limit | Truncates response when reached |
| `repeat_penalty` | Penalty applied to recently generated tokens | 1.0–1.5 | Reduces repetition loops in long outputs |

---

## 4. Engineering Implications

**Use temperature 0 for deterministic tasks.** Classification, information extraction, structured output generation, and any task with a single correct answer should use `temperature=0`. This makes output reproducible and testable — a prerequisite for automated evaluation and production monitoring.

**Temperature and top-p interact.** Applying high temperature and low top-p simultaneously can produce unexpected behavior: the distribution is widened by temperature but immediately re-narrowed by top-p. For most applications, adjust one at a time. A common safe starting point: `temperature=0.7`, `top_p=0.9`, `top_k=40`.

**High temperature does not improve quality.** Increasing temperature raises diversity but also raises the probability of grammatically inconsistent or factually wrong tokens. Quality and diversity trade off directly. Use the lowest temperature that produces acceptable variation for the task.

**`max_tokens` is a cost and context control, not a quality control.** Set it to a value slightly above the expected response length for the task. Leaving it unset or set too high wastes tokens on unnecessarily long responses and consumes context budget in multi-turn applications.

**Inference parameters do not affect the model's knowledge.** They control how the model samples from its learned distribution. A model that does not know the answer to a question will hallucinate at any temperature setting — low temperature makes it more confidently wrong, not less wrong.

---

## 5. Implementation Connection

`labs/llm-fundamentals/lab-inference-parameters` runs the same prompt with systematically varied parameter combinations, making the effects directly observable. The lab demonstrates:

- Identical prompts with `temperature=0` versus `temperature=1.5` to show the variance difference
- Top-k at 1 (greedy) versus 50 versus 100 on an open-ended prompt
- Top-p at 0.5 versus 0.95 on a factual question to show pool restriction in action
- Multiple runs at the same non-zero temperature to confirm output variance

The lab uses a locally running Ollama model and requires no external API keys. All variation is produced by changing the `options` block in the API request.

---

## 6. Failure Modes and Limitations

**Temperature 0 does not guarantee reproducibility across model versions.** Greedy decoding is deterministic for a fixed set of weights. When a provider updates a model — even a minor version bump — the weights change and greedy output may differ. Do not rely on temperature-0 outputs being identical across provider updates.

**Provider default values differ.** OpenAI, Anthropic, and Ollama use different default values for temperature and top-p. A prompt tuned on one provider's defaults will behave differently when moved to another provider without explicitly setting parameters. Always set inference parameters explicitly for any production prompt.

**Low temperature amplifies systematic errors.** If a model is systematically biased toward a wrong answer for a category of inputs, temperature 0 will produce that wrong answer reliably and consistently. Determinism is not accuracy — it just removes noise. Systematic errors become more, not less, visible.

**Combining aggressive top-k and high temperature can conflict.** High temperature widens the distribution but small top-k immediately re-narrows it to a fixed number of tokens. The tokens kept may not be representative of a naturally wide distribution. This combination is rarely useful and is usually a misconfiguration.

---

## 7. Summary

Inference parameters control the sampling step that converts the model's probability distribution into a token selection. Temperature rescales the distribution's width; top-k and top-p restrict which tokens are eligible for sampling. The practical decision rule is direct: low temperature for tasks with correct answers, higher temperature for open-ended tasks, and always set max_tokens explicitly. These parameters do not affect what the model knows — only how it expresses uncertainty in its output.
