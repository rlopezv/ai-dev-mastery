---
id: "llm-fundamentals-architecture"
title: "LLM Fundamentals — Architecture"
type: "architecture"
step: "llm-fundamentals"
path: "docs/llm-fundamentals/architecture.md"
status: "final"
level: "foundational"
concepts:
  - "inference-pipeline"
  - "context-assembler"
  - "autoregressive-generation"
prerequisites:
  - "docs/llm-fundamentals/README.md"
next:
  - "docs/llm-fundamentals/implementation-reference.md"
related:
  - "docs/llm-fundamentals/llm-architecture.md"
  - "docs/llm-fundamentals/tokenization.md"
  - "docs/llm-fundamentals/context-window.md"
  - "docs/llm-fundamentals/inference-parameters.md"
implementation_refs:
  - "labs/llm-fundamentals/"
validation_refs:
  - "meta/standards/validation/docs-checklist.md"
summary: "Describes the LLM inference pipeline — from text input through tokenization, context assembly, transformer forward pass, and token sampling — and maps each component to the labs in this module."
---

# LLM Fundamentals — Architecture

## Navigation

[Docs](../README.md) / [LLM Fundamentals](README.md) / LLM Fundamentals — Architecture

---

## 1. System Overview

The system described in this document is the **LLM inference pipeline**: the sequence of operations that transforms a text prompt into a generated response. This is the runtime system exercised by every API call in every subsequent module.

Understanding this pipeline at the component level converts API knowledge — "send a prompt, get a response" — into architectural knowledge: which component drives cost, where failure modes originate, and where each engineering technique (RAG, memory management, agents) intervenes.

The pipeline has five stages: input tokenization, context assembly, transformer forward pass, token sampling, and output decoding. Stages 3–5 repeat in an autoregressive loop until a stop condition is met.

---

## 2. Core Components

| Component | Role | Responsibility |
|-----------|------|----------------|
| Tokenizer | Input and output codec | Encodes text into token ID sequences; decodes token IDs back to text |
| Context assembler | Input builder | Combines system prompt, conversation history, retrieved content, and user message into a single ordered token sequence within the context window budget |
| Transformer model | Core compute unit | Executes a forward pass over the full token sequence through attention and feed-forward layers; produces a logit vector of size [vocab\_size] |
| Sampling algorithm | Output selector | Applies temperature, top-k, and top-p to the logit distribution; samples one token ID |
| Autoregressive loop | Generation controller | Appends each sampled token to the sequence and triggers the next forward pass; terminates on stop token or max\_tokens limit |

---

## 3. Component Interactions

The components form a linear pipeline with one internal feedback loop:

```
Tokenizer → Context assembler → Transformer → Sampling → [feedback] → Transformer
```

**Key dependencies:**

- The context assembler depends on the tokenizer to count tokens for budget validation before the forward pass.
- The sampling algorithm receives inference parameters (temperature, top-k, top-p, max\_tokens) from the caller — these are not properties of the model but of the request.
- The autoregressive loop feeds each generated token back into the context as input for the next forward pass. The full sequence grows by one token per iteration.
- The loop terminates when the sampling algorithm selects a stop token defined by the model (e.g., `<|eot_id|>`) or when the accumulated output token count reaches max\_tokens.

---

## 4. Data Flow

```
Input text (prompt components)
    │
    ▼
[Tokenizer — encode]
    │  token ID sequences per component
    ▼
[Context assembler]
    │  concatenate: system → history → retrieved content → user message
    │  validate: total_tokens + max_tokens ≤ context_window_limit
    │  truncate oldest history if over budget
    ▼
[Transformer — forward pass]
    │  self-attention + feed-forward over full token sequence
    │  output: logit vector [vocab_size floats]
    ▼
[Sampling algorithm]
    │  apply temperature → top-k → top-p → sample
    │  output: one token ID
    ▼
[Autoregressive loop]
    │  append token ID to sequence
    │  if stop token or max_tokens reached → exit loop
    │  else → back to Transformer forward pass
    ▼
[Tokenizer — decode]
    │  token ID sequence → UTF-8 text
    ▼
Response text
```

---

## 5. Execution Flow

1. The caller sends a request containing prompt components (system prompt, history, user message) and request parameters (inference parameters, max\_tokens).
2. The tokenizer encodes each text component into its token ID sequence.
3. The context assembler concatenates the sequences in canonical order: system prompt → conversation history (oldest to newest) → retrieved content → current user message.
4. The assembler validates the total token count against the context window limit. If `total_input_tokens + max_tokens > limit`, it truncates the oldest history turns until the budget is satisfied.
5. The transformer executes a single forward pass over the assembled sequence, producing a logit vector.
6. The sampling algorithm applies temperature scaling, top-k truncation, and top-p nucleus filtering to the logit vector, then draws one token ID from the resulting distribution.
7. The drawn token ID is appended to the sequence. If it is a stop token, generation ends. If max\_tokens has been reached, generation ends.
8. Otherwise, the transformer executes another forward pass over the extended sequence (steps 5–7 repeat).
9. After the loop exits, the tokenizer decodes all generated token IDs into the response text.
10. The response is returned to the caller along with metadata: prompt token count, completion token count, and generation timing.

---

## 6. Integration Points

**Caller / application layer**
Provides prompt components, inference parameters, and max\_tokens. All context management decisions — truncation strategy, history inclusion, retrieved chunk selection — happen here before the pipeline begins. The pipeline itself is stateless.

**Ollama API (local infrastructure)**
Wraps the transformer and sampling steps behind an HTTP endpoint. `POST /api/generate` accepts `prompt`, `model`, `options` (inference parameters), and `images`. Response metadata (`prompt_eval_count`, `eval_count`) maps directly to context assembler output and autoregressive loop output.

**Next module — `llm-apis`**
Covers the full API contracts of OpenAI, Anthropic, and Ollama. Each provider exposes a different surface over the same underlying pipeline described here. Parameter naming differs (`max_tokens` vs `max_completion_tokens`), but the pipeline is the same.

**Later modules**
- `prompt-engineering` — interventions at the context assembler stage (how to structure prompt components)
- `rag` — inserts a retrieval step that populates the retrieved content slot before context assembly
- `memory-context` — manages the history component across multi-turn calls
- `ai-agents` — adds a decision layer after the sampling step that can trigger tool calls and re-enter the pipeline

---

## 7. Trade-offs and Design Decisions

**Autoregressive generation is sequential by design.** Each token requires a full forward pass, and each forward pass depends on the previous token. Latency therefore scales linearly with output length. This is why streaming APIs return tokens as they are generated — the server produces them one at a time and has no reason to buffer them. Speculative decoding reduces latency by predicting multiple tokens per pass, but this is an optimization of the same sequential structure.

**The context window is a hard budget, not a soft limit.** Soft limits — truncating silently, summarizing automatically — would obscure cost and behavior. The fixed budget makes per-call compute cost predictable and hardware requirements fixed. The application layer is explicitly responsible for what goes in the window; the model is not.

**Inference parameters are caller-supplied, not model-internal.** Temperature, top-k, and top-p are properties of the request, not the model. This means the same model can behave deterministically for structured output tasks and variably for creative tasks with no model change required. The separation keeps the model stateless and the calling convention explicit.

---

## 8. Mapping to Labs

| Pipeline component | Lab | What to observe |
|--------------------|-----|-----------------|
| Transformer + autoregressive loop | `lab-llm-anatomy` | Token counts, generation metadata, model introspection via Ollama API |
| Tokenizer (encode/decode) | `lab-tokenization` | Token IDs, boundary behavior, cross-model differences |
| Context assembler (budget validation) | `lab-context-window` | Token consumption per component, truncation onset, budget arithmetic |
| Sampling algorithm | `lab-inference-parameters` | Output variance across temperature/top-k/top-p settings |

---

## 9. Limitations and Boundaries

**Inference only.** This architecture describes the runtime generation pipeline. Training, pre-training, and fine-tuning use a different computational graph (backward pass, gradient accumulation, optimizer step) that is not covered here.

**Single-turn completion.** The pipeline shown treats each API call independently. Persistent conversation management — deciding what history to retain, when to summarize, how to compress — is the subject of the `memory-context` module.

**No retrieval.** The context assembler shown here has no retrieval step. RAG pipelines insert a document retrieval stage that populates the retrieved content slot before context assembly. That architecture is covered in the `rag` module.

**No tool execution.** The pipeline terminates at response text. Agent architectures extend it by parsing the response for tool calls, executing them, and feeding results back into a new context assembly. That extension is covered in `ai-agents`.

---

## 10. Summary

The LLM inference pipeline consists of five components: tokenizer, context assembler, transformer, sampling algorithm, and autoregressive loop. Text enters as prompt components, is assembled into a token sequence within a fixed context budget, processed by the transformer to produce logits, sampled to select one token at a time, and decoded back to text after the loop terminates. This pipeline is stateless, sequential, and bounded. Every technique introduced in later modules — prompt engineering, RAG, memory management, agents — is an intervention at a specific stage of this pipeline.
