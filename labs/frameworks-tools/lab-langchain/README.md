---
id: "lab-langchain"
title: "LangChain — LCEL Retrieval Chain, Session Memory, and Tool Agent"
type: "lab-readme"
step: "frameworks-tools"
path: "labs/frameworks-tools/lab-langchain/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "LangChain"
  - "LCEL"
  - "chain"
  - "runnable"
  - "LangChain memory"
  - "LangChain agent"

prerequisites:
  - "docs/frameworks-tools/langchain.md"
  - "docs/ai-agents/tool-use-loops.md"

related:
  - "docs/frameworks-tools/architecture.md"
  - "docs/frameworks-tools/implementation-reference.md"

summary: "Implements a three-part LangChain application demonstrating LCEL retrieval chain composition, session memory with RunnableWithMessageHistory, and a tool-calling agent with AgentExecutor."
---

# LangChain — LCEL Retrieval Chain, Session Memory, and Tool Agent

## Navigation

[Labs](../../README.md) / [Frameworks and Tools — Labs](../README.md) / LangChain — LCEL Retrieval Chain, Session Memory, and Tool Agent

---


## Overview

This lab builds a LangChain application in three parts, each demonstrating a distinct
abstraction layer:

**Demo 1 — LCEL retrieval chain.** Loads the shared corpus, splits it into chunks,
indexes the chunks in an in-memory vector store, and builds an LCEL chain that retrieves
relevant chunks before answering three queries. The learner observes how `|` composes
a retriever, prompt template, model, and parser into a single callable pipeline.

**Demo 2 — Session memory.** Wraps a basic prompt-model-parser chain with
`RunnableWithMessageHistory`. Two turns with the same `session_id` demonstrate that the
second response is aware of the first question without the user repeating context.

**Demo 3 — Tool-calling agent.** Declares `multiply` and `square_root` tools with
`@tool`, assembles an `AgentExecutor`, and submits a two-step math task. The agent
emits two tool calls and produces the correct final answer.

Out of scope: persistent vector store (ChromaDB — covered in `lab-llamaindex`), streaming,
LangGraph, and framework-level RAG evaluation.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `LCEL` | `main.py` — `retrieval_chain = {...} \| retrieval_prompt \| llm \| StrOutputParser()` |
| `runnable` | `main.py` — `vectorstore.as_retriever()`, `ChatPromptTemplate`, `StrOutputParser` all implement the Runnable protocol |
| `chain` | `main.py:demo_retrieval_chain()` — the full retrieval pipeline composed with `\|` |
| `LangChain memory` | `main.py:demo_session_memory()` — `RunnableWithMessageHistory` wrapping `base_chain` |
| `LangChain agent` | `main.py:demo_tool_agent()` — `create_tool_calling_agent` + `AgentExecutor` |

---

## Setup

```bash
# Start Ollama (foundational profile)
docker-compose --profile foundational up -d

# Pull the model if not already present
ollama pull mistral

# Install dependencies
pip install -r labs/frameworks-tools/requirements.txt

# Copy environment file (defaults work for Ollama)
cp labs/frameworks-tools/.env.example labs/frameworks-tools/.env
```

**To use OpenAI instead of Ollama:**

```bash
# Edit .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

---

## Run

```bash
cd labs/frameworks-tools/lab-langchain
python main.py
```

Environment variable overrides:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `ollama` | `ollama` or `openai` |
| `MODEL` | `mistral` | Ollama model name |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `OPENAI_API_KEY` | — | Required when `LLM_PROVIDER=openai` |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |

---

## Expected Output

```
============ DEMO 1 — LCEL retrieval chain ============
Provider: ollama  |  Model: mistral
Chunk size: 500  |  Overlap: 50  |  top_k: 3

Corpus loaded: 3 documents
  • agent-coordination.md
  • llm-api-design.md
  • vector-search.md

Chunks created: 42

--- Query: How does HNSW enable fast approximate nearest... ---

Sources retrieved:
  1. vector-search.md — Hierarchical Navigable Small World (HNSW) is the dominant
     ANN algorithm in production vector databases. It builds a multi-layer...
  2. vector-search.md — A query traverses the graph top-down: it enters at the top
     layer, greedy-walks toward the query vector...
  3. vector-search.md — HNSW parameters: M — the number of bidirectional connections
     per node. Higher M improves recall...

[Answer]
HNSW enables fast ANN search by building a multi-layer navigable graph. Queries
enter at the top (coarse) layer and greedy-walk toward the query vector before
descending to finer layers. Parameters M and ef_search control the recall/latency
trade-off without rebuilding the index.

--- Query: What are the retry strategies for LLM API rate limiting? ---
...
[Answer]
Exponential backoff with jitter is the standard strategy for LLM API rate limits.
The delay is calculated as min(base × 2^attempt + random(0,1), max_delay), with
the Retry-After header providing the minimum wait after a 429 response...

============ DEMO 2 — Session memory ============

--- Turn 1 | session_id=session-demo-001 ---
User: What is rate limiting in LLM APIs?
Assistant: Rate limiting in LLM APIs restricts the number of requests per minute (RPM)
and tokens per minute (TPM) a client may send. When exceeded, the API returns HTTP 429
with a Retry-After header specifying the wait duration.

--- Turn 2 | session_id=session-demo-001 ---
User: What strategies exist for handling it?
Assistant: For handling rate limits, exponential backoff with jitter is the standard
approach — retry after increasing delays to avoid thundering herd. You should also
respect the Retry-After header and not retry 4xx errors other than 429.

--- History stored in memory ---
  [Human] What is rate limiting in LLM APIs?
  [AI] Rate limiting in LLM APIs restricts the number of requests per minute...
  [Human] What strategies exist for handling it?
  [AI] For handling rate limits, exponential backoff with jitter...

Turn 2 references rate limiting without the full question being repeated → memory is active.

============ DEMO 3 — Tool-calling agent ============
Tools: ['multiply', 'square_root']  |  Max iterations: 5

--- Task: What is 42 multiplied by 17, and what is the square root of the result? ---

> Entering new AgentExecutor chain...
Invoking: `multiply` with `{'a': 42.0, 'b': 17.0}`
714.0
Invoking: `square_root` with `{'n': 714.0}`
26.720778...

--- Intermediate steps ---
  Step 1: tool=multiply  args={'a': 42.0, 'b': 17.0}
         result=714.0
  Step 2: tool=square_root  args={'n': 714.0}
         result=26.720778...

[Final answer]
42 multiplied by 17 is 714. The square root of 714 is approximately 26.72.
```

---

## What to observe

- **LCEL chain composition in Demo 1**: the retrieval chain is assembled with `|` and
  invoked with a single string. No explicit loop, no manual output passing. Notice how
  `RunnablePassthrough()` routes the query to both the retriever and the prompt template
  simultaneously — this is parallel execution within a single `invoke` call.

- **Source attribution in Demo 1**: each retrieved chunk carries `metadata["source"]`
  showing which corpus file it came from. Queries about HNSW should retrieve exclusively
  from `vector-search.md`; queries about rate limiting from `llm-api-design.md`. If the
  wrong file appears, the embedding model's semantic similarity is not working correctly.

- **Memory continuity in Demo 2**: Turn 2's question — "What strategies exist for handling
  it?" — contains no subject. Without memory, the model would have no referent for "it".
  The response correctly interprets "it" as rate limiting because `history` in the prompt
  contains Turn 1's exchange.

- **Tool dispatch sequence in Demo 3**: the verbose `AgentExecutor` output shows each
  `Invoking:` line with the tool name and arguments. Confirm that `multiply` is called
  before `square_root`, and that `square_root` receives the result of `multiply` (714.0),
  not the original numbers.

---

## Concepts verified

- [ ] `LCEL` — observable as the `{...} | prompt | llm | parser` expression in Demo 1 producing correct answers
- [ ] `runnable` — observable as retriever, prompt, model, and parser all connected without adapter code
- [ ] `chain` — observable as a single `retrieval_chain.invoke("query")` call driving the full retrieval pipeline
- [ ] `LangChain memory` — observable as Turn 2 correctly answering about "it" (rate limiting) without the subject being repeated
- [ ] `LangChain agent` — observable as two sequential `Invoking:` log lines with correct arguments before the final answer

---

## Failure case

Active experiment: modify `main.py` at the marked `# FAILURE CASE` block and re-run.

- **What to change:** in `demo_session_memory()`, remove the `config=` argument from the
  `chain_with_memory.invoke()` call, so it becomes:
  ```python
  response = chain_with_memory.invoke({"question": question})
  ```
- **Expected degradation:**
  - The call raises a `ValueError` or `KeyError` about missing `session_id` in `configurable`
  - If the error is silent, Turn 2's response treats the question in isolation — "it" has no
    referent and the model either asks for clarification or answers generically
  - The history store is never updated, so the `History stored in memory` section shows 0 messages

Restore the `config=` argument after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| `ollama` | Serves the local LLM for chat completions and embeddings |
| OpenAI API | Alternative LLM provider when `LLM_PROVIDER=openai` |
