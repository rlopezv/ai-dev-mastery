---
id: "ai-java-spring-ai"
title: "Spring AI"
type: "topic"
step: "ai-java"
path: "docs/ai-java/spring-ai.md"
status: "draft"
level: "intermediate"

concepts:
  - "Spring AI"
  - "ChatClient"
  - "advisor"
  - "Spring AI RAG"

prerequisites:
  - "docs/ai-java/java-ai-landscape.md"
  - "docs/frameworks-tools/langchain.md"

next:
  - "docs/ai-java/langchain4j.md"

related:
  - "docs/rag/README.md"
  - "docs/memory-context/conversation-history.md"
  - "docs/frameworks-tools/semantic-kernel.md"

implementation_refs: []

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Covers Spring AI's core abstractions — ChatClient, prompt templates, advisors, RAG components, and tool calling — as a Spring Boot-native integration layer for LLM APIs."
---

## 1. Intuition

Spring AI's design goal is to feel like Spring Data or Spring Web: you declare what you
need, and Spring Boot's auto-configuration wires it up from `application.properties`.
A developer who knows Spring Boot already understands how Spring AI works at the
configuration level — they are adding beans to the application context, not learning a
new runtime model.

The central abstraction is the `ChatClient` — a fluent API over the underlying model
provider that mirrors how `RestClient` or `WebClient` works for HTTP. You compose a
request using method chaining, execute it, and process a typed response.

---

## 2. Explanation

### 2.1 Why

Enterprise Spring Boot teams need LLM capabilities embedded inside existing application
contexts — not as sidecar services or separate Python runtimes. Business requirements
include reusing Spring Security for API authentication, Spring Data for persistence,
Spring Boot Actuator for health checks, and existing observability infrastructure
(Micrometer, OpenTelemetry) for LLM call tracing.

Spring AI satisfies these requirements by treating the LLM as a Spring-managed resource.
The `ChatModel` bean is auto-configured from properties, injected via `@Autowired` or
constructor injection, and scoped like any other bean. This makes AI capabilities
first-class citizens in the application context rather than external dependencies.

### 2.2 How

Spring AI is organized around five core abstractions:

**ChatClient.** The primary entry point for interacting with a language model. Built via
`ChatClient.Builder` (auto-configured as a bean in Spring Boot), it exposes a fluent API:
`.prompt()` sets system and user text, `.advisors()` registers pipeline interceptors,
`.call()` or `.stream()` executes the request. `ChatClient` is provider-agnostic — the
same interface works with OpenAI, Anthropic, Ollama, Azure OpenAI, and other supported
providers.

**Prompt templates.** Spring AI's `PromptTemplate` injects variables into prompt text using
`{placeholder}` syntax. Templates can be defined in-code or loaded from classpath resources
(`.st` or `.txt` files), enabling externalized prompt management. This maps to what Python
engineers know as f-string templates in LangChain, but with a Java-idiomatic resource loading
model.

**Advisors.** A chain of interceptors that wraps the `ChatClient` call pipeline. Spring AI
ships built-in advisors: `MessageChatMemoryAdvisor` appends conversation history to each
request; `QuestionAnswerAdvisor` performs RAG retrieval and context injection before the
call; `SimpleLoggerAdvisor` traces the request and response. Custom advisors implement
`CallAroundAdvisor` or `StreamAroundAdvisor` to inject logic into the call chain.
This pattern maps to LangChain's LCEL `RunnableWithMessageHistory` and retrieval chains.

**Vector store and RAG.** Spring AI provides a `VectorStore` abstraction with
implementations for pgvector, Redis, Chroma, Elasticsearch, Pinecone, and others. The
`QuestionAnswerAdvisor` encapsulates the standard RAG loop: embed the query, search the
vector store for top-k documents, inject them into the prompt context, call the model.
The `DocumentReader`, `TextSplitter`, and `VectorStore.add()` APIs handle the ingestion
pipeline.

**Tool calling.** Spring AI maps Java methods annotated with `@Tool` to the provider's
function-calling format. The `ChatClient` resolves tool calls in the model's response,
dispatches to the annotated method, and re-submits the result — implementing the
tool-use loop automatically. This maps to LangChain's `@tool` Python decorator pattern.

### 2.3 Code example

```java
// Spring Boot application — auto-configured ChatClient
// No equivalent lab in this module; see docs/frameworks-tools/langchain.md for the Python equivalent

@Service
public class AssistantService {

    private final ChatClient chatClient;

    public AssistantService(ChatClient.Builder builder, VectorStore vectorStore) {
        this.chatClient = builder
            .defaultSystem("You are a helpful enterprise assistant.")
            .defaultAdvisors(
                new MessageChatMemoryAdvisor(new InMemoryChatMemory()),
                new QuestionAnswerAdvisor(vectorStore)
            )
            .build();
    }

    public String chat(String conversationId, String userMessage) {
        return chatClient.prompt()
            .user(userMessage)
            .advisors(a -> a.param(CHAT_MEMORY_CONVERSATION_ID_KEY, conversationId))
            .call()
            .content();
    }
}

// Tool calling
@Component
public class OrderTools {

    @Tool(description = "Look up order status by order ID")
    public String getOrderStatus(String orderId) {
        return orderRepository.findById(orderId)
            .map(Order::getStatus)
            .orElse("Order not found");
    }
}

// application.properties
// spring.ai.openai.api-key=${OPENAI_API_KEY}
// spring.ai.openai.chat.options.model=gpt-4o-mini
```

---

## 3. Table

| Spring AI Component | Purpose | Python equivalent |
|--------------------|---------|-------------------|
| `ChatClient` | Fluent call builder + provider abstraction | LangChain `ChatOllama` / `ChatOpenAI` + LCEL |
| `ChatClient.Builder` | Auto-configured factory bean | LangChain chain constructor |
| `PromptTemplate` | Variable substitution in prompt strings | LangChain `ChatPromptTemplate` |
| `Advisor` | Call interceptor chain (memory, RAG, logging) | LangChain LCEL pipe `|` composition |
| `MessageChatMemoryAdvisor` | Conversation history injection | LangChain `RunnableWithMessageHistory` |
| `QuestionAnswerAdvisor` | RAG retrieval + context injection | LangChain retrieval chain |
| `VectorStore` | Embedding search abstraction | LlamaIndex `VectorStoreIndex` |
| `DocumentReader` | Document ingestion (PDF, text, web) | LlamaIndex `SimpleDirectoryReader` |
| `TextSplitter` | Chunking for ingestion | LlamaIndex `SentenceSplitter` |
| `@Tool` | Method-level tool declaration | LangChain `@tool` decorator |

| Spring AI Advisor | Effect on pipeline |
|------------------|--------------------|
| `MessageChatMemoryAdvisor` | Appends N prior messages from memory to each request |
| `QuestionAnswerAdvisor` | Retrieves top-k documents and injects as context |
| `SimpleLoggerAdvisor` | Logs full request and response at DEBUG level |
| Custom `CallAroundAdvisor` | Intercept, modify, retry, or gate any call |

---

## 4. Engineering Implications

**Dependency injection as the configuration model.** Spring AI uses the application
context as its wiring mechanism. The `ChatClient.Builder` is a prototype-scoped bean
you customize per service; the `ChatModel` is a singleton. This means AI configuration
follows the same rules as all Spring configuration: it can be externalized, profiled
(different models per environment), and overridden in tests via `@MockBean`.

**Provider switching without code changes.** Because `ChatClient` is provider-agnostic,
switching from OpenAI to Anthropic or Ollama requires only a dependency and property
change — no application code change. This is the same portability promise as Spring Data's
`JpaRepository` over different databases. In practice, switching providers requires
verifying that the new provider supports all features in use (tool calling formats differ
between providers).

**Reactive streaming.** `ChatClient.stream()` returns a `Flux<String>` from Project Reactor,
enabling streaming responses inside reactive Spring WebFlux controllers. For non-reactive
applications, Spring AI provides a synchronous `call()` path. Using `.stream()` in a
synchronous application context requires blocking collection: `flux.collectList().block()`.

**Advisor ordering matters.** Advisors execute in registration order. If `QuestionAnswerAdvisor`
(RAG) runs after `MessageChatMemoryAdvisor` (memory), the retrieved context appears after
conversation history in the prompt — which may affect model behavior. Register advisors in
the order that reflects the intended prompt structure.

**Token counting and cost management.** Spring AI's `ChatResponse` includes `ChatResponseMetadata`
with usage metrics (prompt tokens, completion tokens). Wire these into Micrometer counters
for per-service token tracking. This is the equivalent of recording LangSmith traces in
the Python ecosystem.

---

## 5. Implementation Connection

This is a concept-only topic. No executable lab is provided for this module.

To apply these patterns, create a Spring Boot 3.x project with the following dependencies:

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-pgvector-store-spring-boot-starter</artifactId>
</dependency>
```

The `AssistantService` code example above is a complete implementation seed for a
conversational RAG endpoint. For the equivalent Python implementation, see
`labs/frameworks-tools/lab-integration/main.py`.

---

## 6. Failure Modes and Limitations

**Advisor state sharing.** `InMemoryChatMemory` stores conversation history in the JVM
heap. In a multi-instance deployment, different requests from the same user can hit
different instances and lose conversation continuity. Production deployments must use
a persistent memory store (Redis, relational database) with consistent key routing.

**Tool calling parameter binding.** Spring AI uses Jackson to serialize/deserialize tool
call arguments. Methods with complex parameter types (enums, nested objects) must be
Jackson-serializable. Methods that throw checked exceptions need explicit handling —
unhandled exceptions propagate as tool execution errors to the model, which may cause
unexpected retry loops.

**RAG context window overflow.** `QuestionAnswerAdvisor` retrieves a fixed top-k
document count without awareness of the conversation history length already in the prompt.
In long conversations, the combined context may exceed the model's context window. Teams
with long-running conversations should implement a custom advisor that calculates available
token budget before injecting retrieved context.

**Spring Boot version pinning.** Spring AI's auto-configuration classes are sensitive to
the Spring Boot version. Always use the Spring AI BOM to align versions — manually mixing
Spring AI and Spring Boot versions causes `ClassNotFoundException` or
`NoSuchMethodError` at startup.

---

## 7. Summary

Spring AI provides a Spring Boot-native integration layer for LLM APIs: `ChatClient` as
the provider-agnostic call interface, advisors as the pipeline composition model, and
auto-configured beans for RAG, memory, and tool calling. The pattern maps the LCEL chain
model from Python into Spring's dependency injection architecture, allowing Java teams to
add LLM capabilities to existing applications without a new runtime or technology stack.
