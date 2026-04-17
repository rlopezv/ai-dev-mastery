# Lab: lab-langchain
# Module: frameworks-tools
# Doc reference: docs/frameworks-tools/langchain.md

import sys
import math
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import (
    LLM_PROVIDER, MODEL, OLLAMA_URL,
    build_llm, build_embeddings, load_corpus,
    assert_ollama_ready, assert_openai_key,
)
from shared.utils import print_separator, print_section, print_response, print_sources

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.agents import create_tool_calling_agent, AgentExecutor

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RETRIEVAL_K = 3
AGENT_MAX_ITERATIONS = 5

# ---------------------------------------------------------------------------
# Tool definitions for Demo 3
# ---------------------------------------------------------------------------

# Concept: tool declaration — @tool infers name and schema from the function signature
@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return the result."""
    return a * b


@tool
def square_root(n: float) -> float:
    """Return the square root of a number."""
    return math.sqrt(n)


MATH_TOOLS = [multiply, square_root]

# --------------------------------------------------
# FAILURE CASE — Demo 2: missing configurable key
# --------------------------------------------------
# Failure case:
# - In demo_session_memory(), remove the config= argument from chain_with_memory.invoke()
# - Observe:
#   * KeyError or validation error about missing 'session_id'
#   * RunnableWithMessageHistory cannot locate the history store without session_id
#   * Turn 2 has no knowledge of Turn 1 — memory is silently inactive
#   * This demonstrates that config={"configurable": {"session_id": "..."}} is
#     not optional — it is the only mechanism linking a call to its history store


# ---------------------------------------------------------------------------
# Demo 1: LCEL retrieval chain
# ---------------------------------------------------------------------------

def demo_retrieval_chain(llm, embeddings) -> None:
    print_separator("DEMO 1 — LCEL retrieval chain")
    print(f"Provider: {LLM_PROVIDER}  |  Model: {MODEL}")
    print(f"Chunk size: {CHUNK_SIZE}  |  Overlap: {CHUNK_OVERLAP}  |  top_k: {RETRIEVAL_K}")

    corpus = load_corpus()
    print(f"\nCorpus loaded: {len(corpus)} documents")
    for doc in corpus:
        print(f"  • {doc['source']}")

    # Concept: LCEL chain — split corpus into chunks and index them
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    texts, metadatas = [], []
    for doc in corpus:
        chunks = splitter.split_text(doc["text"])
        for chunk in chunks:
            texts.append(chunk)
            metadatas.append({"source": doc["source"]})
    print(f"\nChunks created: {len(texts)}")

    # Concept: runnable — InMemoryVectorStore implements the Retriever interface
    vectorstore = InMemoryVectorStore(embedding=embeddings)
    vectorstore.add_texts(texts, metadatas=metadatas)
    retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVAL_K})

    retrieval_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Answer the question using only the context provided below. "
            "If the answer is not in the context, say so.\n\n"
            "Context:\n{context}",
        ),
        ("human", "{question}"),
    ])

    def format_docs(docs: list) -> str:
        parts = []
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            parts.append(f"[{source}]\n{doc.page_content}")
        return "\n\n---\n\n".join(parts)

    # Concept: LCEL chain — compose retriever, prompt, model, parser with |
    retrieval_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | retrieval_prompt
        | llm
        | StrOutputParser()
    )

    queries = [
        "How does HNSW enable fast approximate nearest-neighbor search?",
        "What are the retry strategies for LLM API rate limiting?",
        "How does context isolation work in multi-agent systems?",
    ]

    for query in queries:
        print_section(f"Query: {query[:60]}")
        retrieved_docs = retriever.invoke(query)
        print_sources(retrieved_docs)
        answer = retrieval_chain.invoke(query)
        print_response("Answer", answer)


# ---------------------------------------------------------------------------
# Demo 2: session memory with RunnableWithMessageHistory
# ---------------------------------------------------------------------------

def demo_session_memory(llm) -> None:
    print_separator("DEMO 2 — Session memory")

    # Concept: LangChain memory — in-memory store keyed by session_id
    store: dict[str, InMemoryChatMessageHistory] = {}

    def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    memory_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a concise technical assistant. Answer in 2-3 sentences."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ])

    base_chain = memory_prompt | llm | StrOutputParser()

    # Concept: LangChain memory — RunnableWithMessageHistory wraps any chain
    chain_with_memory = RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history",
    )

    session_id = "session-demo-001"
    turns = [
        "What is rate limiting in LLM APIs?",
        "What strategies exist for handling it?",
    ]

    for i, question in enumerate(turns, 1):
        print_section(f"Turn {i} | session_id={session_id}")
        print(f"User: {question}")

        # Concept: LangChain memory — config= with session_id links the call to its store
        response = chain_with_memory.invoke(
            {"question": question},
            config={"configurable": {"session_id": session_id}},
        )
        print(f"Assistant: {response}")

    history = store[session_id].messages
    print_section("History stored in memory")
    for msg in history:
        role = msg.__class__.__name__.replace("Message", "")
        print(f"  [{role}] {str(msg.content)[:80]}")
    print(
        f"\nTurn 2 references rate limiting without the full question being repeated "
        f"→ memory is active."
    )


# ---------------------------------------------------------------------------
# Demo 3: tool-calling agent with AgentExecutor
# ---------------------------------------------------------------------------

def demo_tool_agent(llm) -> None:
    print_separator("DEMO 3 — Tool-calling agent")
    print(f"Tools: {[t.name for t in MATH_TOOLS]}  |  Max iterations: {AGENT_MAX_ITERATIONS}")

    agent_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a math assistant. Use the provided tools to compute answers. "
            "Show each calculation step.",
        ),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Concept: LangChain agent — create_tool_calling_agent builds the LCEL agent runnable
    agent = create_tool_calling_agent(llm, MATH_TOOLS, agent_prompt)

    # Concept: LangChain agent — AgentExecutor runs the tool-use loop with stop condition
    executor = AgentExecutor(
        agent=agent,
        tools=MATH_TOOLS,
        verbose=True,
        max_iterations=AGENT_MAX_ITERATIONS,
        return_intermediate_steps=True,
    )

    task = "What is 42 multiplied by 17, and what is the square root of the result?"
    print_section(f"Task: {task}")

    result = executor.invoke({"input": task})

    steps = result.get("intermediate_steps", [])
    print_section("Intermediate steps")
    for i, (action, observation) in enumerate(steps, 1):
        print(f"  Step {i}: tool={action.tool}  args={action.tool_input}")
        print(f"         result={observation}")

    print_response("Final answer", result["output"])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if LLM_PROVIDER == "ollama":
        assert_ollama_ready(models=[MODEL])
    else:
        assert_openai_key()

    llm = build_llm(temperature=0)
    embeddings = build_embeddings()

    demo_retrieval_chain(llm, embeddings)
    demo_session_memory(llm)
    demo_tool_agent(llm)
