---
id: "llm-fundamentals-llm-architecture"
title: "LLM Architecture"
type: "topic"
step: "llm-fundamentals"
path: "docs/llm-fundamentals/llm-architecture.md"
status: "final"
level: "foundational"
concepts:
  - "transformer-architecture"
  - "self-attention"
  - "token-embedding"
  - "feed-forward-layer"
  - "residual-connection"
prerequisites: []
next:
  - "docs/llm-fundamentals/tokenization.md"
related:
  - "docs/llm-fundamentals/context-window.md"
  - "docs/llm-fundamentals/fine-tuning.md"
implementation_refs:
  - "labs/llm-fundamentals/lab-llm-anatomy"
validation_refs:
  - "meta/standards/validation/docs-checklist.md"
summary: "Explains how the transformer architecture converts a token sequence into a probability distribution over the next token through attention and feed-forward layers."
---

# LLM Architecture

## Navigation

[Docs](../README.md) / [LLM Fundamentals](README.md) / LLM Architecture

---

## 1. Intuition

An LLM is a function that takes a sequence of tokens and returns a probability distribution over what token comes next. It has no understanding of truth, no memory between calls, and no access to external knowledge — it is a very large statistical pattern matcher trained on text.

The architecture that makes this work at scale is the transformer. Its key insight is that instead of reading tokens left to right in sequence, every token simultaneously considers every other token in the input. This one change — from sequential to parallel processing — is what made large-scale language modeling practical.

---

## 2. Explanation

### 2.1 Why

Before transformers, language models used recurrent architectures (RNNs, LSTMs) that processed tokens one at a time. The hidden state carried information forward, but by the time the model reached token 500, the signal from token 1 had been compressed and partially lost through hundreds of transformations. Long-range dependencies — the relationship between a pronoun and the noun it refers to three paragraphs earlier — were routinely missed.

The transformer eliminates this problem by computing attention across all tokens simultaneously in a single pass. Token 500 can directly attend to token 1 with no intermediate compression. This is why transformers handle long documents and complex reasoning chains better than recurrent architectures: the signal path between any two tokens is one step, not hundreds.

### 2.2 How

A transformer processes input through a fixed pipeline repeated across many layers:

**1. Tokenization and embedding**
Input text is first split into integer token IDs (tokenization is covered in the next topic). Each token ID is mapped to a dense vector — the token embedding — that encodes the token's identity. A positional encoding vector is added to each embedding so the model knows the order of tokens; without it, the architecture would treat input as an unordered set.

**2. Self-attention**
This is the core mechanism. For each token, three vectors are computed: Query (Q), Key (K), and Value (V). The attention score between token _i_ and token _j_ is the dot product of Q_i and K_j, scaled by the square root of the vector dimension, then passed through softmax to produce a weight. Token _i_'s output is a weighted sum of all Value vectors, where the weights are the attention scores to every other token.

In practice: token _i_ asks "which other tokens are most relevant to me?" (via Q×K), then assembles its new representation as a weighted blend of what those tokens contain (via V). Every token does this simultaneously.

**3. Feed-forward layer**
After attention, each token's representation passes independently through a small two-layer neural network with a non-linear activation. This layer applies the same transformation to every token position. Research suggests this is where factual associations and pattern completions are primarily stored — the "knowledge" layer.

**4. Residual connections and layer normalization**
Each sub-layer (attention, feed-forward) adds its output back to its input before passing to the next stage. This residual connection preserves the original signal, preventing it from being overwritten by each transformation. Layer normalization stabilizes the numerical values. Together they allow gradients to flow cleanly through dozens of stacked layers during training.

**5. Stacking and output projection**
The attention + feed-forward block is stacked multiple times. GPT-3 has 96 such layers. Each layer refines the token representations. After the final layer, each token's representation is projected onto the full vocabulary (a vector of ~50,000 values), then softmaxed to produce a probability distribution over what the next token should be.

### 2.3 Code example

```python
# See: labs/llm-fundamentals/lab-llm-anatomy/main.py
import requests

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama3.2",
    "prompt": "The capital of France is",
    "stream": False,
})

data = response.json()
print(data["response"])          # the generated text
print(data["eval_count"])        # output tokens generated
print(data["prompt_eval_count"]) # input tokens consumed
```

The Ollama API abstracts the transformer internals, but `eval_count` and `prompt_eval_count` make the token-based processing visible.

---

## 3. Transformer Component Breakdown

| Component | Role | Engineering consequence |
|-----------|------|------------------------|
| Token embedding | Maps each integer token ID to a dense vector | Vocabulary size and embedding dimension set the model's representational capacity |
| Positional encoding | Adds order information to token embeddings | Without it, the model treats input as an unordered bag of tokens |
| Self-attention | Computes weighted relationships between all token pairs | Scales as O(n²) in memory and compute — the source of context window cost |
| Feed-forward layer | Transforms each token representation independently | Stores learned associations; wider layers hold more knowledge |
| Residual connection | Adds sub-layer input to its output | Enables stable training through many layers |
| Layer normalization | Normalizes activations at each sub-layer | Prevents numerical instability during training |
| Output projection | Maps final token representation to vocabulary probabilities | Vocabulary size determines output resolution |

---

## 4. Engineering Implications

**Context window cost is quadratic.** Self-attention requires every token to attend to every other token. Doubling the context length quadruples the attention computation. This is why large context windows (128k, 1M tokens) are significantly more expensive per token than short ones.

**Inference is stateless.** The model has no memory between API calls. Every request processes the full input context from scratch. If you send the same conversation twice, the model recomputes attention over every token both times. Caching strategies (covered in `performance-optimization`) exist specifically to avoid this.

**Output is probabilistic, not deterministic.** The model returns a probability distribution, then samples from it. Running the same prompt twice can produce different outputs depending on sampling parameters. Deterministic output requires temperature 0 (greedy decoding), which has its own trade-offs.

**Model scale trades against inference cost.** A model with more layers and wider feed-forward layers is more capable but slower and more memory-intensive. Choosing a model for production means balancing capability against latency and cost — a decision that requires understanding what architectural scale buys.

---

## 5. Implementation Connection

`labs/llm-fundamentals/lab-llm-anatomy` connects these concepts to a running model via the Ollama API. The lab demonstrates:

- Sending a prompt and receiving a text completion
- Observing token counts (`prompt_eval_count`, `eval_count`) to make the input/output budget concrete
- Running the same prompt multiple times to observe output variation caused by sampling
- Querying available models to see how model metadata is exposed at the API level

The lab uses a locally running `llama3.2` model via the `foundational` infrastructure profile. No external API keys are required.

---

## 6. Failure Modes and Limitations

**Hallucination.** The transformer optimizes for the next probable token, not for factual accuracy. When the correct answer has low training-data frequency, the model generates a plausible-sounding but incorrect token sequence. There is no internal verification mechanism — the architecture has no concept of truth.

**Silent context truncation.** Content that exceeds the context window is dropped without error. The model simply cannot attend to it. Prompts that grow beyond the limit silently lose early content, including instructions that appear at the beginning.

**No runtime learning.** The model cannot update its weights during inference. New information must be injected through context (RAG) or through a new fine-tuning run. What looks like the model "learning" from conversation is just the conversation history appearing in the context window.

**Attention does not guarantee relevance.** High attention scores between two tokens indicate statistical co-occurrence in training data, not semantic relevance to the task. A model can confidently attend to irrelevant tokens if they pattern-match to familiar sequences.

---

## 7. Summary

The transformer converts a token sequence into a next-token probability distribution by computing self-attention across all input tokens simultaneously, then applying a feed-forward transformation at each layer. The architecture is stateless, probabilistic, and subject to a hard context window limit imposed by the quadratic cost of attention. These properties — not API details — are what determine how you design prompts, manage long inputs, and decide when retrieval or fine-tuning is needed.
