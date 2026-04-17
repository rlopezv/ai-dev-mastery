---
id: "ai-java-java-patterns"
title: "Java AI Patterns"
type: "topic"
step: "ai-java"
path: "docs/ai-java/java-patterns.md"
status: "draft"
level: "intermediate"

concepts:
  - "Java AI pattern"
  - "AI service"

prerequisites:
  - "docs/ai-java/spring-ai.md"
  - "docs/ai-java/langchain4j.md"

next:
  - "docs/ai-java/architecture.md"

related:
  - "docs/frameworks-tools/framework-comparison.md"
  - "docs/ai-agents/tool-use-loops.md"
  - "docs/memory-context/context-management.md"

implementation_refs: []

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Catalogs the implementation idioms Java engineers apply when building LLM-powered applications: type-safe AI service interfaces, Spring dependency injection for model clients, reactive streaming, and configuration externalization."
---

## 1. Intuition

The previous topics described what Spring AI and LangChain4j provide. This topic answers
the narrower question: when writing the actual Java code, which patterns recur across
both frameworks, and what does idiomatic Java AI code look like?

Java brings its own idioms to AI development. Interfaces define contracts. Dependency
injection wires configurations. Annotations express declarative intent. Records and sealed
classes model structured outputs. Reactive streams handle asynchronous output. These are
not new patterns invented for AI — they are the standard Java patterns applied to a new
problem domain.

---

## 2. Explanation

### 2.1 Why

AI code written without these idioms produces the same problems it would in any other
Java domain: hard-coded credentials, untestable components, ambiguous types, and
configuration drift between environments. The patterns below make Java AI code testable,
configurable, and maintainable by teams that did not write it.

### 2.2 How

**Pattern 1: Interface-driven AI services.**
Declare AI behavior as a Java interface. LangChain4j generates the implementation;
Spring AI can wire the same pattern with `ChatClient`. This keeps AI behavior declarative
and separates the contract from the provider. Callers depend on the interface, not the
framework implementation — enabling substitution in tests.

```java
interface KnowledgeAssistant {
    @SystemMessage("Answer using only provided context. Be concise.")
    String answer(@MemoryId String sessionId, @UserMessage String question);
}
```

**Pattern 2: Configuration via Spring properties.**
Externalize model selection, temperature, and context window settings to
`application.properties` or `application.yml`. Use Spring `@ConfigurationProperties`
beans to validate and namespace AI configuration. This follows the same pattern as
`spring.datasource.*` configuration.

```java
@ConfigurationProperties(prefix = "ai")
record AiProperties(String model, double temperature, int maxTokens) {}
```

**Pattern 3: Per-environment model routing.**
Use Spring profiles to route to different models per environment: a local Ollama model
in development, a hosted model in staging and production. The `ChatClient` or
`ChatLanguageModel` bean is the injection point; the implementation changes via profile,
not application code.

```yaml
# application-dev.yml
spring.ai.ollama.chat.options.model: mistral

# application-prod.yml
spring.ai.openai.chat.options.model: gpt-4o-mini
```

**Pattern 4: Reactive streaming with Project Reactor.**
For Spring AI streaming responses, return `Flux<String>` from controller methods. Use
`chatClient.prompt().user(message).stream().content()` to obtain the flux.
In non-reactive applications, collect the flux synchronously with
`flux.collectList().block()` — but understand this blocks the calling thread.

```java
// Spring WebFlux controller
@GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> streamResponse(@RequestParam String message) {
    return chatClient.prompt()
        .user(message)
        .stream()
        .content();
}
```

**Pattern 5: Structured output via typed response.**
Both frameworks support binding model responses to Java records or classes. Spring AI's
`.call().entity(MyRecord.class)` instructs the model to respond in JSON and deserializes
the result. LangChain4j supports the same via return type on the AI service interface.
This is the Java equivalent of Pydantic models in Python structured output patterns.

```java
// LangChain4j typed response
interface ClassifierService {
    @SystemMessage("Classify the intent. Respond in JSON.")
    IntentResult classify(@UserMessage String text);
}

record IntentResult(String intent, double confidence, List<String> entities) {}

// Spring AI typed response
MyRecord result = chatClient.prompt()
    .user(text)
    .call()
    .entity(MyRecord.class);
```

**Pattern 6: Token usage tracking.**
Extract token usage from `ChatResponse` metadata and publish as Micrometer counters.
This pattern enables per-service cost attribution and token budget enforcement without
third-party observability services.

```java
ChatResponse response = chatClient.prompt().user(message).call().chatResponse();
ChatResponseMetadata metadata = response.getMetadata();
Usage usage = metadata.getUsage();
meterRegistry.counter("ai.tokens.prompt",
    "service", serviceName).increment(usage.getPromptTokens());
meterRegistry.counter("ai.tokens.completion",
    "service", serviceName).increment(usage.getGenerationTokens());
```

### 2.3 Code example

```java
// Integration of the core patterns — no runnable lab; see labs/frameworks-tools/ for Python equivalents

@Service
@RequiredArgsConstructor
public class EnterpriseChatService {

    private final ChatClient chatClient;         // Spring AI — injected via auto-configuration
    private final MeterRegistry meterRegistry;   // Micrometer — injected by Spring Boot

    public String chat(String sessionId, String userMessage) {
        ChatResponse response = chatClient.prompt()
            .user(userMessage)
            .advisors(a -> a.param(CHAT_MEMORY_CONVERSATION_ID_KEY, sessionId))
            .call()
            .chatResponse();

        trackUsage(response);
        return response.getResult().getOutput().getContent();
    }

    private void trackUsage(ChatResponse response) {
        Usage usage = response.getMetadata().getUsage();
        meterRegistry.counter("ai.tokens.prompt").increment(usage.getPromptTokens());
        meterRegistry.counter("ai.tokens.completion").increment(usage.getGenerationTokens());
    }
}
```

---

## 3. Table

| Pattern | Framework | When to apply |
|---------|-----------|---------------|
| Interface-driven AI service | LangChain4j (primary), Spring AI | When AI logic is called from multiple application layers |
| Spring properties externalization | Spring AI | Any Spring Boot deployment |
| Profile-based model routing | Spring AI | Dev/staging/prod with different model tiers |
| Reactive streaming (`Flux<String>`) | Spring AI + WebFlux | Long responses, SSE endpoints, async UI updates |
| Structured output (typed entity) | Both | Downstream processing, schema enforcement |
| Token usage tracking (Micrometer) | Spring AI (built-in), LangChain4j (manual) | Cost attribution, budget enforcement |
| `@MockBean` replacement in tests | Spring AI | Unit/integration tests without LLM calls |
| `ChatMemoryProvider` per session ID | LangChain4j | Multi-user conversational applications |

| Java concept | AI application |
|-------------|----------------|
| Interface | AI service contract (decouples AI from framework) |
| `record` | Structured output schema, configuration properties |
| `@ConfigurationProperties` | AI model configuration externalization |
| Spring profile | Per-environment model routing |
| `Flux<T>` | Streaming response from the model |
| Micrometer counter | Token usage and cost tracking |
| `@MockBean` | LLM client substitution in tests |
| `@Tool` / `@Function` | Method exposed as a model-callable function |

---

## 4. Engineering Implications

**Testability as a first-class concern.** The interface-driven pattern produces AI services
that can be mocked in unit tests without LLM calls. In Spring AI, `@MockBean ChatClient`
replaces the real client in test contexts. In LangChain4j, the AI service interface
implementation can be replaced with a stub. Teams that skip the interface layer end up
testing against the real model, which introduces latency, cost, and nondeterminism into
the test suite.

**Structured output reduces post-processing code.** Mapping a free-text model response
to a Java object in application code is fragile: it requires string parsing, null handling,
and schema validation. Using typed structured output (`.entity(MyRecord.class)` or a typed
AI service return type) delegates parsing and validation to the framework. The trade-off is
that structured output uses JSON mode or response format constraints, which not all models
support at equal quality.

**Reactive streaming adds complexity.** `Flux<String>` streaming improves user-perceived
latency for long responses, but it requires a reactive controller, SSE client, and
backpressure handling. For internal service calls that are not user-facing, synchronous
collection is simpler and sufficient. Introduce streaming only where the user experience
benefit justifies the added complexity.

**Configuration drift.** Prompt templates, system messages, and model parameters embedded
in `@SystemMessage` annotations are compiled into the application JAR. Changing a prompt
requires a code change and deployment. For applications where prompt iteration is frequent,
externalizing prompt templates to classpath resources (loaded via `PromptTemplate`) or a
configuration store decouples prompt changes from code changes.

---

## 5. Implementation Connection

This is a concept-only topic. No executable lab is provided.

The patterns described here synthesize what Spring AI (`spring-ai.md`) and LangChain4j
(`langchain4j.md`) demonstrate individually. For the Python equivalents of each pattern,
the closest references are:

- Interface-driven AI service → `labs/frameworks-tools/lab-langchain/main.py` demo_agent
- Structured output → `docs/structured-outputs/structured-outputs.md`
- Memory per session ID → `labs/frameworks-tools/lab-langchain/main.py` demo_memory
- Token tracking → Spring AI's `ChatResponseMetadata` (no direct Python lab; Python uses LangSmith)

---

## 6. Failure Modes and Limitations

**Over-engineering for simple use cases.** Not every AI integration needs an AI service
interface, a vector store, and a Micrometer counter. A single `@Service` with an injected
`ChatClient` and one `chat(String message)` method is sufficient for many use cases. Apply
the full pattern set only where the complexity is warranted.

**Mixing async and sync patterns.** Calling `flux.block()` inside a WebFlux reactive
pipeline introduces a blocking operation on the reactive thread pool, which can exhaust
threads under load. In a reactive application, the entire chain — from model call to HTTP
response — must be non-blocking. In a servlet-based application, `flux.block()` is
acceptable but unnecessary: use the synchronous `.call().content()` path instead.

**Annotation-driven prompt injection attacks.** `@UserMessage` parameters that pass
user input directly into the prompt without sanitization are vulnerable to prompt injection.
The AI service interface does not validate or sanitize its parameters. Apply input
validation at the controller layer before passing user-controlled strings to AI service
methods, especially when the AI service has tool access.

---

## 7. Summary

Java AI development applies familiar Java idioms — interfaces, dependency injection, records,
Spring profiles, Micrometer counters — to the AI problem domain. The most impactful pattern
is the interface-driven AI service: declaring AI behavior as a typed Java interface
decouples AI functionality from its implementation, enables testing without live model
calls, and integrates naturally into Spring Boot applications. The other patterns extend
this foundation: profile-based routing for environment portability, structured output for
type safety, and reactive streaming for user-facing latency optimization.
