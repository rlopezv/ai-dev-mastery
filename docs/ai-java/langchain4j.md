---
id: "ai-java-langchain4j"
title: "LangChain4j"
type: "topic"
step: "ai-java"
path: "docs/ai-java/langchain4j.md"
status: "draft"
level: "intermediate"

concepts:
  - "LangChain4j"
  - "AI service"
  - "LangChain4j memory"
  - "LangChain4j RAG"

prerequisites:
  - "docs/ai-java/java-ai-landscape.md"
  - "docs/frameworks-tools/langchain.md"

next:
  - "docs/ai-java/java-patterns.md"

related:
  - "docs/rag/README.md"
  - "docs/ai-agents/tool-use-loops.md"
  - "docs/memory-context/conversation-history.md"

implementation_refs: []

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Covers LangChain4j's core abstractions — AI services, chat memory, RAG pipeline, and tool integration — as a framework-portable Java implementation of the LangChain pattern."
---

## 1. Intuition

LangChain4j's central insight is that the most common AI interaction pattern in Java is
not a pipeline configuration problem — it is an interface definition problem. Instead of
building chains of objects, you declare a Java interface annotated with what you want:
a system prompt, conversation memory, retrieval augmentation, available tools. LangChain4j
generates an implementation at startup.

This approach — called the AI service pattern — produces AI-powered beans that look like
any other Spring or CDI service to the rest of the application. Callers invoke typed Java
methods; LangChain4j handles model calls, memory management, and tool dispatch internally.

---

## 2. Explanation

### 2.1 Why

LangChain's Python model builds chains by composing `Runnable` objects. This works well
in Python's dynamic type system, where duck typing and lambda functions make ad-hoc
composition natural. In Java, the same pattern would require verbose chain construction
code for every use case.

LangChain4j chose a different approach: use Java's interface and annotation system to
declare AI service contracts, then generate implementations. The result is AI code that
reads like a service layer declaration rather than a framework configuration exercise.
This pattern integrates seamlessly with Spring Boot (`@AiService` stereotype), Quarkus
(CDI injection), and plain Java (programmatic builder).

### 2.2 How

LangChain4j is organized around five primary abstractions:

**ChatLanguageModel.** The provider-agnostic model client. Built via a fluent builder
(`OpenAiChatModel.builder()`, `OllamaChatModel.builder()`, etc.), it takes messages and
returns `AiMessage`. This is the lowest-level abstraction — used directly only when the
AI service pattern is insufficient.

**AI service.** The central LangChain4j abstraction. You declare a Java interface,
annotate it with `@SystemMessage` for the system prompt and `@UserMessage` (or method
parameters) for the user turn. LangChain4j's `AiServices.builder()` generates a proxy
implementation that routes calls to the underlying model, handles conversation memory,
invokes tools, and manages RAG retrieval. This maps to LangChain's `create_tool_calling_agent`
+ `AgentExecutor` pattern, but expressed as a typed Java interface.

**ChatMemory.** Conversation history management. `MessageWindowChatMemory` keeps the last
N messages; `TokenWindowChatMemory` keeps messages within a token budget. Memory is
attached to the AI service during construction. For multi-user applications, a
`ChatMemoryProvider` supplies a per-conversation-id memory instance, equivalent to
LangChain's `RunnableWithMessageHistory` with a `session_id` key.

**Content retriever and RAG.** LangChain4j's RAG pipeline mirrors LlamaIndex's structure:
`EmbeddingStore` (Chroma, pgvector, in-memory) stores vectors; `EmbeddingModel` generates
them; `ContentRetriever` wraps both into a search interface that the AI service queries
automatically on each call. The `EmbeddingStoreIngestor` handles the ingestion pipeline:
document loading, splitting (via `DocumentSplitter`), embedding, and storage.

**Tools.** Java methods annotated with `@Tool` become available to the model as function
calls. LangChain4j serializes the method signature and Javadoc description as the tool
schema, dispatches calls to the method implementation, and appends results to the message
history. Multiple tool classes can be registered per AI service.

**Framework integration.** LangChain4j's AI service works in any Java context, but the
wiring mechanism changes depending on the application framework:

- **Spring Boot:** Use the `langchain4j-spring-boot-starter`. LangChain4j registers a
  `ChatLanguageModel` bean auto-configured from `langchain4j.*` properties. The AI
  service can be declared as a `@Bean` in a `@Configuration` class and injected normally.
- **Quarkus:** Use the `quarkus-langchain4j` extension. It provides CDI-native AI service
  injection: annotate the interface with `@RegisterAiService` and inject with `@Inject`.
  Quarkus Dev Services can spin up a local Ollama instance automatically for development.
- **Micronaut:** No dedicated LangChain4j extension exists; construct the AI service
  programmatically in a `@Singleton` factory method. Micronaut's `@Factory` pattern
  works cleanly with LangChain4j's builder API.
- **Standalone / Dropwizard / Jakarta EE:** Construct models and AI services in
  application startup code and store them as application-scoped state. No DI framework
  is required; LangChain4j has no Spring or Quarkus runtime dependency.

### 2.3 Code example

```java
// AI service pattern — see docs/ai-java/java-patterns.md for broader idiom catalog

// --- Spring Boot / standalone: programmatic builder ---

// 1. Declare the interface (same regardless of application framework)
interface SupportAssistant {

    @SystemMessage("You are a customer support agent. Answer only using the provided context.")
    String chat(@MemoryId String conversationId, @UserMessage String userMessage);
}

// 2. Build the AI service with memory, RAG, and tools
SupportAssistant assistant = AiServices.builder(SupportAssistant.class)
    .chatLanguageModel(OpenAiChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName(GPT_4_O_MINI)
        .build())
    .chatMemoryProvider(conversationId -> MessageWindowChatMemory.withMaxMessages(20))
    .contentRetriever(EmbeddingStoreContentRetriever.from(embeddingStore))
    .tools(new OrderTools(), new ProductTools())
    .build();

// 3. Call it — looks like any other Java service method
String response = assistant.chat("session-42", "What is the status of order 1001?");

// --- Quarkus: declarative injection via quarkus-langchain4j extension ---
// The interface declaration is identical; wiring is handled by the extension.

@RegisterAiService(tools = OrderTools.class)
@ApplicationScoped
interface QuarkusSupportAssistant {

    @SystemMessage("You are a customer support agent. Answer only using the provided context.")
    String chat(@MemoryId String conversationId, @UserMessage String userMessage);
}

// Injection in a Quarkus resource — no builder code required
@Inject QuarkusSupportAssistant assistant;
// application.properties: quarkus.langchain4j.openai.api-key=...

// Ingestion pipeline for RAG
EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
    .documentSplitter(DocumentSplitters.recursive(500, 50))
    .embeddingModel(embeddingModel)
    .embeddingStore(embeddingStore)
    .build();
ingestor.ingest(FileSystemDocumentLoader.loadDocuments(Path.of("docs/")));
```

---

## 3. Table

| LangChain4j Component | Purpose | Python equivalent |
|----------------------|---------|-------------------|
| `ChatLanguageModel` | Provider-agnostic model client | LangChain `ChatOpenAI` / `ChatOllama` |
| `AiServices` | AI service proxy factory | LangChain `create_tool_calling_agent` + `AgentExecutor` |
| `@SystemMessage` | Declares system prompt on interface method | LangChain `ChatPromptTemplate` system message |
| `@UserMessage` | Maps method parameter to user turn | LangChain `HumanMessage` |
| `@MemoryId` | Routes conversation to per-id memory | LangChain `RunnableWithMessageHistory` session_id |
| `MessageWindowChatMemory` | Last-N-messages conversation history | LangChain `ConversationBufferWindowMemory` |
| `TokenWindowChatMemory` | Token-budget conversation history | LangChain token buffer memory |
| `EmbeddingStore` | Vector store abstraction | LlamaIndex `VectorStoreIndex` |
| `ContentRetriever` | Search interface over embedding store | LlamaIndex `VectorIndexRetriever` |
| `EmbeddingStoreIngestor` | Document ingestion pipeline | LlamaIndex `VectorStoreIndex.from_documents()` |
| `@Tool` | Method-level tool declaration | LangChain `@tool` decorator |

| AI service builder method | Effect |
|--------------------------|--------|
| `.chatLanguageModel(model)` | Sets the underlying model client |
| `.chatMemoryProvider(fn)` | Per-conversation-id memory supplier |
| `.contentRetriever(retriever)` | Attaches RAG to every call |
| `.tools(instances...)` | Registers tool-annotated beans |
| `.systemMessageProvider(fn)` | Dynamic system prompt per user/session |

| Application framework | LangChain4j integration | Key artifact |
|-----------------------|------------------------|--------------|
| Spring Boot | `langchain4j-spring-boot-starter` + `@Bean` factory | `langchain4j-open-ai-spring-boot-starter` |
| Quarkus | `quarkus-langchain4j` extension + `@RegisterAiService` + `@Inject` | `io.quarkiverse.langchain4j:quarkus-langchain4j-openai` |
| Micronaut | `@Factory` + `@Singleton` builder method | `langchain4j-open-ai` (no dedicated extension) |
| Dropwizard / Jakarta EE | Application startup builder + manual lifecycle | `langchain4j-open-ai` |
| Standalone Java | Programmatic builder, no DI | `langchain4j-open-ai` |

---

## 4. Engineering Implications

**Interface-as-contract.** The AI service interface is the boundary between AI behavior
and the rest of the application. Changing a `@SystemMessage` or adding a tool changes the
model's behavior without touching callers. This is the Java idiom for the "prompt as
configuration" principle: the interface declaration is the configuration artifact.

**Memory scope and lifecycle.** When using `ChatMemoryProvider`, LangChain4j creates a
memory instance per conversation ID and holds it in the provider's map. Default
implementations use JVM heap. For multi-instance deployments, implement a custom
`ChatMemory` backed by Redis or a database. The memory ID maps directly to a user or
session identifier — never use the same ID across security boundaries.

**Tool method visibility and serialization.** LangChain4j uses reflection to build tool
schemas from `@Tool` method signatures. Method parameters must be Jackson-serializable;
Javadoc on the `@Tool` annotation becomes the tool description sent to the model —
write it as if writing an API description, not code commentary. Ambiguous descriptions
cause the model to call the wrong tool or fail to invoke tools when appropriate.

**Streaming in LangChain4j.** Streaming uses `StreamingChatLanguageModel` instead of
`ChatLanguageModel`. The AI service interface method returns `TokenStream` instead of
`String`. `TokenStream.onNext(consumer).onComplete(handler).start()` registers callbacks.
This is a different programming model from Project Reactor's `Flux`; mixing LangChain4j
streaming with reactive Spring WebFlux requires an adapter.

**Framework portability.** LangChain4j works without Spring. In a plain Java application
or with Quarkus, construct models and AI services programmatically using builders. The
`langchain4j-spring-boot-starter` provides auto-configuration, but it is optional. This
makes LangChain4j the right choice when Spring Boot is not the application framework.

---

## 5. Implementation Connection

This is a concept-only topic. No executable lab is provided for this module.

The AI service pattern has no direct Python equivalent — it is a Java-specific abstraction.
The closest Python analog is a class wrapping a LangChain `AgentExecutor` with message
history. For the Python implementation reference, see:

- `labs/frameworks-tools/lab-langchain/main.py` — agent with memory and tools
- `labs/frameworks-tools/lab-integration/main.py` — RAG pipeline with memory

To apply LangChain4j in a project, add the dependency for your model provider:

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot-starter</artifactId>
    <version>0.36.0</version>
</dependency>
```

---

## 6. Failure Modes and Limitations

**RAG on every call regardless of query type.** The `contentRetriever` attached to an AI
service runs on every method call, including calls where retrieval is unnecessary (simple
factual questions, conversational turns). This adds latency and token cost. Advanced
configurations use a `ReRankingContentRetriever` or a custom router that invokes retrieval
conditionally. For simpler cases, a second AI service method without the retriever annotation
handles non-RAG queries.

**Tool call loops.** If a tool method returns a value the model cannot use to generate a
final answer, the model may call the tool repeatedly. LangChain4j does not enforce a
maximum tool call depth by default. Set a maximum iterations limit on the
`ChatLanguageModel` or implement a guard in the tool method itself.

**Javadoc-driven tool schema brittleness.** The `@Tool` description becomes part of the
model's tool schema. If the description is inconsistent with parameter names, or if
parameter types are not self-documenting, the model will generate incorrect tool call
arguments. Test tool invocation in isolation with a known prompt before integrating into
a full AI service.

**Spring Boot auto-configuration conflicts.** When both `langchain4j-spring-boot-starter`
and `spring-ai-openai-spring-boot-starter` are on the classpath, both auto-configurations
activate. Property key namespaces differ (`langchain4j.*` vs `spring.ai.*`), but having
two LLM client beans may cause `NoUniqueBeanDefinitionException` if callers autowire by
type. Use `@Qualifier` or explicit bean construction in this scenario.

---

## 7. Summary

LangChain4j implements the AI service pattern: you declare a typed Java interface
annotated with prompts, memory, and tool bindings, and LangChain4j generates a proxy that
routes calls to the model. This approach maps the LangChain agent model to Java's
interface-driven design style, producing AI services that integrate naturally into Spring
Boot or any Java environment. The framework's key trade-off is interface-level simplicity
at the cost of reduced pipeline visibility compared to explicit LCEL-style chain construction.
