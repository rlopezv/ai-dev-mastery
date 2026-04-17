---
id: "ai-java-implementation-reference"
title: "AI Development in Java — Implementation Reference"
type: "implementation-reference"
step: "ai-java"
path: "docs/ai-java/implementation-reference.md"
status: "draft"
level: "intermediate"

concepts:
  - "Spring AI"
  - "LangChain4j"
  - "AI service"
  - "advisor"
  - "Java AI pattern"

prerequisites:
  - "docs/ai-java/architecture.md"

next:
  - "docs/ai-java/validation.md"

related:
  - "docs/ai-java/spring-ai.md"
  - "docs/ai-java/langchain4j.md"
  - "docs/ai-java/java-patterns.md"

implementation_refs: []

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Documents the implementation patterns for Java AI applications: how architecture components map to code constructs, why each pattern is the correct abstraction, and the design decisions behind the Java AI idioms."
---

## 1. Implementation Overview

This document covers the design reasoning behind Java AI implementation patterns. It does
not provide setup instructions — those belong in a project's own documentation.

> **Note:** This document contains orientative code — structures, interfaces, signatures.
> No executable labs exist for this module. For runnable reference implementations, see
> the Python equivalents in `labs/frameworks-tools/`.

The two frameworks map to distinct implementation styles:

- **Spring AI** patterns are Spring Boot configuration patterns applied to LLM integration.
  The implementation decisions mirror those for Spring Data or Spring Web: bean scope,
  advisor ordering, configuration externalization, and test substitution.
- **LangChain4j** patterns center on the AI service interface. The implementation decisions
  are about interface design: what to declare at the interface level, what to configure
  at the builder level, and where to apply per-session scoping.

---

## 2. Core Patterns

| Pattern | Description | When to use |
|---------|-------------|-------------|
| `ChatClient` fluent call | Compose request via method chain, execute via `.call()` or `.stream()` | Spring Boot applications; inline prompt composition |
| AI service interface | Declare AI behavior as annotated Java interface; LangChain4j generates impl | When AI logic is called from multiple layers or needs testability |
| Advisor chain | Register interceptors on `ChatClient.Builder` for memory, RAG, logging | Spring AI; when pipeline stages need explicit ordering |
| `ChatMemoryProvider` | Supplies per-session memory via a function keyed by conversation ID | Multi-user conversational applications |
| Typed structured output | Declare AI service method return type or use `.entity(Class)` | Downstream processing, schema enforcement |
| Spring profile routing | Different `ChatModel` or `ChatLanguageModel` bean per profile | Per-environment model selection without code change |
| `@Tool` method declaration | Annotate Java method to expose as model-callable function | Tool calling in both frameworks |
| Token usage tracking | Extract from `ChatResponseMetadata`; publish as Micrometer counter | Cost attribution, budget enforcement |

---

## 3. Component Mapping

### Spring AI

| Architecture component | Implementation |
|----------------------|----------------|
| Model client | Auto-configured `ChatModel` bean (provider-specific auto-config) |
| Call entry point | `ChatClient` (prototype-scoped; built from `ChatClient.Builder`) |
| Memory | `MessageChatMemoryAdvisor` wrapping `InMemoryChatMemory` or `RedisChatMemory` |
| RAG | `QuestionAnswerAdvisor` wrapping `VectorStore` |
| Tool calling | `@Tool`-annotated method; registered via `.defaultTools(bean)` on builder |
| Streaming | `chatClient.prompt().stream().content()` returning `Flux<String>` |
| Structured output | `.call().entity(MyRecord.class)` |
| Token tracking | `response.getMetadata().getUsage()` → Micrometer counter |

### LangChain4j

| Architecture component | Implementation |
|----------------------|----------------|
| Model client | `OpenAiChatModel.builder().build()` or provider-equivalent builder |
| AI service | `AiServices.builder(Interface.class).build()` generated proxy |
| Memory | `ChatMemoryProvider` lambda returning `MessageWindowChatMemory` per session ID |
| RAG | `ContentRetriever` (typically `EmbeddingStoreContentRetriever`) on AI service builder |
| Tool calling | `@Tool`-annotated bean methods; `.tools(instance)` on AI service builder |
| Streaming | `StreamingChatLanguageModel` + `TokenStream` callbacks |
| Structured output | Interface method return type (Java record) |
| Memory scoping | `@MemoryId` annotation on interface method parameter |

---

## 4. Data Structures and Interfaces

### Spring AI — ChatClient call structure

```java
// Orientative — no lab in this module; see labs/frameworks-tools/ for Python equivalents

// Minimal call
String response = chatClient
    .prompt()
    .system("You are a helpful assistant.")
    .user(userMessage)
    .call()
    .content();

// Full pipeline call with advisors and typed output
ChatResponse response = chatClient
    .prompt()
    .user(userMessage)
    .advisors(a -> a.param(CHAT_MEMORY_CONVERSATION_ID_KEY, sessionId))
    .call()
    .chatResponse();

// Streaming
Flux<String> stream = chatClient
    .prompt()
    .user(userMessage)
    .stream()
    .content();
```

### LangChain4j — AI service interface patterns

```java
// Orientative

// Minimal interface
interface SimpleAssistant {
    String chat(String userMessage);
}

// Full interface: system prompt, memory ID, RAG, typed output
interface EnterpriseAssistant {

    @SystemMessage("""
        You are an enterprise assistant. Answer using provided context only.
        If the answer is not in the context, say "I don't know."
        """)
    String chat(@MemoryId String sessionId, @UserMessage String userMessage);

    @SystemMessage("Classify the intent. Respond in JSON.")
    IntentResult classify(@UserMessage String text);
}

// Builder: wires all components
EnterpriseAssistant assistant = AiServices.builder(EnterpriseAssistant.class)
    .chatLanguageModel(model)
    .chatMemoryProvider(id -> MessageWindowChatMemory.withMaxMessages(20))
    .contentRetriever(EmbeddingStoreContentRetriever.from(embeddingStore))
    .tools(new OrderTools(), new ProductTools())
    .build();

record IntentResult(String intent, double confidence) {}
```

### Ingestion pipeline (LangChain4j)

```java
// Orientative

EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
    .documentSplitter(DocumentSplitters.recursive(500, 50))  // chunk size, overlap
    .embeddingModel(embeddingModel)
    .embeddingStore(embeddingStore)
    .build();

List<Document> docs = FileSystemDocumentLoader.loadDocuments(Path.of("corpus/"));
ingestor.ingest(docs);
```

---

## 5. Design Decisions

**Why the advisor chain pattern (Spring AI)?**
The advisor chain separates concerns without coupling them. Memory, RAG, logging, and
custom guardrails are independent — each advisor is unaware of the others. Adding or
removing a stage does not require modifying other stages. This mirrors the Servlet filter
chain pattern that Spring engineers already understand.

**Why the interface-as-contract pattern (LangChain4j)?**
Interfaces in Java already define contracts with testable substitutions. Making the AI
service a Java interface means callers can be tested without live model calls (replace
with a mock implementation). The framework's annotation processing at startup time catches
missing `@SystemMessage` or mismatched parameter types before runtime.

**Why `ChatMemoryProvider` instead of a single memory instance?**
A single `InMemoryChatMemory` instance would share history across all users. `ChatMemoryProvider`
is a function `conversationId → ChatMemory`, which creates isolated memory per session.
The same principle applies to Spring AI's `MessageChatMemoryAdvisor` with the
`CHAT_MEMORY_CONVERSATION_ID_KEY` parameter.

**Why profile-based model routing instead of conditional code?**
Conditional code for model selection (`if (env.isProduction()) { ... }`) mixes environment
logic into business logic. Spring profiles externalize this decision. The application code
is identical across environments; the active profile determines the model bean injected.

**Why extract token usage from `ChatResponseMetadata`?**
Third-party cost tracking services (LangSmith, Helicone) require external API calls and
data egress. Extracting usage from `ChatResponseMetadata` keeps cost data inside the
application's own Micrometer metrics, which are already collected by Prometheus/Datadog.
This avoids adding an external dependency to the observability chain.

---

## 6. External Dependencies

| Tool | Role | Notes |
|------|------|-------|
| OpenAI API | Primary model provider in examples | Any Spring AI / LangChain4j supported provider works |
| Ollama | Local model provider for development | Enables offline development without API keys |
| pgvector (PostgreSQL) | Vector store for production | Reuses existing PostgreSQL infrastructure |
| Redis | Persistent chat memory | Required for multi-instance conversation continuity |
| Chroma | Alternative vector store | Simpler setup than pgvector for non-PostgreSQL environments |

---

## 7. Mapping to Labs

This module has no executable labs. Conceptually equivalent Python lab references:

| Pattern / Component | Python lab reference | Concept verified |
|---------------------|---------------------|-----------------|
| Advisor chain (memory + RAG) | `labs/frameworks-tools/lab-integration/main.py` | Integrated memory and retrieval pipeline |
| Tool calling | `labs/frameworks-tools/lab-langchain/main.py` demo_agent | Agent loop with tool dispatch |
| RAG ingestion | `labs/frameworks-tools/lab-llamaindex/main.py` build_index | Chunking, embedding, vector store ingestion |
| Conversation history | `labs/frameworks-tools/lab-langchain/main.py` demo_memory | Per-session message accumulation |

---

## 8. Trade-offs and Constraints

**Spring AI vs LangChain4j selection.** Spring AI minimizes boilerplate in Spring Boot
applications but adds a framework dependency and requires Spring Boot 3.x. LangChain4j
requires explicit builder construction but works in any Java environment. The decision
criterion is the application framework context, not feature completeness — both frameworks
implement the same capabilities.

**Interface annotation vs builder configuration.** LangChain4j's annotation-driven approach
compiles AI configuration into the JAR. Spring AI's builder approach keeps configuration
at runtime (advisors can be switched). If AI behavior must change without redeployment,
Spring AI's externalized advisor and prompt template approach is more flexible.

**In-memory vs persistent memory.** `InMemoryChatMemory` and `InMemoryChatMemory` are
appropriate for development and single-instance, short-lived conversations. Horizontal
scaling or long-lived conversations require persistent memory. The memory abstraction
in both frameworks supports this substitution without changing the application code.

---

## 9. Failure Modes

**Advisor ordering bug.** Registering `QuestionAnswerAdvisor` before
`MessageChatMemoryAdvisor` means the model receives retrieved context before conversation
history in the prompt. This changes the model's weighting of information sources and may
degrade response quality for follow-up questions that reference prior turns. Always
register memory before RAG in the advisor chain.

**AI service method parameter mismatch.** LangChain4j maps method parameters to prompt
placeholders by parameter name (or annotation). If a method parameter is not annotated
with `@UserMessage` or `@MemoryId` and does not match a `{placeholder}` in the system
message template, LangChain4j either ignores it or throws at build time. Verify all
parameters are explicitly bound during AI service construction.

**Structured output model support gap.** `.entity(Class)` and typed AI service return
types rely on the model's structured output / JSON mode support. Older or smaller models
(including some Ollama-hosted models) produce invalid JSON intermittently. Add fallback
parsing logic or validation for structured output in production, especially with non-GPT-4
class models.

---

## 10. Summary

Spring AI and LangChain4j implement the same logical pipeline — history retrieval, RAG,
prompt assembly, model call, tool dispatch, history persistence — through different
structural patterns. Spring AI uses an advisor chain attached to a `ChatClient`; LangChain4j
uses an interface-driven proxy generated from annotated declarations. Both apply standard
Java idioms: Spring configuration, dependency injection, interface contracts, Micrometer
metrics. The design decisions prioritize testability (interface mocking), environment
portability (profile-based model routing), and operational visibility (usage tracking).
