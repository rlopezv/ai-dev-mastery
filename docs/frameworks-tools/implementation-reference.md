---
id: "frameworks-tools-implementation-reference"
title: "Frameworks and Tools — Implementation Reference"
type: "implementation-reference"
step: "frameworks-tools"
path: "docs/frameworks-tools/implementation-reference.md"
status: "draft"
level: "intermediate"

concepts:
  - "LangChain"
  - "LlamaIndex"
  - "AutoGen"
  - "Semantic Kernel"
  - "pipeline composition"
  - "framework abstraction"

prerequisites:
  - "docs/frameworks-tools/architecture.md"

next:
  - "docs/frameworks-tools/validation.md"

related:
  - "docs/frameworks-tools/langchain.md"
  - "docs/frameworks-tools/llamaindex.md"
  - "docs/frameworks-tools/autogen.md"
  - "docs/frameworks-tools/semantic-kernel.md"

implementation_refs:
  - "labs/frameworks-tools/lab-langchain"
  - "labs/frameworks-tools/lab-llamaindex"
  - "labs/frameworks-tools/lab-autogen"
  - "labs/frameworks-tools/lab-semantic-kernel"
  - "labs/frameworks-tools/lab-integration"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how architecture components translate into implementation patterns across LangChain, LlamaIndex, AutoGen, and Semantic Kernel."
---

## 1. Implementation Overview

> **Note:** This document contains orientative code — structures, interfaces, signatures.
> It is not directly executable. For complete, runnable implementations see the labs
> referenced in `implementation_refs`.

Each framework maps a distinct set of concepts to concrete Python interfaces. The
architecture document describes what these frameworks do at system level; this document
explains why the code is structured the way it is in each lab — the design decisions behind
the interface choices, not the setup steps.

The four frameworks share the same infrastructure layer (LLM APIs, vector stores, embedding
models) but access it through fundamentally different abstractions. Understanding why each
abstraction exists is more valuable than memorizing its API.

---

## 2. Core Patterns

| Pattern | Description | When to use |
|---------|-------------|-------------|
| LCEL composition | Connect Runnables with `\|` to form a pipeline | Multi-step pipelines with shared input schema |
| Memory injection | Wrap a chain with `RunnableWithMessageHistory` | Sessions that require conversation continuity |
| Index-and-query separation | Build index once; query engine operates on it | Corpora that are indexed infrequently but queried often |
| Agent executor loop | Wrap a tool-calling model in `AgentExecutor` | Single-agent tasks with tool dispatch |
| Conversation loop | Use `initiate_chat` between ConversableAgents | Multi-agent tasks with structured dialogue |
| Plugin registration | Decorate methods with `@kernel_function` | Enterprise integration with versioned prompts |
| Planner-as-router | Use `FunctionChoiceBehavior` to select functions | Tasks where the execution path is not known at design time |

---

## 3. Component Mapping

| Architecture Component | Implementation |
|------------------------|----------------|
| LangChain chain | `ChatPromptTemplate \| ChatOpenAI \| StrOutputParser` |
| LangChain memory | `RunnableWithMessageHistory(chain, get_session_history)` |
| LangChain agent | `AgentExecutor(agent=create_tool_calling_agent(...), tools=[...])` |
| LlamaIndex ingestion | `SimpleDirectoryReader → SentenceSplitter → VectorStoreIndex.from_documents` |
| LlamaIndex retrieval | `VectorStoreIndex.as_retriever(similarity_top_k=k)` |
| LlamaIndex synthesis | `VectorStoreIndex.as_query_engine(response_mode="compact")` |
| AutoGen two-agent | `UserProxyAgent.initiate_chat(AssistantAgent, message)` |
| AutoGen GroupChat | `GroupChat(agents=[...]) → GroupChatManager → UserProxyAgent.initiate_chat` |
| SK kernel | `Kernel() → add_service(OpenAIChatCompletion) → add_plugin(plugin_instance)` |
| SK planner | `settings = OpenAIChatPromptExecutionSettings(tool_choice="auto")` |

---

## 4. Data Structures and Interfaces

### LangChain: chain input and output schema

```python
# Orientative — see labs/frameworks-tools/lab-langchain/main.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory

# A chain's input schema is derived from the prompt template's input variables.
# Output schema is the return type of the final Runnable in the chain.
chain = prompt | model | parser          # output: str
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,                  # callable: session_id → BaseChatMessageHistory
    input_messages_key="question",
    history_messages_key="history",
)
# invoke requires the configurable session_id
chain_with_history.invoke(
    {"question": "..."},
    config={"configurable": {"session_id": "user-123"}}
)
```

### LlamaIndex: index construction and query

```python
# Orientative — see labs/frameworks-tools/lab-llamaindex/main.py
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

# Index is built once and persisted; query engine is created from the persisted index.
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

# Later, reload without re-ingesting
index = VectorStoreIndex.from_vector_store(vector_store)
query_engine = index.as_query_engine(similarity_top_k=3)
response = query_engine.query("...")   # Response object with source_nodes
```

### AutoGen: agent configuration

```python
# Orientative — see labs/frameworks-tools/lab-autogen/main.py
import autogen

llm_config = {
    "model": "gpt-4o-mini",
    "functions": [              # tool definitions follow OpenAI function format
        {
            "name": "search_docs",
            "description": "Search the document corpus",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        }
    ],
}
# function_map connects tool names to Python callables
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    function_map={"search_docs": search_docs_function},
)
```

### Semantic Kernel: plugin and invocation

```python
# Orientative — see labs/frameworks-tools/lab-semantic-kernel/main.py
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings

class DocumentPlugin:
    @kernel_function(
        name="summarize",
        description="Summarizes the provided text in three bullet points"
    )
    async def summarize(self, text: str) -> str:
        # implementation — SK handles calling this via the planner
        ...

# Register and invoke
kernel.add_plugin(DocumentPlugin(), plugin_name="Documents")
settings = OpenAIChatPromptExecutionSettings(tool_choice="auto")
result = await kernel.invoke_prompt("Summarize this: {{$text}}", text="...", settings=settings)
```

---

## 5. Design Decisions

**LangChain: LCEL over legacy chain classes.** The older `LLMChain`, `ConversationChain`,
and `RetrievalQA` classes are deprecated. LCEL is the current composition model. The labs
use LCEL exclusively to reflect the production-current API and to make the data flow
explicit through the `|` composition syntax.

**LlamaIndex: index-query separation.** The labs separate index construction from query
engine creation. This reflects a production pattern where indexing happens in a background
job and query execution happens in a request handler. Building and querying the index in
the same function obscures this separation and produces misleading performance
measurements.

**AutoGen: NEVER human input mode for lab automation.** `human_input_mode="NEVER"` allows
labs to run without interactive input. This is not the production default — production
systems that require human oversight should set `"TERMINATE"` or `"ALWAYS"` as appropriate.
The lab configuration exists to make the automation testable.

**Semantic Kernel: async throughout.** All SK invocations are coroutines. Lab entry points
use `asyncio.run(main())` to manage the event loop explicitly. This makes the async
boundary visible and avoids implicit event loop management that behaves differently across
frameworks.

---

## 6. External Dependencies

| Tool | Role | Infrastructure profile |
|------|------|------------------------|
| OpenAI API | LLM for LangChain, AutoGen, Semantic Kernel | `light` |
| Ollama | Local LLM alternative | `light` |
| ChromaDB | Vector store for LlamaIndex | `full` |
| LangChain (`langchain`, `langchain-openai`) | Orchestration framework | `light` |
| LlamaIndex (`llama-index-core`, `llama-index-vector-stores-chroma`) | Retrieval framework | `full` |
| AutoGen (`pyautogen`) | Multi-agent framework | `light` |
| Semantic Kernel (`semantic-kernel`) | Enterprise integration framework | `light` |

---

## 7. Mapping to Labs (MANDATORY)

| Pattern / Component | Lab | Concept verified |
|---------------------|-----|-----------------|
| LCEL chain with retriever and memory | `lab-langchain` | Runnable composition, session history |
| LlamaIndex ingestion and VectorStoreIndex | `lab-llamaindex` | Node creation, index persistence, query engine |
| AutoGen two-agent conversation | `lab-autogen` | initiate_chat loop, tool execution via proxy |
| Semantic Kernel plugins and planner | `lab-semantic-kernel` | Plugin registration, FunctionChoiceBehavior |
| LangChain + LlamaIndex combined pipeline | `lab-integration` | Cross-framework interface, end-to-end data flow |

---

## 8. Trade-offs and Constraints

**Framework version lock-in vs. dependency hygiene.** Pinning framework versions ensures
reproducibility but delays access to bug fixes and new model support. Unpinned versions
break silently on minor updates. The right approach is explicit version pinning with a
documented upgrade policy.

**LCEL streaming vs. synchronous chains.** LCEL propagates streaming automatically when
all components support it. A single non-streaming component in the chain (e.g., a custom
postprocessor that returns a string) breaks streaming propagation. Design for streaming
from the start or accept synchronous response delivery.

**LlamaIndex response modes.** `compact` minimizes tokens by fitting as many nodes as
possible into a single LLM call. `refine` issues one LLM call per retrieved node and
accumulates the answer iteratively — higher quality for long documents, higher cost.
`tree_summarize` builds a summary tree for very long corpora. Choose based on corpus
size and cost tolerance.

**AutoGen context growth vs. turn limits.** Setting `max_turns` too low terminates the
conversation before the task is complete. Setting it too high allows the transcript to
grow beyond the model's context window. Tune `max_turns` empirically for each task type
and monitor transcript length.

---

## 9. Failure Modes

**LangChain: missing `configurable` in `invoke`.** `RunnableWithMessageHistory` requires
the `config` parameter with a `session_id` key on every invocation. Omitting it raises a
`KeyError` inside the history lookup. This is a common error when refactoring chains that
did not originally have memory.

**LlamaIndex: embedding model mismatch at query time.** If the index was built with one
embedding model and queried with another, retrieval returns semantically random results.
Store the embedding model identifier in index metadata and validate it before querying.

**AutoGen: function not found in `function_map`.** When the assistant emits a tool call
for a function not registered in `function_map`, the proxy sends an error message back to
the assistant. The assistant may retry, loop, or hallucinate a substitute. Register all
tool names before calling `initiate_chat`.

**Semantic Kernel: unresolved template variables.** A prompt template that references a
variable not provided in the invocation arguments resolves to an empty string without
raising an error. This produces silent, semantically empty prompt slots. Validate all
template variables at invocation time.

---

## 10. Summary

LangChain implements orchestration through the Runnable protocol and LCEL composition.
LlamaIndex implements retrieval through the index-query separation pattern with persistent
storage. AutoGen implements multi-agent coordination through the conversation loop with
explicit tool dispatch. Semantic Kernel implements enterprise integration through the
plugin registry and planner model. The design decisions behind each implementation reflect
the framework's primary abstraction: chainability for LangChain, data structure for
LlamaIndex, dialogue for AutoGen, service registry for Semantic Kernel.
