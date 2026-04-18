---
id: "frameworks-tools-labs-readme"
title: "Frameworks and Tools — Labs"
type: "lab-readme"
step: "frameworks-tools"
path: "labs/frameworks-tools/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "LangChain"
  - "LCEL"
  - "LangChain memory"
  - "LangChain agent"
  - "LlamaIndex"
  - "index"
  - "query engine"
  - "AutoGen"
  - "ConversableAgent"
  - "Semantic Kernel"
  - "kernel"
  - "plugin"
  - "planner"
  - "pipeline composition"

prerequisites:
  - "docs/frameworks-tools/README.md"
  - "docs/frameworks-tools/langchain.md"
  - "docs/frameworks-tools/llamaindex.md"
  - "labs/ai-agents/README.md"

next:
  - "labs/ai-java/README.md"

related:
  - "docs/frameworks-tools/architecture.md"
  - "docs/frameworks-tools/implementation-reference.md"

implementation_refs:
  - "labs/frameworks-tools/lab-langchain"
  - "labs/frameworks-tools/lab-llamaindex"
  - "labs/frameworks-tools/lab-autogen"
  - "labs/frameworks-tools/lab-semantic-kernel"
  - "labs/frameworks-tools/lab-integration"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Guides the implementation of LangChain, LlamaIndex, AutoGen, and Semantic Kernel applications across five labs, with a shared corpus used by all retrieval labs."
---

# Frameworks and Tools — Labs

## Navigation

[Labs](../README.md) / Frameworks and Tools — Labs

---


## 1. Overview

These labs implement concrete applications with each major AI framework covered in the
`frameworks-tools` module. Each lab isolates one framework and builds a self-contained
application that demonstrates the framework's primary abstraction at runtime.

**What these labs cover:**
- Building a LangChain LCEL chain with session memory, a retrieval step, and a tool-calling agent
- Building a LlamaIndex retrieval pipeline over the shared corpus with persistent ChromaDB indexing
- Coordinating agents through an AutoGen conversation loop with tool execution
- Registering Semantic Kernel plugins and using the planner to compose multi-step tasks
- Combining LangChain orchestration with a LlamaIndex retriever in an integrated pipeline

**What these labs do not cover:**
- Production deployment of framework-based applications (covered in `deployment-scaling`)
- Evaluation and testing of framework pipelines (covered in `evaluation-testing`)
- LangGraph, LlamaIndex AgentRunner, or AutoGen Studio (advanced extensions beyond this module)

**Corpus:** `lab-langchain`, `lab-llamaindex`, and `lab-integration` operate on a shared
corpus of three technical documents. Read the corpus before running these labs — it lets
you predict retrieval results and verify that the pipeline is behaving correctly.

---

## 2. Read the Corpus Before Running the Labs

The `corpus/` directory contains three technical documents used by the retrieval labs.

```text
labs/frameworks-tools/corpus/
├── vector-search.md          ← dense retrieval, HNSW, approximate nearest-neighbor search
├── llm-api-design.md         ← LLM API design patterns, streaming, rate limiting, retries
└── agent-coordination.md     ← multi-agent coordination patterns, message passing, state isolation
```

**Why reading first matters.** The corpus is a fixed knowledge base. When you run
`lab-langchain` or `lab-llamaindex` and issue a query like "How does HNSW work?", the
correct behavior is for the pipeline to retrieve chunks from `vector-search.md` and
incorporate them into the response. If you have read the file, you can confirm the
retrieval is working — the response should reflect the specific algorithms described there,
not general knowledge the model already has.

Read all three files before running `lab-langchain`, `lab-llamaindex`, or `lab-integration`.

---

## 3. Lab Inventory

| Lab | Description | Type | Decision |
|-----|-------------|------|----------|
| `lab-langchain` | Build a LangChain LCEL retrieval chain with session memory and a tool-calling agent | implementation | required |
| `lab-llamaindex` | Build a LlamaIndex VectorStoreIndex pipeline over the corpus with persistent ChromaDB storage | implementation | required |
| `lab-autogen` | Implement a two-agent AutoGen conversation and a three-agent GroupChat with tool execution | implementation | optional |
| `lab-semantic-kernel` | Register Semantic Kernel plugins, configure a planner, and compose a multi-step task | implementation | optional |
| `lab-integration` | Connect a LangChain LCEL chain to a LlamaIndex retriever for end-to-end RAG with session memory | module-integration | optional |

---

## 4. Execution Model

`lab-langchain`, `lab-autogen`, `lab-semantic-kernel`, and `lab-integration` run as Python
scripts via `python main.py` from the lab directory. They call the OpenAI API or a local
Ollama instance depending on the `LLM_PROVIDER` environment variable.

`lab-llamaindex` runs as a Python script and requires ChromaDB to be running for index
persistence. Run it with the `intermediate` profile.

**Infrastructure per lab:**

| Lab | Ollama | OpenAI API | ChromaDB |
|-----|--------|------------|----------|
| `lab-langchain` | ✅ (default) | optional | — |
| `lab-llamaindex` | ✅ (default) | optional | ✅ (required) |
| `lab-autogen` | — | ✅ (required) | — |
| `lab-semantic-kernel` | — | ✅ (required) | — |
| `lab-integration` | ✅ (default) | optional | ✅ (required) |

**Start infrastructure:**

```bash
# Light profile — Ollama only (lab-langchain, lab-autogen, lab-semantic-kernel)
docker-compose --profile foundational up -d

# Full profile — Ollama + ChromaDB (lab-llamaindex, lab-integration)
docker-compose --profile intermediate up -d
```

**Install Python dependencies:**

```bash
pip install -r labs/frameworks-tools/requirements.txt
```

**Copy and edit environment variables:**

```bash
cp labs/frameworks-tools/.env.example labs/frameworks-tools/.env
# Edit .env: set OPENAI_API_KEY if using OpenAI, leave defaults for Ollama
```

**Run a lab:**

```bash
cd labs/frameworks-tools/lab-langchain
python main.py
```

---

## 5. Lab Structure

```text
labs/frameworks-tools/
├── README.md                           ← this file
├── requirements.txt                    ← all Python dependencies for this module
├── .env.example                        ← environment variable template
├── corpus/
│   ├── vector-search.md                ← retrieval algorithms and vector search
│   ├── llm-api-design.md               ← LLM API design patterns
│   └── agent-coordination.md           ← multi-agent coordination patterns
├── shared/
│   ├── config.py                       ← env vars, LLM client factory, load_corpus()
│   └── utils.py                        ← display helpers, token counter
├── lab-langchain/
│   ├── README.md
│   └── main.py
├── lab-llamaindex/
│   ├── README.md
│   └── main.py
├── lab-autogen/
│   ├── README.md
│   └── main.py
├── lab-semantic-kernel/
│   ├── README.md
│   └── main.py
└── lab-integration/
    ├── README.md
    └── main.py
```

Labs are isolated: each `main.py` imports only from `shared/` and the standard library.
No lab imports from another lab's directory.

---

## 6. Shared Module

All labs import from `labs/frameworks-tools/shared/`. The shared module provides:

| Module | Exports | Purpose |
|--------|---------|---------|
| `config.py` | `OLLAMA_URL`, `OPENAI_API_KEY`, `MODEL`, `CHROMA_HOST`, `CHROMA_PORT`, `CORPUS_DIR`, `load_corpus()` | Environment configuration and corpus loader |
| `utils.py` | `print_separator()`, `print_response()`, `count_tokens()` | Output formatting and token counting helpers |

`load_corpus()` follows the module-standard signature:

```python
def load_corpus(corpus_dir: pathlib.Path = CORPUS_DIR) -> list[dict]:
    """
    Load all .md files from corpus_dir.
    Returns list of dicts with 'source' (filename) and 'text' (content) keys.
    """
```

`lab-autogen` and `lab-semantic-kernel` do not use the corpus — they import only
`config.py` for API key and model configuration.

---

## 7. Mapping to Documentation

| Documentation | Lab | What the lab verifies |
|---------------|-----|-----------------------|
| `docs/frameworks-tools/langchain.md` | `lab-langchain` | LCEL chain composed with `\|`; memory persists across session turns; agent dispatches tool calls; `RunnableWithMessageHistory` requires `configurable` |
| `docs/frameworks-tools/llamaindex.md` | `lab-llamaindex` | Corpus chunked into nodes; index persisted to ChromaDB; reloaded without re-ingesting; `similarity_top_k` change produces different results |
| `docs/frameworks-tools/autogen.md` | `lab-autogen` | Two-agent conversation terminates on "TERMINATE"; tool call dispatched by `UserProxyAgent`; GroupChat selects next speaker |
| `docs/frameworks-tools/semantic-kernel.md` | `lab-semantic-kernel` | Plugin registered; planner selects correct function; vague description causes wrong function selection |
| `docs/frameworks-tools/architecture.md` | `lab-integration` | LangChain LCEL chain wraps a LlamaIndex retriever; end-to-end pipeline returns response with corpus provenance |

---

## 8. Validation

**lab-langchain**
```text
Part 1 — Retrieval chain:
  Query: "What algorithms does HNSW use for approximate nearest-neighbor search?"
  Expected: Response references HNSW-specific content from corpus/vector-search.md.
            Source documents printed with filenames and similarity scores.

Part 2 — Session memory:
  Turn 1: "What is rate limiting in LLM APIs?"
  Turn 2: "What strategies exist for handling it?"
  Expected: Turn 2 response references rate limiting without repeating the question
            (evidence of history awareness). Session ID printed each turn.

Part 3 — Tool-calling agent:
  Task: "What is 42 multiplied by 17, and what is the square root of the result?"
  Expected: Agent emits at least two tool calls (multiply, sqrt).
            Final answer: "42 × 17 = 714, √714 ≈ 26.72"
```

**lab-llamaindex**
```text
Part 1 — Index construction:
  Expected: "Loaded N documents. Created M nodes."
            Index persisted to ChromaDB. Run time printed.

Part 2 — Index reload:
  Expected: "Loaded index from ChromaDB (no re-ingestion)." printed.
            Reload time significantly less than construction time.

Part 3 — Query comparison:
  Query: "How does HNSW enable fast approximate nearest-neighbor search?"
  With top_k=1: Response based on single node — may lack context.
  With top_k=5: Response richer, references multiple aspects.
  Expected: Both queries print "Source nodes retrieved: N" with N matching top_k.
```

**lab-autogen** *(optional)*
```text
Two-agent:
  Expected: AssistantAgent response ends with "TERMINATE".
            UserProxyAgent prints "TERMINATION DETECTED — conversation ended."
            Tool call dispatched and result returned within the conversation.

GroupChat:
  Expected: GroupChatManager prints "Next speaker: <name>" before each turn.
            Three agents each contribute at least one message.
            Conversation ends within max_round.
```

**lab-semantic-kernel** *(optional)*
```text
Part 1 — Direct plugin call:
  Expected: Native function returns expected result. Semantic function produces
            a formatted summary. Both results printed.

Part 2 — Planner:
  Task: "Summarize the key design patterns and format the result as a report."
  Expected: Planner selects both summarize and format functions.
            "Selected function: <name>" printed for each planner decision.
            Final output includes formatted report.

Part 3 — Failure case (vague description):
  Expected: Planner selects wrong function or skips a required step.
            "Selected function: <wrong_name>" appears in output.
```

**lab-integration** *(optional)*
```text
Query: "What coordination patterns exist for multi-agent systems and how does
        message passing work?"
Expected: LlamaIndex retriever surfaces nodes from corpus/agent-coordination.md.
          LangChain chain assembles context from retrieved nodes.
          Response explicitly references content from the corpus file.
          Source node filenames printed: "Retrieved from: agent-coordination.md".
          Session turn 2 references turn 1 (memory active).
```

---

## 9. Common Issues

**`langchain_openai` not found.** LangChain's provider integrations are in separate
packages. Install `langchain-openai` for OpenAI models and `langchain-community` for
Ollama. The `requirements.txt` includes both, but verify installation if imports fail.

**`RunnableWithMessageHistory` raises `KeyError: 'session_id'`.** The `configurable`
key is missing from the `invoke` call. Every call to a chain with history must include
`config={"configurable": {"session_id": "<id>"}}`. This is not optional.

**LlamaIndex index build fails with ChromaDB connection error.** ChromaDB must be running
before `lab-llamaindex` is executed. Start the intermediate profile with
`docker-compose --profile intermediate up -d` and wait for ChromaDB to report healthy before
running the lab.

**LlamaIndex query returns empty results after reload.** The embedding model used at
query time differs from the model used at index build time. Both the lab's build and
query paths must use the same `embed_model` setting. Check `shared/config.py` for the
canonical embedding model name.

**AutoGen conversation does not terminate.** The `AssistantAgent`'s system message does
not instruct it to include "TERMINATE" in the final response. Update the system message
to include an explicit instruction: "When the task is complete, end your response with
the word TERMINATE." Also set `max_turns` as a safety guard.

**Semantic Kernel `@kernel_function` not found.** The import path changed between SK
versions. Verify the installed version matches `requirements.txt`. In SK ≥1.0, the
decorator is at `semantic_kernel.functions.kernel_function`.

**Ollama does not produce tool calls for LangChain agent.** Confirm the Ollama model
supports the `tools=` parameter. `mistral:latest` and `llama3.1` support tool calling.
Older models or smaller variants may not. If Ollama does not return tool calls, set
`LLM_PROVIDER=openai` and provide `OPENAI_API_KEY`.

---

## 10. Engineering Notes

**ChromaDB persistence across lab runs.** `lab-llamaindex` creates a named collection in
ChromaDB. On subsequent runs, the lab checks whether the collection exists before
re-ingesting. This is intentional — it demonstrates the index-query separation pattern.
To force a fresh index, delete the collection via the ChromaDB HTTP API or set
`RESET_INDEX=true` in the environment.

**LangChain version sensitivity.** LangChain has released breaking API changes in minor
versions. The labs target `langchain>=0.3` and `langchain-openai>=0.2`. The legacy
`LLMChain`, `ConversationChain`, and `RetrievalQA` classes are not used — all chains use
LCEL. If you see deprecation warnings about these classes, the installed version is
mismatched.

**AutoGen code execution is disabled in labs.** `code_execution_config=False` in
`lab-autogen`. Enabling it causes the `UserProxyAgent` to execute Python code blocks
from the assistant's responses in a subprocess. This is intentional for the lab to
remain safe in any environment. The lab README notes this explicitly.

**Semantic Kernel async execution.** All SK invocations are coroutines. The lab entry
point uses `asyncio.run(main())`. Do not call `asyncio.run()` inside an already-running
event loop (e.g., Jupyter notebooks). In a notebook, use `await main()` instead.

**Corpus loading is read-once.** `load_corpus()` reads files from disk each time it is
called. For labs that call it multiple times (e.g., `lab-integration`), cache the result
in a local variable rather than calling `load_corpus()` on each request.

---

## 11. Next Steps

After completing these labs, proceed to `labs/ai-java/README.md` to apply AI engineering
patterns in a Java context using Spring AI and LangChain4j.

To compare framework-based retrieval with the raw pipeline from the `rag` module, run
`lab-llamaindex` alongside `labs/rag/lab-integration/` on the same corpus. The retrieval
quality difference is observable with the same query.

To extend `lab-langchain` with the agent patterns from the previous module, replace the
`AgentExecutor` with a ReAct-structured system prompt and compare the behavior.
