# Glossary

Cross-module reference for canonical term definitions.
Consulted throughout the tutorial — not part of any module sequence.

When writing documentation, always check this file before introducing a term.
Use the canonical name as defined here. Do not paraphrase or rename existing entries.

---

<!-- Entries are added here alphabetically as modules are written -->

### Anthropic Messages API
The HTTP API exposed by Anthropic for interacting with Claude models, distinguished from the OpenAI Chat Completions API by a separate top-level `system` field, a content block response structure, and different field names for token usage and stop reasons.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/anthropic-api.md`

### API client
A language-level library that wraps the raw HTTP calls to an LLM provider's API, handling authentication, serialization, and often retry logic; the OpenAI Python SDK and the Anthropic Python SDK are the primary clients used in this tutorial.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/openai-api.md`

### chat completion API
An HTTP interface for LLM interaction in which the caller sends an ordered list of role-labeled messages and receives a generated assistant reply; the API is stateless, and the caller is responsible for managing conversation history.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/openai-api.md`

### content block
A typed response unit in the Anthropic Messages API that encapsulates a single piece of generated output — text, tool call, or image — allowing a model response to contain multiple heterogeneous elements in a single call.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/anthropic-api.md`

### conversation accumulation
The pattern of appending each user message and assistant reply to a growing message list before every subsequent API call, enabling stateful multi-turn conversations over a stateless API.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/api-patterns.md`

### first-token latency
The elapsed time between sending an API request and receiving the first token of the response; in streaming mode this is typically under 500ms regardless of response length, whereas in batch mode it grows with total output length.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/streaming.md`

### local LLM runtime
A process that runs open-weight language models on local hardware and exposes them via an HTTP API, enabling offline development without cloud provider accounts or per-request costs; Ollama is the local runtime used in this tutorial.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/ollama-api.md`

### message role
A label on each message in a chat completion request that declares its origin and purpose: `system` for developer instructions, `user` for end-user input, and `assistant` for model replies or injected context.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/openai-api.md`

### OpenAI-compatible API
A REST API that implements the same request and response schema as the OpenAI Chat Completions endpoint, allowing client code written for OpenAI to run against other providers — such as Ollama — by changing only the `base_url` parameter.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/ollama-api.md`

### provider abstraction
A design pattern that normalizes provider-specific API schemas into a common response structure, localizing schema differences and enabling application logic to switch between providers without modification.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/api-patterns.md`

### rate limiting
A server-enforced constraint on the number of API requests or tokens a client may send within a time window, returning HTTP 429 when exceeded; transient and recoverable by retrying after a delay.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/api-patterns.md`

### retry with backoff
A resilience pattern that catches transient API errors and re-sends the request after an increasing delay — typically doubling on each attempt — to avoid overwhelming a rate-limited or temporarily unavailable endpoint.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/api-patterns.md`

### server-sent events
An HTTP mechanism in which the server writes a sequence of data lines to an open connection over time rather than closing it after a single response, used by LLM APIs to transmit token deltas as they are generated.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/streaming.md`

### streaming
A delivery mode for LLM API responses in which token deltas are transmitted over a persistent HTTP connection as they are generated, reducing first-token latency without changing total generation time.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/streaming.md`

### system prompt
The developer-controlled instruction text that establishes model behavior, persona, and constraints before the conversation begins; in the OpenAI API it is a message with `role: system`, and in the Anthropic API it is a separate top-level `system` field.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/anthropic-api.md`

### token delta
A partial response chunk transmitted during streaming, containing the one or more tokens generated since the previous chunk; the full response is reconstructed by concatenating all deltas received before the stream closes.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/streaming.md`

### usage metadata
The token count fields returned in every LLM API response — prompt tokens consumed and completion tokens generated — used for cost tracking, context budget management, and rate limit monitoring.
- **Origin:** `llm-apis`
- **Doc:** `docs/llm-apis/openai-api.md`

### catastrophic forgetting
The degradation of a model's general capabilities caused by heavy fine-tuning on a narrow domain, where the new weight updates overwrite patterns needed for tasks outside the training distribution.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/fine-tuning.md`

### autoregressive generation
A generation strategy in which the model produces one token at a time, appends it to the input sequence, and executes a new forward pass to produce the next token, repeating until a stop condition is reached.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/architecture.md`

### byte pair encoding
A subword tokenization algorithm that builds a vocabulary by iteratively merging the most frequent adjacent byte pairs in a training corpus until a target vocabulary size is reached.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/tokenization.md`

### greedy decoding
A token selection strategy that always picks the highest-probability token from the model's output distribution, equivalent to setting temperature to 0; deterministic for a fixed model version but prone to repetitive output.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/inference-parameters.md`

### feed-forward layer
A two-layer neural network applied independently to each token representation after self-attention, where learned associations and factual patterns are primarily stored.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/llm-architecture.md`

### completion tokens
The tokens generated by the model in response to an input prompt; counted separately from prompt tokens and bounded by the `max_tokens` parameter set by the caller.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/context-window.md`

### context assembler
The application-layer component responsible for combining system prompt, conversation history, retrieved content, and user message into a single ordered token sequence that fits within the context window budget.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/architecture.md`

### context truncation
The silent removal of tokens — typically the oldest conversation turns — when the total input exceeds the context window limit, without raising an error to the caller.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/context-window.md`

### context window
The maximum number of tokens an LLM can process in a single forward pass, covering both input and output tokens; once the limit is reached, earlier content is inaccessible to the model.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/context-window.md`

### fine-tuning
The process of continuing a pre-trained model's training on a task-specific dataset to shift the model's behavior by modifying its weights, without changing its architecture.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/fine-tuning.md`

### inference parameters
Numeric controls applied at generation time — such as temperature, top-k, and top-p — that shape the probability distribution from which output tokens are sampled.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/inference-parameters.md`

### prompt tokens
The tokens that form the input to a model in a single API call, including system prompt, conversation history, retrieved content, and the current user message.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/context-window.md`

### positional encoding
A vector added to each token embedding to inject sequence order information, enabling the transformer to distinguish between the same token appearing at different positions.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/llm-architecture.md`

### residual connection
A pattern that adds a sub-layer's input directly to its output before passing to the next stage, preserving the original signal and enabling stable gradient flow through many stacked layers.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/llm-architecture.md`

### instruction tuning
A form of supervised fine-tuning where the training data consists of (instruction, response) pairs covering a wide range of tasks, converting a base language model into an instruction-following assistant.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/fine-tuning.md`

### inference pipeline
The sequence of operations that transforms a text prompt into a generated response: tokenization, context assembly, transformer forward pass, token sampling, and autoregressive loop until a stop condition is met.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/architecture.md`

### large language model
A neural network trained on large text corpora to predict the probability distribution over the next token given a sequence of input tokens, with behavior at inference time determined by weights established during training.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/llm-architecture.md`

### temperature
An inference parameter that rescales the model's output logits before softmax, controlling the width of the probability distribution; values below 1.0 sharpen the distribution toward the top token, values above 1.0 flatten it.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/inference-parameters.md`

### top-k sampling
A token selection strategy that restricts the sampling pool to the k tokens with the highest probabilities after temperature scaling, zeroing out all other candidates before re-normalization.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/inference-parameters.md`

### top-p sampling
A token selection strategy that retains the smallest set of tokens whose cumulative probability reaches a threshold p, adapting the pool size to the shape of the distribution rather than fixing a count.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/inference-parameters.md`

### self-attention
A mechanism in which each token computes a weighted sum of all other tokens' representations using learned Query, Key, and Value projections, allowing every token to directly attend to every other token in the input.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/llm-architecture.md`

### LoRA
A parameter-efficient fine-tuning technique that inserts small trainable adapter matrices alongside frozen original weight matrices in the attention layers, reducing memory requirements by 10–100x relative to full fine-tuning.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/fine-tuning.md`

### multimodal model
A model that accepts inputs from more than one modality — such as text and images — by encoding all inputs into a shared vector embedding space and processing them together in a single transformer forward pass.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/multimodality.md`

### multimodality
The ability of a model to process non-text inputs by encoding them into the same token space as text, enabling unified cross-modal reasoning over images, audio, or video.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/multimodality.md`

### supervised fine-tuning
A fine-tuning approach in which a model is trained on a curated dataset of (input, output) pairs to minimize prediction error on those examples, shifting the model's behavior toward the patterns represented in the data.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/fine-tuning.md`

### token vocabulary
The fixed set of subword units a tokenizer can produce, with each unit assigned a unique integer ID; vocabulary size is determined at tokenizer training time and cannot be changed at inference time.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/tokenization.md`

### tokenizer
The component that encodes text into token IDs and decodes token IDs back to text using a fixed vocabulary and merge rules established at training time.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/tokenization.md`

### token embedding
A dense vector representation of a token ID that encodes the token's identity in a high-dimensional space, serving as the model's internal representation of each input token.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/llm-architecture.md`

### tokenization
The process of converting raw text into integer token IDs that a language model processes, where token boundaries do not align with word boundaries.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/tokenization.md`

### vision encoder
A neural network — typically a Vision Transformer (ViT) or convolutional model — that divides an image into patches, encodes each patch into a dense vector, and projects those vectors into a language model's embedding space for joint attention with text tokens.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/multimodality.md`

### transformer architecture
A neural network design that uses self-attention to allow each token in a sequence to attend to all other tokens, enabling parallel processing and long-range dependency modeling.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/llm-architecture.md`

---

## Maintenance

### When to update

Update this file whenever a document introduces a concept listed in its frontmatter
`concepts` field that does not yet have an entry here.

This check is performed automatically by Claude Code as part of the write and fix tasks.

### Entry format

```markdown
### <term>
<One-sentence canonical definition.>
- **Origin:** `<module-name>`
- **Doc:** `docs/<module-name>/<topic>.md`
```

Example:

```markdown
### embedding
Vector representation of text that encodes semantic meaning as a point
in high-dimensional space, enabling similarity search via geometric distance.
- **Origin:** `llm-fundamentals`
- **Doc:** `docs/llm-fundamentals/llm-architecture.md`
```

### Rules

- One entry per term — no duplicates
- Definition must be one sentence
- Do not modify existing entries without explicit human instruction
- If a term conflicts with an existing entry, flag it with a comment:

```markdown
<!-- CONFLICT: <term> defined differently in <module> — needs human review -->
```
