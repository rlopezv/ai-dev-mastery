---
id: "ai-java-labs-readme"
title: "AI Development in Java — Labs"
type: "lab-readme"
step: "ai-java"
path: "labs/ai-java/README.md"
status: "draft"
level: "advanced"
concepts:
  - "spring-ai"
  - "langchain4j"
prerequisites:
  - "docs/ai-java/README.md"
related:
  - "labs/frameworks-tools/README.md"
summary: "Concept-only module — no executable labs. Documents why Java labs are out of scope and provides Python reference implementations for equivalent patterns."
---

# AI Development in Java — Labs

## Navigation

[Labs](../README.md) / AI Development in Java — Labs

---

## Status

This module is **concept-only**. No executable labs are provided.

## Why no labs

The `ai-java` module covers Java AI framework concepts (Spring AI, LangChain4j) for an
audience of Java enterprise architects. The underlying AI patterns — RAG, tool calling,
agent loops, memory management — are already demonstrated in the Python labs from prior
modules (`frameworks-tools`, `rag`, `ai-agents`, `memory-context`).

Adding Java labs would require:
- A JDK 17+ runtime in the devcontainer
- A Spring Boot 3.x project skeleton per lab
- Maven or Gradle build tooling
- Different infrastructure integration (Spring Data vs Python clients)

This scope is beyond the current tutorial footprint, which uses a Python-centric devcontainer.

## Applying the concepts

To apply the `ai-java` module concepts in a running environment:

1. Create a new Spring Boot 3.x project at [start.spring.io](https://start.spring.io)
2. Add the `spring-ai-openai-spring-boot-starter` or equivalent dependency
3. Use the code examples from the topic docs as implementation seeds:
   - `docs/ai-java/spring-ai.md` — Spring AI `ChatClient` and advisor patterns
   - `docs/ai-java/langchain4j.md` — LangChain4j AI service interface pattern
   - `docs/ai-java/java-patterns.md` — Java idioms for AI integration

## Python reference implementations

| Java pattern | Python equivalent |
|-------------|-------------------|
| Spring AI advisor chain (memory + RAG) | `labs/frameworks-tools/lab-integration/main.py` |
| LangChain4j AI service with tools | `labs/frameworks-tools/lab-langchain/main.py` demo_agent |
| RAG ingestion pipeline | `labs/frameworks-tools/lab-llamaindex/main.py` build_index |
| Conversation memory per session | `labs/frameworks-tools/lab-langchain/main.py` demo_memory |
