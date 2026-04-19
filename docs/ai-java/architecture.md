---
id: "ai-java-architecture"
title: "AI Development in Java — Architecture"
type: "architecture"
step: "ai-java"
path: "docs/ai-java/architecture.md"
status: "draft"
level: "intermediate"

concepts:
  - "Java AI ecosystem"
  - "Spring AI"
  - "LangChain4j"
  - "AI service"
  - "advisor"

prerequisites:
  - "docs/ai-java/java-patterns.md"

next:
  - "docs/ai-java/implementation-reference.md"

related:
  - "docs/frameworks-tools/architecture.md"
  - "docs/rag/architecture.md"
  - "docs/memory-context/architecture.md"

implementation_refs: []

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes how Java AI components compose into a system: Spring AI's advisor pipeline and LangChain4j's AI service proxy, the data flow through each, and the points where they connect to provider APIs and infrastructure."
---

# AI Development in Java — Architecture

## Navigation

[Docs](../README.md) / [AI Development in Java](README.md) / AI Development in Java — Architecture

---

## 1. System Overview

A Java AI application built with Spring AI or LangChain4j is a standard Spring Boot
(or Java) application with LLM integration layered on top of existing infrastructure.
The AI components follow the same wiring model as database access or HTTP clients:
they are beans or builder-constructed objects, injected into service classes, and
configured from external properties.

The two frameworks implement different architectures for the same capabilities:

- **Spring AI** uses an **advisor pipeline** — a chain of interceptors around the
  `ChatClient.call()` execution point. Memory, RAG, and logging are advisors that
  modify the request before the model call and process the response after.
- **LangChain4j** uses an **AI service proxy** — a generated implementation of a
  developer-declared interface. The proxy handles memory, retrieval, and tool dispatch
  internally, surfacing only the typed method to the caller.

---

## 2. Core Components

| Component | Framework | Role |
|-----------|-----------|------|
| `ChatClient` | Spring AI | Fluent entry point for model calls; executes advisor chain |
| `ChatModel` | Spring AI | Configured bean for a specific model provider |
| `Advisor` | Spring AI | Interceptor in the call pipeline (memory, RAG, logging) |
| `VectorStore` | Spring AI | Abstraction over embedding search infrastructure |
| `ChatLanguageModel` | LangChain4j | Provider client constructed via builder |
| `AiServices` proxy | LangChain4j | Generated implementation of the AI service interface |
| `ChatMemory` | LangChain4j | Conversation history store (window or token-bounded) |
| `EmbeddingStore` | LangChain4j | Vector search abstraction for RAG |
| `ContentRetriever` | LangChain4j | Query-to-document pipeline attached to the AI service |
| `@Tool` method | Both | Java method exposed to the model as a callable function |

---

## 3. Component Interactions

### Spring AI — advisor pipeline

```text
Controller / Service
        │
        ▼
  ChatClient.prompt()
        │
        ▼
  ┌─────────────────────────────────────────────┐
  │               Advisor Chain                  │
  │  ┌────────────────────────────────────┐      │
  │  │  1. MessageChatMemoryAdvisor        │      │
  │  │     Prepend N prior messages       │      │
  │  └──────────────────┬─────────────────┘      │
  │                     ▼                         │
  │  ┌────────────────────────────────────┐      │
  │  │  2. QuestionAnswerAdvisor           │      │
  │  │     Embed query → VectorStore      │      │
  │  │     Inject top-k docs into context │      │
  │  └──────────────────┬─────────────────┘      │
  │                     ▼                         │
  │  ┌────────────────────────────────────┐      │
  │  │  3. (Custom Advisor)               │      │
  │  │     Audit / guardrail / routing    │      │
  │  └──────────────────┬─────────────────┘      │
  └─────────────────────┼─────────────────────────┘
                        ▼
              ChatModel.call(prompt)
                        │
                        ▼
               Provider API (OpenAI / Anthropic / Ollama)
                        │
                        ▼
                 ChatResponse
```

### LangChain4j — AI service proxy

```text
Controller / Service
        │
        ▼
  AI Service Interface method call
        │
        ▼
  ┌─────────────────────────────────────────────┐
  │         AiServices Proxy (generated)          │
  │                                               │
  │  1. Retrieve conversation from ChatMemory    │
  │  2. Run ContentRetriever (RAG)               │
  │  3. Build prompt from @SystemMessage +       │
  │     conversation + retrieved docs + user msg │
  │  4. Call ChatLanguageModel                   │
  │  5. If tool call: dispatch → @Tool method    │
  │     → re-submit with tool result             │
  │  6. Save assistant turn to ChatMemory        │
  │  7. Return typed response                    │
  │                                               │
  └──────────────────────────────────────────────┘
        │
        ▼
  Provider API (OpenAI / Anthropic / Ollama)
```

---

## 4. Data Flow

### Spring AI: request through the advisor pipeline

```text
User message string
  → ChatClient.prompt().user(message)
  → [Advisor 1] MessageChatMemoryAdvisor
      reads: ChatMemory[conversationId] → prior messages
      writes: prepends messages to ChatRequest
  → [Advisor 2] QuestionAnswerAdvisor
      reads: user message text
      embeds: EmbeddingModel.embed(query)
      searches: VectorStore.similaritySearch(queryEmbedding, topK)
      writes: appends retrieved documents as context in ChatRequest
  → ChatModel.call(ChatRequest)
      → HTTP POST → Provider API
      ← ChatResponse
  → [Advisor 2 post-process] QuestionAnswerAdvisor
      extracts source metadata from response
  → [Advisor 1 post-process] MessageChatMemoryAdvisor
      saves user + assistant messages to ChatMemory
  → ChatResponse.getResult().getOutput().getContent()
  → String returned to caller
```

### LangChain4j: request through AI service proxy

```text
assistant.chat(sessionId, userMessage)
  → proxy: load ChatMemory[sessionId] → prior messages
  → proxy: ContentRetriever.retrieve(userMessage)
      embeds query via EmbeddingModel
      searches EmbeddingStore → List<TextSegment>
  → proxy: build UserMessage with retrieved segments injected
  → proxy: prepend SystemMessage (@SystemMessage annotation)
  → proxy: prepend conversation history
  → ChatLanguageModel.generate(messages)
      → HTTP POST → Provider API
      ← AiMessage
  → if AiMessage.hasToolExecutionRequests():
      for each request: invoke @Tool method → ToolExecutionResult
      → ChatLanguageModel.generate(messages + toolResults)
      ← AiMessage (text response)
  → proxy: save messages to ChatMemory[sessionId]
  → deserialize response to declared return type
  → return to caller
```

---

## 5. Execution Flow

Both frameworks follow the same logical execution sequence — they differ in where the
logic lives and how it is expressed:

```text
1. Input arrives         → method call or ChatClient.prompt()
2. History retrieval     → ChatMemory / MessageChatMemoryAdvisor reads prior turns
3. RAG retrieval         → ContentRetriever / QuestionAnswerAdvisor embeds + searches
4. Prompt assembly       → system message + history + docs + user message
5. Model call            → HTTP POST to provider API
6. Tool dispatch         → if tool call: invoke @Tool method, resubmit
7. Response processing   → deserialize to type or extract content string
8. History persistence   → save turn to ChatMemory / MessageChatMemoryAdvisor
9. Return to caller      → typed response or String
```

---

## 6. Integration Points

| Integration | Spring AI | LangChain4j |
|-------------|-----------|-------------|
| OpenAI | `spring-ai-openai-spring-boot-starter` | `langchain4j-open-ai` |
| Anthropic | `spring-ai-anthropic-spring-boot-starter` | `langchain4j-anthropic` |
| Ollama (local) | `spring-ai-ollama-spring-boot-starter` | `langchain4j-ollama` |
| pgvector | `spring-ai-pgvector-store-spring-boot-starter` | `langchain4j-pgvector` |
| Redis | `spring-ai-redis-store-spring-boot-starter` | Custom `ChatMemory` impl |
| Chroma | `spring-ai-chroma-store-spring-boot-starter` | `langchain4j-chroma` |
| Micrometer | Built-in `ChatResponseMetadata.getUsage()` | Manual counter registration |
| Spring Security | Standard filter chain wraps AI endpoints | Standard — LangChain4j is provider-agnostic |

---

## 7. Trade-offs and Design Decisions

**Advisor chain vs AI service proxy.** Spring AI's advisor chain is explicit — you register
advisors in a builder and their execution order is visible. LangChain4j's AI service proxy
is implicit — the proxy handles everything declared via annotations. The advisor chain
gives more control over pipeline composition; the AI service proxy gives less boilerplate
for standard patterns.

**Framework lock-in surface.** Spring AI ties the application to the Spring ecosystem.
LangChain4j is framework-portable. If your organization may adopt Quarkus or Micronaut
alongside Spring Boot, LangChain4j has a lower migration cost. If Spring Boot is the
permanent platform, Spring AI's auto-configuration saves significant wiring code.

**Structured output typing.** LangChain4j's interface return type approach enforces the
schema at the interface declaration. Spring AI's `.entity(Class)` call enforces it at the
call site. Both generate JSON mode constraints for the model, but the type safety guarantee
applies at different points in the code.

---

## 8. Mapping to Labs

This module has no executable labs. The equivalent Python implementations are:

| Architecture component | Python lab reference |
|----------------------|---------------------|
| Advisor pipeline (memory + RAG) | `labs/frameworks-tools/lab-integration/main.py` |
| Tool dispatch loop | `labs/frameworks-tools/lab-langchain/main.py` demo_agent |
| RAG ingestion pipeline | `labs/frameworks-tools/lab-llamaindex/main.py` |
| Conversation memory | `labs/frameworks-tools/lab-langchain/main.py` demo_memory |

---

## 9. Limitations and Boundaries

This architecture document covers LLM integration within a Java application. It does not cover:

- **Inference infrastructure.** Running models locally (Ollama) or on cloud providers is
  infrastructure configuration, not application architecture.
- **Vector store schema design.** Database schema, index configuration, and scaling of
  the vector store are covered in `rag` and `deployment-scaling`.
- **Multi-service architectures.** Distributing AI components across microservices,
  message queues, or event-driven pipelines is covered in `deployment-scaling`.
- **Evaluation pipelines.** Testing and evaluating Java AI application output is covered
  in `evaluation-testing`.

---

## 10. Summary

Java AI applications route through either Spring AI's advisor pipeline or LangChain4j's
AI service proxy. Both implement the same logical sequence: retrieve history, retrieve
context (RAG), assemble prompt, call model, dispatch tools if needed, persist history,
return response. Spring AI expresses this as an explicit advisor chain around a
`ChatClient`; LangChain4j expresses it as a generated proxy implementation of a
developer-declared interface. The integration points — provider APIs, vector stores,
memory stores — are shared across both frameworks.
