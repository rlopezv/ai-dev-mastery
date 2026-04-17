# AI Dev Mastery

A progressive learning path for building AI-powered systems — from LLM fundamentals
to production-grade architectures. Designed for enterprise software architects with
a Java background who want to develop practical AI engineering skills.

---

## Repository Structure

```text
ai-dev-mastery/
├── docs/           → conceptual documentation, one directory per module
├── labs/           → executable labs, one directory per module
├── infrastructure/ → local environment (Ollama, ChromaDB, Open WebUI)
└── meta/           → editorial standards and templates (not learner-facing)
```

---

## Modules

| # | Module | Level | Docs | Labs |
|---|--------|-------|:----:|:----:|
| 01 | [LLM Fundamentals](docs/llm-fundamentals/README.md) | Foundational | ✅ | ✅ |
| 02 | [LLM APIs](docs/llm-apis/README.md) | Foundational | ✅ | ✅ |
| 03 | [Prompt Engineering](docs/prompt-engineering/README.md) | Foundational | ✅ | ✅ |
| 04 | [Structured Outputs & Tool Usage](docs/structured-outputs/README.md) | Intermediate | ✅ | ✅ |
| 05 | [RAG](docs/rag/README.md) | Intermediate | ✅ | ✅ |
| 06 | [Memory & Context Management](docs/memory-context/README.md) | Intermediate | ✅ | ✅ |
| 07 | [AI Agents](docs/ai-agents/README.md) | Intermediate | ✅ | ✅ |
| 08 | [Frameworks & Tools](docs/frameworks-tools/README.md) | Intermediate | ✅ | ✅ |
| 09 | [AI with Java](docs/ai-java/README.md) | Intermediate | ✅ | — |
| 10 | Evaluation & Testing | Advanced | ⬜ | ⬜ |
| 11 | Safety & Guardrails | Advanced | ⬜ | ⬜ |
| 12 | Performance & Optimization | Advanced | ⬜ | ⬜ |
| 13 | Deployment & Scaling | Advanced | ⬜ | ⬜ |
| 14 | Observability & MLOps | Advanced | ⬜ | ⬜ |
| 15 | Reference Architectures | Advanced | ⬜ | ⬜ |
| 16 | Real-World Projects | Advanced | ⬜ | ⬜ |

Follow the modules in order — each one builds on the previous.

---

## Getting Started

### 1. Set up the environment

Prerequisites:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [VSCode](https://code.visualstudio.com/) with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

Open the repository in a Dev Container — VSCode will detect `.devcontainer/` and
prompt you to reopen inside the container.

### 2. Start the local infrastructure

```bash
cd infrastructure
cp .env.example .env
docker-compose --profile light up -d
```

See [infrastructure/README.md](infrastructure/README.md) for hardware configuration,
available profiles, and model selection.

### 3. Read the docs, run the labs

Each module has a `docs/<module>/README.md` that lists what to read and in what order.
Labs for that module live in `labs/<module>/README.md`.

→ Start with [docs/llm-fundamentals/README.md](docs/llm-fundamentals/README.md)

---

## Documentation

The `docs/` directory contains the conceptual foundation for every module.
→ See [docs/README.md](docs/README.md) for how to navigate and what each document type covers.

---

## Labs

| # | Module | Labs | Status |
|---|--------|------|:------:|
| 01 | [LLM Fundamentals](labs/llm-fundamentals/README.md) | lab-tokenization, lab-context-window, lab-inference-parameters | ✅ |
| 02 | [LLM APIs](labs/llm-apis/README.md) | lab-chat-completion, lab-streaming, lab-tool-calling | ✅ |
| 03 | [Prompt Engineering](labs/prompt-engineering/README.md) | lab-prompt-anatomy, lab-chain-of-thought, lab-few-shot | ✅ |
| 04 | [Structured Outputs](labs/structured-outputs/README.md) | lab-json-mode, lab-function-calling, lab-output-validation | ✅ |
| 05 | [RAG](labs/rag/README.md) | lab-embeddings, lab-chunking-strategies, lab-retrieval-playground, lab-query-pipeline, lab-rag-evaluation | ✅ |
| 06 | [Memory & Context Management](labs/memory-context/README.md) | lab-memory-types, lab-conversation-history, lab-context-management, lab-external-memory, lab-integration | ✅ |
| 07 | [AI Agents](labs/ai-agents/README.md) | lab-single-agent-loop, lab-tool-use-loops, lab-multi-agent, lab-agent-patterns, lab-mcp-server, lab-integration | ✅ |
| 08 | [Frameworks & Tools](labs/frameworks-tools/README.md) | lab-langchain, lab-llamaindex, lab-autogen, lab-semantic-kernel, lab-integration | ✅ |
| 09 | AI with Java | — (concept-only) | — |
| 10 | Evaluation & Testing | — | ⬜ |
| 11 | Safety & Guardrails | — | ⬜ |
| 12 | Performance & Optimization | — | ⬜ |
| 13 | Deployment & Scaling | — | ⬜ |
| 14 | Observability & MLOps | — | ⬜ |
| 15 | Reference Architectures | — | ⬜ |
| 16 | Real-World Projects | — | ⬜ |

→ See [labs/README.md](labs/README.md) for infrastructure requirements and conventions.
