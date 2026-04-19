---
id: "llm-apis-readme"
title: "LLM APIs"
type: "step-readme"
step: "llm-apis"
path: "docs/llm-apis/README.md"
status: "draft"
level: "foundational"

concepts:
  - "chat-completion-api"
  - "openai-compatible-api"
  - "streaming"
  - "api-client"
  - "api-patterns"

prerequisites:
  - "docs/llm-fundamentals/README.md"

next:
  - "docs/llm-apis/openai-api.md"

related:
  - "docs/prompt-engineering/README.md"
  - "docs/llm-fundamentals/context-window.md"

implementation_refs:
  - "labs/llm-apis/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Covers how to interact with LLM providers through their HTTP APIs — OpenAI, Ollama, and Anthropic — and the common patterns that make API-level code robust and portable."
---

# LLM APIs

## Navigation

[Docs](../README.md) / LLM APIs

---

## 1. Overview

An LLM's intelligence is only accessible through an API call. This step moves from conceptual understanding of how LLMs work to practical ability to invoke them from application code. It covers three providers with different API designs — OpenAI, Ollama, and Anthropic — plus the cross-cutting concerns that apply to all of them: streaming, error handling, and common integration patterns.

Understanding the API contract at this level is prerequisite to everything that follows. Prompt engineering, RAG retrieval, and agent tool use are all operations that ultimately resolve to one or more API calls. The patterns established here — message structure, response parsing, streaming, error handling — recur throughout the tutorial.

---

## 2. Scope

**Covered:**
- The OpenAI Chat Completions API: message roles, request structure, response parsing, usage metadata
- The Ollama local API: OpenAI-compatible interface, local model management
- The Anthropic Messages API: how it differs from OpenAI's design and why
- Streaming: server-sent events, token deltas, and when to use streaming
- API patterns: retry with backoff, conversation accumulation, provider abstraction

**Not covered:**
- Prompt design strategies (see `prompt-engineering`)
- Structured outputs and function calling (see `structured-outputs`)
- Embeddings APIs (see `rag`)
- Performance optimization and caching (see `performance-optimization`)
- Model evaluation or benchmarking (see `evaluation-testing`)

---

## 3. Key Concepts

**Chat completion API**
The dominant interface for LLM interaction. A caller sends an ordered list of messages, each with a role and content, and receives a generated reply. The conversation is stateless on the server side — the caller manages history.

**OpenAI-compatible API**
A REST API that implements the same request and response schema as OpenAI's Chat Completions endpoint. Ollama, many open-source serving frameworks, and some commercial providers expose this interface, making client code portable across providers without modification.

**Streaming**
A delivery mode in which the model's response is transmitted as a sequence of token deltas over a persistent HTTP connection (SSE), rather than as a single response after full generation. Streaming reduces perceived latency at the cost of more complex client-side assembly.

**API client**
A language-level library that wraps the raw HTTP calls to a provider's API, handling authentication, serialization, and often retry logic. The OpenAI Python SDK and the Anthropic Python SDK are the primary clients used in this module.

**API patterns**
Recurring implementation strategies — retry with exponential backoff, conversation history accumulation, provider abstraction via a common interface — that make API-level code resilient and maintainable.

---

## 4. Concept Map

```
openai-api ──────────────────────┐
                                  ▼
ollama-api ──► openai-compatible-api ──► chat-completion-api
                                  │
anthropic-api ────────────────────┘
                    │
                    ▼
              streaming ──► server-sent events ──► token delta
                    │
                    ▼
             api-patterns ──► retry / conversation / abstraction
```

- **OpenAI** and **Ollama** share the same API schema; client code is interchangeable.
- **Anthropic** uses a different schema; it requires separate handling.
- **Streaming** applies to all three providers, with provider-specific delta formats.
- **API patterns** are provider-agnostic strategies applied on top of any provider's client.

---

## 5. Learning Flow

| Order | Topic | Dependency |
|-------|-------|------------|
| 1 | `openai-api.md` | llm-fundamentals |
| 2 | `ollama-api.md` | openai-api |
| 3 | `anthropic-api.md` | openai-api |
| 4 | `streaming.md` | openai-api, ollama-api |
| 5 | `api-patterns.md` | all above |
| 6 | `architecture.md` | all topics |
| 7 | `implementation-reference.md` | architecture |
| 8 | `validation.md` | all above |

Read topics 1–3 in sequence before starting the labs. Streaming and patterns build on direct API knowledge. Run each required lab immediately after its corresponding topic.

---

## 6. Documentation Structure

```text
docs/llm-apis/
├── README.md                    ← this file
├── openai-api.md                ← OpenAI Chat Completions API
├── ollama-api.md                ← Ollama local API
├── anthropic-api.md             ← Anthropic Messages API
├── streaming.md                 ← SSE streaming across providers
├── api-patterns.md              ← retry, accumulation, abstraction
├── architecture.md              ← system-level view of this step
├── implementation-reference.md  ← bridge to lab execution
└── validation.md                ← completion criteria
```

---

## 7. Labs Overview

| Lab | Type | Purpose |
|-----|------|---------|
| `lab-openai-api` | implementation | Send chat completion requests to an OpenAI-compatible endpoint and parse structured responses |
| `lab-ollama-api` | implementation | Invoke Ollama's local API directly and via the OpenAI-compatible interface |
| `lab-anthropic-api` | implementation | Send requests to the Anthropic Messages API and handle its distinct response structure |
| `lab-streaming` | implementation | Consume streaming responses from multiple providers and assemble the token stream client-side |
| `lab-api-patterns` | implementation | Implement retry with backoff, conversation accumulation, and a provider-switching abstraction |

All labs use the `foundational` infrastructure profile. `lab-openai-api` and `lab-anthropic-api` require valid API keys in the environment.

---

## 8. How to Use This Step

**Recommended path:**
1. Read this README to orient yourself.
2. Read `openai-api.md` and run `lab-openai-api`.
3. Read `ollama-api.md` and run `lab-ollama-api`.
4. Read `anthropic-api.md` and run `lab-anthropic-api`.
5. Read `streaming.md` and run `lab-streaming`.
6. Read `api-patterns.md`. Run `lab-api-patterns` if you want pattern practice.
7. Read `architecture.md` and `implementation-reference.md`.
8. Complete `validation.md` before moving to `prompt-engineering`.

**Optional path:**
If you only need Ollama for local development, you can skip `lab-openai-api` and `lab-anthropic-api`. However, read all three topic files — the API design differences are architecturally relevant.

---

## 9. Relationship to Other Steps

| Position | Step | Relationship |
|----------|------|--------------|
| Before | `llm-fundamentals` | Token, context window, and inference parameter concepts are assumed throughout this step. |
| After | `prompt-engineering` | Prompt design strategies are applied through the API calls established here. |
| Later dependency | `structured-outputs` | Function calling and structured responses are extensions of the basic chat completion request. |
| Later dependency | `rag` | Retrieval pipelines inject context into API calls; the API call itself is the terminal step. |

---

## 10. Next Steps

Begin with the first topic:

→ [`docs/llm-apis/openai-api.md`](./openai-api.md)

---

## 11. Engineering Takeaways

### What This Adds

Practical ability to invoke LLMs from application code — handling authentication, message structure, streaming, and error recovery across multiple providers. Every AI capability in subsequent modules resolves to one or more API calls; this module establishes the call contract.

### Engineering Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Provider abstraction layer | Swap providers without code changes | Extra indirection; abstraction may not cover provider-specific features |
| Streaming vs batch responses | Lower perceived latency for end users | More complex client-side assembly; harder to test |
| Retry with exponential backoff | Resilience to transient provider errors | Adds latency on failures; masks persistent errors if not bounded |

### When NOT to Use This

- When the problem does not require language generation — a deterministic API or rule engine is cheaper and more predictable.
- When provider availability or cost is a hard constraint — evaluate feasibility before building the integration layer.

### Common Failure Modes

- **Failure:** Conversation accumulates unbounded and exhausts the context window.
  **Cause:** History is appended on every turn without a length check or truncation strategy.
  **Signal:** API returns a context length exceeded error after N turns.

- **Failure:** Role order errors cause unexpected model behavior.
  **Cause:** Messages sent with incorrect or swapped roles (e.g., system content in user role).
  **Signal:** Model ignores system instructions or responds as if in a different persona.

- **Failure:** Streaming responses silently dropped.
  **Cause:** Stream buffer not fully consumed before the response is considered complete.
  **Signal:** Truncated output; missing end-of-stream event handling.

### What Changes vs Traditional Systems

API calls become the I/O boundary of the system, not internal function calls. The application owns state — every call is stateless on the provider side, so conversation history must be managed explicitly. Authentication and rate limits add operational constraints that do not exist in internal APIs.

### Minimal Adoption Heuristic

**Use this when:**
- You need to call any LLM provider from application code — this is the foundational interface layer.

**Avoid this when:**
- You are evaluating whether AI is needed at all — make that decision first using the concepts from `llm-fundamentals`.
