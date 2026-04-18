# Documentation

## Navigation

[Home](../README.md) / Docs

---

The `docs/` directory contains the conceptual foundation for every module. Each module
has its own directory with a set of documents that explain the what, why, and how before
you run the labs.

---

## How to navigate

Within each module, read documents in this order:

| Step | Document | Purpose |
|------|----------|---------|
| 1 | `README.md` | Module overview, concept map, learning sequence |
| 2 | Topic files (`<concept>.md`) | One concept per file, in the order listed in the README |
| 3 | `architecture.md` | How the components fit together as a system |
| 4 | `implementation-reference.md` | Patterns, data structures, and trade-offs used in the labs |
| 5 | `validation.md` | What to verify before moving to the next module |

The labs implement what the docs explain. Open the corresponding lab only after reading
the topic document it maps to.

---

## Document types

| Type | What it contains |
|------|-----------------|
| `README.md` | Module scope, concept map, reading order, lab inventory, engineering takeaways |
| Topic (`<concept>.md`) | One concept: why it exists, how it works, minimal code example |
| `architecture.md` | Component diagram, data flows, integration points |
| `implementation-reference.md` | Concrete patterns, schema definitions, execution flows used across the labs |
| `validation.md` | Practical tasks, lab criteria, integration scenarios, self-assessment |

Each `README.md` closes with an **Engineering Takeaways** section — an architect-oriented synthesis
of what the module adds, when to use it, key trade-offs, and common failure modes. The depth of this
section varies by module level (foundational / intermediate / advanced).

---

## Modules

| Module | Description | Status |
|--------|-------------|:------:|
| [LLM Fundamentals](llm-fundamentals/README.md) | Tokens, context windows, inference, sampling strategies | ✅ |
| [LLM APIs](llm-apis/README.md) | OpenAI-compatible API, streaming, tool calling, client patterns | ✅ |
| [Prompt Engineering](prompt-engineering/README.md) | Prompt structure, chain-of-thought, few-shot, system prompts | ✅ |
| [Structured Outputs & Tool Usage](structured-outputs/README.md) | JSON schema enforcement, function calling, output validation | ✅ |
| [RAG](rag/README.md) | Embeddings, chunking, retrieval strategies, context assembly, evaluation | ✅ |
| [Memory & Context Management](memory-context/README.md) | Conversation history, token budgets, context management strategies, external memory | ✅ |
| [AI Agents](ai-agents/README.md) | Tool use, planning, multi-step execution, agent loops | ✅ |
| [Frameworks & Tools](frameworks-tools/README.md) | LangChain, LlamaIndex, AutoGen, Semantic Kernel, workflow tools | ✅ |
| [AI with Java](ai-java/README.md) | Spring AI, LangChain4j, Quarkus integration, Java AI patterns | ✅ |
| Evaluation & Testing | Automated evaluation, regression testing, benchmark design | ⬜ |
| Safety & Guardrails | Input/output filtering, alignment techniques, red-teaming | ⬜ |
| Performance & Optimization | Quantization, batching, latency profiling | ⬜ |
| Deployment & Scaling | Containerization, inference servers, scaling strategies | ⬜ |
| Observability & MLOps | Tracing, logging, drift detection, model lifecycle | ⬜ |
| Reference Architectures | End-to-end system designs combining multiple modules | ⬜ |
| Real-World Projects | Full production scenarios with evaluation and deployment | ⬜ |
