---
id: "llm-apis-validation"
title: "LLM APIs — Validation"
type: "validation"
step: "llm-apis"
path: "docs/llm-apis/validation.md"
status: "draft"
level: "foundational"

concepts:
  - "chat-completion-api"
  - "openai-compatible-api"
  - "streaming"
  - "provider-abstraction"
  - "retry-with-backoff"
  - "conversation-accumulation"

prerequisites:
  - "docs/llm-apis/implementation-reference.md"

next:
  - "docs/prompt-engineering/README.md"

related:
  - "docs/llm-apis/README.md"
  - "docs/llm-apis/api-patterns.md"

implementation_refs:
  - "labs/llm-apis/lab-openai-api"
  - "labs/llm-apis/lab-ollama-api"
  - "labs/llm-apis/lab-anthropic-api"
  - "labs/llm-apis/lab-streaming"
  - "labs/llm-apis/lab-api-patterns"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"
  - "meta/standards/validation/labs-checklist.md"

summary: "Defines the conceptual, practical, and lab-level criteria that confirm a learner has mastered LLM API interaction across providers, streaming, and common patterns."
---

# LLM APIs — Validation

## Navigation

[Docs](../README.md) / [LLM APIs](README.md) / LLM APIs — Validation

---

## 1. Validation Overview

This step is complete when the learner can make API calls to all three providers (OpenAI/Ollama, Anthropic), consume streaming responses, and implement the three core patterns (retry, accumulation, abstraction) in application code. Mastery at this level is practical: it is demonstrated by running code that produces correct results, not by reciting definitions.

---

## 2. Conceptual Validation

| Concept | Validation Method |
|---------|------------------|
| Chat completion API | Explain the message list structure, why the API is stateless, and what `finish_reason` signals |
| OpenAI-compatible API | Explain which parameter change is sufficient to redirect the OpenAI SDK to Ollama |
| Message roles | Explain what each role (`system`, `user`, `assistant`) communicates to the model and why the distinction exists |
| OpenAI vs. Anthropic schema | Identify the three concrete fields that differ between the two providers' request and response schemas |
| Streaming | Explain why streaming reduces perceived latency without reducing total generation time |
| First token latency | Explain the mechanism that produces shorter first-token latency in streaming mode |
| Retry with backoff | Explain why doubling the delay on each retry is preferable to a fixed interval, and which error types should not be retried |
| Conversation accumulation | Explain why token cost grows linearly with conversation length and what the application must do to keep it bounded |

---

## 3. Practical Validation

```text
Task 1: Send a 3-turn conversation to Ollama using the OpenAI SDK
Expected: Each turn references the previous one correctly; final reply is coherent

Task 2: Send the same conversation to Anthropic using the Messages API
Expected: System prompt is a top-level field; messages alternate user/assistant; reply text is read from content[0].text

Task 3: Stream a response from any provider and print tokens as they arrive
Expected: Output appears progressively; full assembled text matches what a batch call would return

Task 4: Implement retry with backoff for a function that fails on the first two attempts
Expected: Function succeeds on the third attempt; total elapsed time reflects the backoff delays

Task 5: Wrap OpenAI and Anthropic calls behind a common interface
Expected: The same caller code produces a ChatResponse from both providers without modification
```

---

## 4. Lab Validation

| Lab | Validation Criteria |
|-----|---------------------|
| `lab-openai-api` | Sends a chat request; parses `choices[0].message.content`; reads `usage.prompt_tokens` and `usage.completion_tokens`; checks `finish_reason` |
| `lab-ollama-api` | Uses OpenAI SDK with `base_url` override; also calls native Ollama `/api/tags` endpoint and lists available models |
| `lab-anthropic-api` | Sends request with `system` as top-level field; reads `content[0].text`; reads `usage.input_tokens` and `usage.output_tokens`; checks `stop_reason` |
| `lab-streaming` | Iterates chunk deltas; accumulates full text; prints tokens as they arrive; confirms assembled text matches expected content |
| `lab-api-patterns` | Implements retry that succeeds on third attempt; runs 5-turn conversation with coherent history; calls both providers through a normalized interface |

---

## 5. Integration Validation

At this point in the roadmap, the learner should be able to reason across module boundaries:

- **From `llm-fundamentals`**: Token count in `usage.prompt_tokens` reflects the tokenization of the messages list. A longer system prompt or more conversation history directly increases this count and consumes context window budget.
- **To `prompt-engineering`**: Prompt design strategies — few-shot examples, chain-of-thought — are expressed as additional messages or content in the `system` field. The API call itself does not change; only the message content changes.
- **To `structured-outputs`**: Tool use and function calling are extensions of the chat completion request that add a `tools` field. The message accumulation pattern must be extended to include `tool_use` and `tool_result` messages.

A learner who cannot explain how `usage.prompt_tokens` connects to the context window model from `llm-fundamentals` has not integrated the concepts across modules.

---

## 6. Failure Detection

**Common misconceptions:**

- *"The API remembers the conversation"*: Every call sends the full history. There is no server-side session. Removing the message history from a request produces a stateless, context-free response.
- *"Streaming is faster"*: Total generation time is identical. Only first-token latency changes.
- *"OpenAI and Anthropic work the same way"*: Three specific fields differ: `system` placement, response text path, and usage field names. Code that ignores these differences will fail silently or raise exceptions.
- *"A 429 error means the request is invalid"*: Rate limit errors are transient — the request is valid but the quota is temporarily exhausted. Retrying is the correct response.

**Incorrect implementations to watch for:**

- Sending `role: "system"` as a message in the Anthropic API
- Not checking `finish_reason` and treating all responses as complete
- Accumulating messages without trimming, causing context window overflow after many turns
- Using `response.choices[0].message.content` for an Anthropic response

---

## 7. Completion Criteria

This step is complete when:
- All four required labs (`lab-openai-api`, `lab-ollama-api`, `lab-anthropic-api`, `lab-streaming`) execute correctly and produce expected output
- Conceptual questions in section 2 can be answered without consulting the documentation
- Practical tasks in section 3 can be implemented from memory given the SDK documentation
- Integration reasoning in section 5 can be articulated without prompting

---

## 8. Self-Assessment Checklist

```text
- [ ] I can explain why the Chat Completions API is stateless and what that means for history management
- [ ] I can switch the OpenAI SDK between OpenAI and Ollama by changing one parameter
- [ ] I understand the three structural differences between the OpenAI and Anthropic APIs
- [ ] I can consume a streaming response and assemble it into a complete string
- [ ] I can implement retry with exponential backoff that distinguishes retryable from non-retryable errors
- [ ] I can implement a conversation accumulator that appends both user and assistant turns
- [ ] I can write a provider abstraction that returns the same structure from both OpenAI and Anthropic
- [ ] I can explain why token cost grows with conversation length and how to control it
```

---

## 9. Next Steps

**If validation passes:** Proceed to `prompt-engineering`. The API call infrastructure established in this module is the execution layer for everything that follows.

**If conceptual gaps remain:** Re-read the topic where the gap is. The most common gaps at this stage are the Anthropic schema differences (`anthropic-api.md`) and the mechanics of streaming chunk accumulation (`streaming.md`).

**If labs fail to execute:** Verify that Ollama is running and the target model is available. For cloud provider labs, confirm that `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` are set in the environment. Refer to `labs/llm-apis/README.md` for setup instructions.
