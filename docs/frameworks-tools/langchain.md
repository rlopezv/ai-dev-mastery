---
id: "frameworks-tools-langchain"
title: "LangChain"
type: "topic"
step: "frameworks-tools"
path: "docs/frameworks-tools/langchain.md"
status: "draft"
level: "intermediate"

concepts:
  - "LangChain"
  - "LCEL"
  - "chain"
  - "LangChain memory"
  - "LangChain agent"
  - "runnable"

prerequisites:
  - "ai-agents"
  - "docs/structured-outputs/tool-usage.md"

next:
  - "docs/frameworks-tools/llamaindex.md"

related:
  - "docs/ai-agents/single-agent-loop.md"
  - "docs/memory-context/conversation-history.md"
  - "docs/frameworks-tools/framework-comparison.md"

implementation_refs:
  - "labs/frameworks-tools/lab-langchain"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how LangChain's LCEL composability model, memory abstractions, and agent integration work and when to apply them."
---

## 1. Intuition

Think of LangChain as a connector system for LLM operations. A raw LLM call is a function
from input to output. LangChain treats every transformation — prompt formatting, model
calls, output parsing, retrieval steps, tool dispatch — as a composable unit with a
standard interface. You plug these units together with the `|` operator and get a pipeline
that handles data flow, error routing, and streaming without manual wiring.

The framework's central abstraction is the **Runnable** — any object with an `invoke`,
`stream`, and `batch` interface. LCEL (LangChain Expression Language) is the composition
syntax that connects Runnables into chains.

---

## 2. Explanation

### 2.1 Why

LLM application code is repetitive: construct a prompt, call the API, parse the response,
feed the result into the next step. When pipelines grow — adding retrieval, tool calls,
memory, and branching — this manual wiring becomes fragile. Each step couples to the
previous one through ad-hoc conventions, and changing one step requires understanding the
entire pipeline.

LangChain was designed to make this composition explicit. By standardizing the interface of
every transformation, it lets engineers connect steps declaratively and replace any step
without rewriting adjacent code. LCEL extends this with lazy evaluation, streaming
propagation, and parallel branch execution as first-class properties of the pipeline.

### 2.2 How

**Runnables** are the core primitive. A `ChatPromptTemplate`, a `ChatOpenAI` model, and a
`StrOutputParser` are all Runnables. LCEL chains them with `|`:

```text
prompt | model | parser
```

Each link passes its output as input to the next. LangChain handles the type conversions.

**Memory** integrates into a chain through a `RunnableWithMessageHistory` wrapper that
reads from and writes to a session-keyed history store before and after each model call.
The history store can be in-memory, Redis-backed, or any store that implements
`BaseChatMessageHistory`.

**Agents** in LangChain are chains where the model's output drives branching: if the model
returns a tool call, LangChain dispatches to the tool and feeds the result back to the
model; if the model returns a final answer, the chain terminates. The `AgentExecutor` loop
implements this stop condition.

**Retrieval chains** extend basic chains with a `Retriever` step that fetches documents
before the prompt is assembled. The retrieved documents are inserted into the prompt via
a context slot, implementing RAG within the chain abstraction.

### 2.3 Code example

```python
# See: labs/frameworks-tools/lab-langchain/main.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}")
])
model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

chain = prompt | model | parser
result = chain.invoke({"question": "What is LCEL?"})
```

---

## 3. Table

| Component | Role | Key interface |
|-----------|------|---------------|
| `ChatPromptTemplate` | Formats messages from variables | `invoke(dict) → messages` |
| `ChatOpenAI` / `ChatAnthropic` | Calls the LLM API | `invoke(messages) → AIMessage` |
| `StrOutputParser` | Extracts text from model response | `invoke(AIMessage) → str` |
| `RunnableWithMessageHistory` | Attaches session memory to any chain | wraps a Runnable |
| `AgentExecutor` | Runs the tool-use loop | `invoke(input) → final answer` |
| `Retriever` | Fetches relevant documents | `invoke(query) → list[Document]` |
| `RunnableParallel` | Executes multiple branches concurrently | `invoke(input) → dict` |

---

## 4. Engineering Implications

**LCEL adds observable latency overhead.** Each `|` boundary is a Python function call with
type-coercion logic. For single-call applications the overhead is negligible. For high-QPS
pipelines with many chained steps, measure before committing to LCEL.

**Memory scoping is the developer's responsibility.** `RunnableWithMessageHistory` stores
history by session ID but does not enforce context window limits. An unbounded history
grows until the model rejects the request. The application must implement trimming or
summarization explicitly — LangChain does not do this automatically.

**Agent loops are not deterministic.** LangChain's `AgentExecutor` runs until the model
emits a final answer or a `max_iterations` limit is reached. Without an explicit limit, a
model that repeatedly emits tool calls will spin. Always set `max_iterations`.

**LCEL is lazy by default.** Chains are not executed until `invoke`, `stream`, or `batch`
is called. This matters for logging and testing: print statements inside a chain definition
do not fire at definition time.

---

## 5. Implementation Connection

`lab-langchain` builds a complete LangChain application: an LCEL retrieval chain with
session memory and a tool-using agent. Key observations:

- How `RunnableWithMessageHistory` reads and writes history before and after each call
- How `AgentExecutor` dispatches tool calls and feeds results back to the model
- How `RunnableParallel` executes document retrieval and prompt formatting concurrently

Inspect the chain's `.input_schema` and `.output_schema` to understand how LangChain
infers types from the component composition.

---

## 6. Failure Modes and Limitations

**Abstraction opacity.** When a chain fails, the error may be several layers deep in
LangChain internals. Debugging requires understanding the Runnable protocol and inspecting
intermediate values with `.with_listeners()` or LangSmith tracing.

**Version instability.** LangChain has undergone multiple breaking API changes. Code
written for `langchain 0.0.x` does not run on `langchain 0.2.x` without modification.
Pin versions explicitly and test upgrades before applying them.

**Over-abstraction for simple tasks.** For a single-prompt, single-call application,
LangChain adds complexity with no benefit. The framework pays off when pipelines have
multiple steps, branching logic, or shared state that needs explicit management.

**Tool schema coupling.** LangChain's `Tool` abstraction wraps Python functions and infers
their schemas from docstrings. Schema drift between the docstring and the actual function
signature is not caught at definition time and causes silent errors at runtime.

---

## 7. Summary

LangChain makes LLM pipelines composable through the Runnable protocol and LCEL. Every
step — prompt, model, parser, retriever, tool dispatcher — shares the same interface,
so chains are built by connecting components with `|` rather than writing explicit plumbing
code. Memory, agents, and retrieval are first-class citizens of the chain abstraction.
The framework trades transparency for velocity: it accelerates multi-step pipeline
construction but adds debugging complexity and requires careful management of context limits
and agent termination conditions.
