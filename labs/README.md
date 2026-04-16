# Labs

The `labs/` directory contains executable labs for every module. Each lab implements
one concept from the corresponding `docs/` document. Labs in a module build on each
other — run them in the order listed in the module README.

---

## How to navigate

Labs follow the same module sequence as `docs/`. The entry point for each module's
labs is `labs/<module>/README.md`, linked from the module table below and from each
`docs/<module>/README.md`.

---

## Infrastructure

All labs run locally. The required services depend on the module:

| Profile | Services | Modules |
|---------|----------|---------|
| `light` | Ollama + Open WebUI | 01 LLM Fundamentals → 04 Structured Outputs |
| `light` + local ChromaDB | Ollama + Open WebUI + ChromaDB PersistentClient (no Docker) | 06 Memory & Context Management |
| `full` | Ollama + Open WebUI + ChromaDB server | 05 RAG and later (when Docker ChromaDB is required) |

Start the infrastructure before running any lab:

```bash
cd infrastructure
cp .env.example .env

# Modules 01–04
docker-compose --profile light up -d

# Module 05 onwards
docker-compose --profile full up -d
```

For hardware configuration (GPU, VRAM, model selection) see
[infrastructure/README.md](../infrastructure/README.md).

---

## Runtime prerequisites

Each module declares its own Python dependencies in `labs/<module>/requirements.txt`.
Install them before running that module's labs:

```bash
pip install -r labs/<module>/requirements.txt
```

Python 3.11 or later is required across all modules.

---

## Conventions

**`shared/`** — each module has a `labs/<module>/shared/` directory with utilities
shared across all labs in that module (API client, configuration, common helpers).
Never import from another module's `shared/`.

**`corpus/`** — modules that operate on a fixed document set include a
`labs/<module>/corpus/` directory. Read those files before running the labs —
knowing the content lets you predict retrieval results, understand similarity scores,
and verify that the pipeline is working correctly. Other modules follow the same
pattern when a fixed knowledge base is needed.

**`.env`** — each module provides a `.env.example`. Copy it to `.env` and edit only
if your Ollama URL or model names differ from the defaults. Never hardcode URLs or
model names in lab code.

**Execution order** — within a module, labs must be run in the listed order. Later
labs depend on state (ChromaDB collections, trained artifacts) produced by earlier
ones. The module README marks which labs produce shared state.

---

## Modules

| Module | Labs | Status |
|--------|------|:------:|
| [LLM Fundamentals](../labs/llm-fundamentals/README.md) | lab-tokenization, lab-context-window, lab-inference-parameters | ✅ |
| [LLM APIs](../labs/llm-apis/README.md) | lab-chat-completion, lab-streaming, lab-tool-calling | ✅ |
| [Prompt Engineering](../labs/prompt-engineering/README.md) | lab-prompt-anatomy, lab-chain-of-thought, lab-few-shot | ✅ |
| [Structured Outputs](../labs/structured-outputs/README.md) | lab-json-mode, lab-function-calling, lab-output-validation | ✅ |
| [RAG](rag/README.md) | lab-embeddings, lab-chunking-strategies, lab-retrieval-playground, lab-query-pipeline, lab-rag-evaluation | ✅ |
| [Memory & Context Management](memory-context/README.md) | lab-memory-types, lab-conversation-history, lab-context-management, lab-external-memory, lab-integration | ✅ |
| AI Agents | — | ⬜ |
| Frameworks & Tools | — | ⬜ |
| AI with Java | — | ⬜ |
| Evaluation & Testing | — | ⬜ |
| Safety & Guardrails | — | ⬜ |
| Performance & Optimization | — | ⬜ |
| Deployment & Scaling | — | ⬜ |
| Observability & MLOps | — | ⬜ |
| Reference Architectures | — | ⬜ |
| Real-World Projects | — | ⬜ |
