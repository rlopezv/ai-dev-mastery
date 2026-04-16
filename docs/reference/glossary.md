# Glossary

Cross-module reference for canonical term definitions.
Consulted throughout the tutorial — not part of any module sequence.

When writing documentation, always check this file before introducing a term.
Use the canonical name as defined here. Do not paraphrase or rename existing entries.

---

<!-- Entries are added here alphabetically as modules are written -->

### chain-of-thought
A prompting technique that asks the model to produce intermediate reasoning steps before the final answer, externalizing the reasoning process so each step becomes context for the next and enabling reliable multi-step inference.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/chain-of-thought.md`

### context
The background information or input material included in a prompt that the model needs to complete the task but does not already know, such as the text to classify, the code to review, or the document to summarize.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/prompt-anatomy.md`

### few-shot prompting
A technique that provides labeled input/output examples inside the prompt so the model can infer the expected task pattern from demonstration rather than from explicit instruction.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/few-shot.md`

### in-context learning
The ability of a language model to adapt its behavior to a task by observing examples provided in the prompt, without any change to the model's weights.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/few-shot.md`

### instruction
The explicit task directive within a prompt that tells the model what action to perform — classify, summarize, translate, extract, generate — and what the expected output shape is.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/prompt-anatomy.md`

### instruction conflict
A prompt design failure mode in which two instructions cannot both be satisfied simultaneously, causing the model to arbitrarily satisfy one and ignore the other.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/prompt-pitfalls.md`

### intermediate reasoning steps
The sequence of explicit reasoning operations a model produces before a final answer when chain-of-thought is elicited, each step serving as input context for the next.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/chain-of-thought.md`

### output-format specification
An explicit instruction within a prompt that defines the required structure of the model's response — JSON schema, bullet list, single word, or a specific template — to ensure the output can be parsed reliably.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/prompt-patterns.md`

### over-specification
A prompt design failure mode in which too many constraints are placed on the model's response, creating geometrically incompatible requirements that cause some constraints to be silently violated.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/prompt-pitfalls.md`

### prompt anatomy
The internal structure of a prompt as a composition of five functional components — system prompt, instruction, context, examples, and output format specification — each communicating a distinct signal to the model.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/prompt-anatomy.md`

### prompt injection
An attack in which user-provided content introduces new instructions into the prompt that override or extend the original developer instructions, causing the model to behave outside its intended scope.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/prompt-pitfalls.md`

### prompt pattern
A reusable structural template for a prompt that separates the invariant scaffolding — role, format, process — from the variable task content, enabling the pattern to be tested and versioned independently.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/prompt-patterns.md`

### role prompting
A prompting technique that assigns the model a specific professional identity with relevant expertise and behavioral constraints, anchoring the response vocabulary, tone, and assumed knowledge base.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/prompt-patterns.md`

### scratchpad
The space in a model's generated output where chain-of-thought reasoning is written, serving as external working memory that the model attends to when generating subsequent tokens.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/chain-of-thought.md`

### shot
A single labeled input/output example included in a prompt; the number of shots determines the technique name: zero-shot (no examples), one-shot (one example), few-shot (two to five), many-shot (ten or more).
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/few-shot.md`

### step-by-step instruction
A prompting pattern that decomposes a task into an explicit numbered sequence of steps the model must follow in order, prescribing the reasoning process rather than leaving it implicit.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/prompt-patterns.md`

### under-specification
A prompt design failure mode in which instructions are too vague or incomplete, allowing multiple valid interpretations and causing inconsistent output across runs.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/prompt-pitfalls.md`

### zero-shot prompting
A prompting approach that provides only an instruction with no examples, relying on the model's training to interpret and execute the task without demonstrated patterns.
- **Origin:** `prompt-engineering`
- **Doc:** `docs/prompt-engineering/prompt-anatomy.md`

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

### field-selection
The schema design practice of declaring only the fields an application will actually use, limiting the surface area where a model can hallucinate or default to plausible-but-incorrect values.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/schema-design.md`

### function-calling
The OpenAI/Anthropic term for the mechanism by which a model emits a structured function invocation — specifying function name and JSON-serialized arguments — instead of generating a text response; the application executes the function and returns the result.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/tool-usage.md`

### json-mode
An API-level constraint that forces a model to return syntactically valid JSON without imposing a specific schema; guarantees parseable output but does not constrain field names, nesting, or types.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/structured-outputs.md`

### json-schema
A vocabulary for describing the structure, types, and constraints of JSON data, used both for structured output enforcement (response format) and for declaring tool parameter shapes.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/schema-design.md`

### parallel-tools
A tool use pattern in which the model emits multiple independent tool calls in a single response turn; the application executes all calls (potentially concurrently), appends one result message per call, and resumes the model with the full result set.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/tool-patterns.md`

### pydantic-model
A Python class inheriting from `pydantic.BaseModel` that declares field types and constraints, generates JSON Schema via `model_json_schema()`, and validates deserialized data via `model_validate()` — used as the single source of truth for both API schema declarations and application-side validation.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/schema-design.md`

### response-format
An API request parameter that attaches a JSON Schema to the request, instructing the provider to enforce structural conformance before returning the response; stronger than JSON mode because it guarantees both valid JSON and schema compliance.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/structured-outputs.md`

### router-pattern
A tool use pattern in which multiple tools are declared and the model selects which tool applies based on the user query; the application does not pre-select the tool but relies on the model's reasoning to dispatch to the appropriate capability.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/tool-patterns.md`

### schema-constraints
Restrictions added to a JSON Schema declaration — such as `enum`, `minimum`, `maximum`, `maxLength`, and `additionalProperties: false` — that narrow the range of values a model can generate, reducing hallucination surface area.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/schema-design.md`

### sequential-chain
A tool use pattern in which the application hard-codes a pipeline of tool calls where the output of one step is the input to the next; the model is not involved in step ordering, trading model agency for application predictability.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/tool-patterns.md`

### single-tool
The baseline tool use pattern in which the model emits one tool call per turn; the application executes it, appends the result, and calls the model again until `finish_reason` is `"stop"`.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/tool-patterns.md`

### structured-output
A model response that conforms to a declared JSON Schema, enforced at the API level so that invalid responses are rejected or corrected before being returned to the caller.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/structured-outputs.md`

### tool-call
The structured object emitted by a model when it decides to invoke a tool, containing the tool name and JSON-serialized arguments that conform to the declared parameter schema.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/tool-usage.md`

### tool-declaration
The structured definition of a tool provided to the model at request time, consisting of a name, a description (which the model reads to decide relevance), and a JSON Schema describing the expected parameter shape.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/tool-usage.md`

### tool-patterns
Recurring compositions of tool calls — single tool, parallel tools, sequential chain, and router — each with a distinct message accumulation strategy and trade-off between model agency and application control.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/tool-patterns.md`

### tool-result
The application-generated message appended to the conversation history after a tool executes, containing the function's return value and the `tool_call_id` that links it to the originating tool call.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/tool-usage.md`

### tool-use
The mechanism by which a model, instead of generating a text response, generates a structured function call specifying which tool to invoke and what arguments to pass; the application executes the tool and returns the result for the model to incorporate into its response.
- **Origin:** `structured-outputs`
- **Doc:** `docs/structured-outputs/tool-usage.md`

### answer-faithfulness
A generation quality metric that measures whether every claim in a generated answer is supported by the retrieved context, with no fabricated or ungrounded statements; typically assessed by an LLM-as-judge grader given the context and the answer.
- **Origin:** `rag`
- **Doc:** `docs/rag/rag-evaluation-and-metrics.md`

### answer-relevance
A generation quality metric that measures whether the generated answer addresses the user's question, independent of whether the answer is grounded; a faithful but off-topic answer scores low on relevance.
- **Origin:** `rag`
- **Doc:** `docs/rag/rag-evaluation-and-metrics.md`

### bm25
A sparse retrieval algorithm that scores documents by a weighted, length-normalized sum of term-frequency and inverse-document-frequency values for each query term; excels at exact-term matching and does not require an embedding model.
- **Origin:** `rag`
- **Doc:** `docs/rag/retrieval-strategies.md`

### chunk-deduplication
The process of identifying and removing near-duplicate chunks from a retrieval candidate list before context assembly, typically by applying a cosine similarity threshold to prevent the same information from occupying multiple slots in the context block.
- **Origin:** `rag`
- **Doc:** `docs/rag/context-assembly.md`

### chunk-overlap
A chunking parameter that causes consecutive chunks to share a fixed number of tokens at their boundary, preventing facts that span a chunk boundary from being retrieved in incomplete form.
- **Origin:** `rag`
- **Doc:** `docs/rag/document-processing-and-chunking.md`

### chunk-size
The maximum number of tokens or characters in a single chunk; the primary parameter controlling the granularity of retrieval units, with smaller values increasing embedding precision and larger values preserving more surrounding context per retrieved unit.
- **Origin:** `rag`
- **Doc:** `docs/rag/document-processing-and-chunking.md`

### chunking
The process of splitting source documents into smaller, retrievable segments whose size and boundaries are tuned to maximize embedding focus and retrieval precision.
- **Origin:** `rag`
- **Doc:** `docs/rag/document-processing-and-chunking.md`

### context-assembly
The pipeline step that selects, deduplicates, orders, and formats retrieved chunks into a context block that fits within the model's token budget, ready to be injected into the generation prompt.
- **Origin:** `rag`
- **Doc:** `docs/rag/context-assembly.md`

### cosine-similarity
A distance metric between two vectors that measures the cosine of the angle between them, producing a value between -1 and 1; used to rank stored chunk vectors by semantic proximity to a query vector.
- **Origin:** `rag`
- **Doc:** `docs/rag/embeddings-and-vector-search.md`

### dense-retrieval
A retrieval approach that encodes the query and all corpus chunks as dense embedding vectors and finds the most semantically similar chunks using approximate nearest-neighbor search; captures semantic similarity and paraphrase but may miss rare exact-term matches.
- **Origin:** `rag`
- **Doc:** `docs/rag/retrieval-strategies.md`

### document-loader
The ingestion pipeline component that reads source documents from files, databases, or APIs and extracts clean plain text, handling format-specific concerns such as PDF multi-column layout, HTML boilerplate removal, and Markdown header preservation.
- **Origin:** `rag`
- **Doc:** `docs/rag/document-processing-and-chunking.md`

### embedding
A dense vector representation of a text segment produced by an embedding model, encoding semantic meaning as a point in high-dimensional space such that semantically similar texts are geometrically close.
- **Origin:** `rag`
- **Doc:** `docs/rag/embeddings-and-vector-search.md`

### embedding-model
A neural network trained to map text inputs to dense vectors, where geometric proximity in the output space corresponds to semantic similarity in meaning; must remain consistent between index build time and query time.
- **Origin:** `rag`
- **Doc:** `docs/rag/embeddings-and-vector-search.md`

### evaluation-dataset
A fixed set of (query, relevant_chunk_ids, expected_answer) triples used to measure RAG pipeline quality; must be static across pipeline comparisons to ensure metric scores are comparable.
- **Origin:** `rag`
- **Doc:** `docs/rag/rag-evaluation-and-metrics.md`

### hallucination
A model output that contains statements not supported by the provided context or training data, presented with unwarranted confidence; in RAG systems, reduced by grounding generation in retrieved content and instructing the model to answer only from the provided context.
- **Origin:** `rag`
- **Doc:** `docs/rag/rag-fundamentals.md`

### hybrid-retrieval
A retrieval strategy that runs both dense (embedding-based) and sparse (BM25) retrieval and merges the two ranked result lists, recovering candidates that each approach would miss individually.
- **Origin:** `rag`
- **Doc:** `docs/rag/retrieval-strategies.md`

### knowledge-grounding
The property of a generated response whereby every factual claim can be traced to a specific piece of retrieved source content, making the response auditable and its claims verifiable.
- **Origin:** `rag`
- **Doc:** `docs/rag/rag-fundamentals.md`

### lost-in-the-middle
An empirically observed LLM attention pattern in which the model assigns lower weight to content placed in the middle of a long context window compared to content at the beginning and end, causing relevant chunks placed in the middle to be under-utilized in generation.
- **Origin:** `rag`
- **Doc:** `docs/rag/context-assembly.md`

### non-parametric-memory
Knowledge provided to a model at inference time through the context window — such as retrieved documents — as opposed to knowledge encoded in model weights; available for the duration of a single call and updatable without retraining.
- **Origin:** `rag`
- **Doc:** `docs/rag/rag-fundamentals.md`

### parametric-memory
Knowledge encoded in a model's weights during training, always available at inference time but static — it does not change unless the model is retrained or fine-tuned.
- **Origin:** `rag`
- **Doc:** `docs/rag/rag-fundamentals.md`

### prompt-context-block
The formatted section of a RAG prompt that contains the numbered, assembled retrieved chunks, presented before the user query and wrapped in framing instructions that direct the model to reason from the provided content.
- **Origin:** `rag`
- **Doc:** `docs/rag/context-assembly.md`

### reciprocal-rank-fusion
A rank aggregation algorithm that merges multiple ranked lists by summing `1/(k + rank)` scores per document across lists, using only rank positions (not raw scores) and therefore robust to score scale differences between retrieval systems.
- **Origin:** `rag`
- **Doc:** `docs/rag/retrieval-strategies.md`

### recursive-chunking
A chunking strategy that applies a priority-ordered list of split delimiters — paragraph break, sentence boundary, word boundary — and splits on the coarsest delimiter that keeps chunks within the target size, producing chunks that respect natural text structure.
- **Origin:** `rag`
- **Doc:** `docs/rag/document-processing-and-chunking.md`

### reranking
A second-pass relevance scoring step that applies a cross-encoder model to the top-k retrieval candidates, attending jointly to the query and each chunk to produce more accurate relevance scores than cosine similarity alone.
- **Origin:** `rag`
- **Doc:** `docs/rag/retrieval-strategies.md`

### retrieval-augmented-generation
A pattern that augments a language model's generation by retrieving relevant documents from an external knowledge store at query time and injecting them as context in the prompt, enabling grounded responses from up-to-date or private information without retraining the model.
- **Origin:** `rag`
- **Doc:** `docs/rag/rag-fundamentals.md`

### retrieval-precision
A retrieval quality metric measuring what fraction of the top-k retrieved chunks are relevant to the query; high precision means few irrelevant chunks reach the context assembler.
- **Origin:** `rag`
- **Doc:** `docs/rag/rag-evaluation-and-metrics.md`

### retrieval-recall
A retrieval quality metric measuring what fraction of all relevant chunks in the index appear in the top-k retrieved results; low recall means the correct information is in the store but the retrieval step fails to surface it.
- **Origin:** `rag`
- **Doc:** `docs/rag/rag-evaluation-and-metrics.md`

### sparse-retrieval
A retrieval approach that builds an inverted index of term frequencies and ranks documents by BM25 score; excels at exact keyword matching and does not require an embedding model, but cannot capture synonyms or paraphrase.
- **Origin:** `rag`
- **Doc:** `docs/rag/retrieval-strategies.md`

### token-budget
The number of tokens available for retrieved context in a RAG prompt, calculated as the context window size minus the system prompt tokens, query tokens, and output reservation; determines how many chunks can be included before the context overflows.
- **Origin:** `rag`
- **Doc:** `docs/rag/context-assembly.md`

### vector-index
A data structure that stores embedding vectors and supports efficient approximate nearest-neighbor queries; common index types include HNSW (hierarchical navigable small world) for general use and IVF (inverted file index) for very large collections.
- **Origin:** `rag`
- **Doc:** `docs/rag/embeddings-and-vector-search.md`

### vector-search
A retrieval mechanism that finds the stored documents most semantically similar to a query by computing geometric distance between embedding vectors, returning the top-k closest vectors from the index.
- **Origin:** `rag`
- **Doc:** `docs/rag/embeddings-and-vector-search.md`

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
