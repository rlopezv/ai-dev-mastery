# Lab: lab-integration
# Module: frameworks-tools
# Doc reference: docs/frameworks-tools/architecture.md

import sys
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import (
    LLM_PROVIDER, MODEL, OLLAMA_URL,
    CHROMA_HOST, CHROMA_PORT, RESET_INDEX,
    OPENAI_API_KEY, OPENAI_MODEL,
    build_llm, build_embeddings, load_corpus,
    assert_ollama_ready, assert_openai_key,
)
from shared.utils import print_separator, print_section, print_response, print_sources

# LlamaIndex — index + retrieval layer
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore

# LangChain — orchestration layer
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.documents import Document as LCDocument

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INTEGRATION_COLLECTION = "frameworks-tools-integration"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
RETRIEVAL_K = 4

# ---------------------------------------------------------------------------
# LlamaIndex settings
# ---------------------------------------------------------------------------

def configure_llamaindex() -> None:
    if LLM_PROVIDER == "openai":
        from llama_index.llms.openai import OpenAI
        from llama_index.embeddings.openai import OpenAIEmbedding
        Settings.llm = OpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0)
        Settings.embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY)
    else:
        from llama_index.llms.ollama import Ollama
        from llama_index.embeddings.ollama import OllamaEmbedding
        Settings.llm = Ollama(model=MODEL, base_url=OLLAMA_URL, temperature=0)
        Settings.embed_model = OllamaEmbedding(model_name=MODEL, base_url=OLLAMA_URL)
    Settings.chunk_size = CHUNK_SIZE
    Settings.chunk_overlap = CHUNK_OVERLAP


# ---------------------------------------------------------------------------
# Build or reload LlamaIndex index
# ---------------------------------------------------------------------------

def get_llamaindex_retriever(chroma_client: chromadb.HttpClient):
    """Return a LlamaIndex retriever backed by ChromaDB."""
    collection = chroma_client.get_or_create_collection(INTEGRATION_COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    if RESET_INDEX or collection.count() == 0:
        print("Building LlamaIndex index from corpus...")
        corpus = load_corpus()
        documents = [
            Document(text=doc["text"], metadata={"source": doc["source"]})
            for doc in corpus
        ]
        parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        nodes = parser.get_nodes_from_documents(documents)
        print(f"  Nodes created: {len(nodes)}")
        index = VectorStoreIndex(nodes, storage_context=storage_context)
        print(f"  Index persisted to collection '{INTEGRATION_COLLECTION}'")
    else:
        print(f"Reloading LlamaIndex index from ChromaDB ({collection.count()} vectors)...")
        index = VectorStoreIndex.from_vector_store(
            vector_store, storage_context=storage_context
        )

    # Concept: retriever — LlamaIndex retriever returns nodes with metadata
    return index.as_retriever(similarity_top_k=RETRIEVAL_K)


# ---------------------------------------------------------------------------
# LangChain-compatible retriever wrapper
# ---------------------------------------------------------------------------

def make_langchain_retriever(llamaindex_retriever):
    """
    Wrap a LlamaIndex retriever so it behaves as a LangChain Retriever.
    Returns a callable: str -> list[LCDocument].
    """
    def retrieve(query: str) -> list[LCDocument]:
        # Concept: pipeline composition — LlamaIndex nodes converted to LangChain Documents
        nodes = llamaindex_retriever.retrieve(query)
        docs = []
        for node in nodes:
            docs.append(LCDocument(
                page_content=node.get_content(),
                metadata={
                    "source": node.metadata.get("source", "unknown"),
                    "score": node.score or 0.0,
                },
            ))
        return docs

    return retrieve


# ---------------------------------------------------------------------------
# Demo 1: LangChain chain with LlamaIndex retriever
# ---------------------------------------------------------------------------

def demo_integrated_pipeline(llm, llamaindex_retriever) -> None:
    print_separator("DEMO 1 — LangChain chain + LlamaIndex retriever")

    lc_retriever = make_langchain_retriever(llamaindex_retriever)

    def format_docs(docs: list) -> str:
        parts = []
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            score = doc.metadata.get("score", 0.0)
            parts.append(f"[{source} | score={score:.3f}]\n{doc.page_content}")
        return "\n\n---\n\n".join(parts)

    retrieval_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Answer using only the context below. State which document each claim "
            "comes from.\n\nContext:\n{context}",
        ),
        ("human", "{question}"),
    ])

    # Concept: pipeline composition — LlamaIndex retriever plugged into a LangChain chain
    retrieval_chain = (
        {
            "context": lambda q: format_docs(lc_retriever(q)),
            "question": lambda q: q,
        }
        | retrieval_prompt
        | llm
        | StrOutputParser()
    )

    queries = [
        "How does HNSW achieve fast approximate nearest-neighbor search?",
        "What coordination patterns exist for multi-agent systems?",
        "What retry strategy should I use for LLM API rate limits?",
    ]

    for query in queries:
        print_section(f"Query: {query[:65]}")
        retrieved = lc_retriever(query)
        print_sources(retrieved)
        answer = retrieval_chain.invoke(query)
        print_response("Answer", answer)


# ---------------------------------------------------------------------------
# Demo 2: add session memory on top of the integrated pipeline
# ---------------------------------------------------------------------------

def demo_memory_pipeline(llm, llamaindex_retriever) -> None:
    print_separator("DEMO 2 — Integrated pipeline with session memory")

    lc_retriever = make_langchain_retriever(llamaindex_retriever)

    def format_docs(docs: list) -> str:
        return "\n\n".join(
            f"[{d.metadata.get('source','?')}]\n{d.page_content}" for d in docs
        )

    rag_memory_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Answer using only the provided context. Keep prior conversation in mind.\n\n"
            "Context:\n{context}",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ])

    base_chain = (
        {
            "context": lambda d: format_docs(lc_retriever(d["question"])),
            "question": lambda d: d["question"],
            "history": lambda d: d["history"],
        }
        | rag_memory_prompt
        | llm
        | StrOutputParser()
    )

    store: dict[str, InMemoryChatMessageHistory] = {}

    def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    # Concept: pipeline composition — memory wrapper added to a retrieval chain
    chain_with_memory = RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history",
    )

    session_id = "integration-session-001"
    turns = [
        "What is the HNSW algorithm used for?",
        "What parameters control its performance?",
    ]

    for i, question in enumerate(turns, 1):
        print_section(f"Turn {i} | session_id={session_id}")
        print(f"User: {question}")
        response = chain_with_memory.invoke(
            {"question": question},
            config={"configurable": {"session_id": session_id}},
        )
        print(f"Assistant: {response}")

    # --------------------------------------------------
    # FAILURE CASE
    # --------------------------------------------------
    # Failure case:
    # - Change INTEGRATION_COLLECTION = "frameworks-tools-integration" to a new name
    #   (e.g., "test-collection") and set RESET_INDEX=false, then run
    # - Observe:
    #   * A new empty collection is created; LlamaIndex builds no index
    #   * VectorStoreIndex.from_vector_store returns an empty index
    #   * All queries return 0 nodes; the retrieval chain answers from model knowledge only
    #   * Responses no longer cite specific source files
    #   * This demonstrates that the embedding model + collection name pair must be consistent


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if LLM_PROVIDER == "ollama":
        assert_ollama_ready(models=[MODEL])
    else:
        assert_openai_key()

    configure_llamaindex()

    print_separator("SETUP")
    print(f"Provider: {LLM_PROVIDER}  |  Model: {MODEL}")
    print(f"ChromaDB: {CHROMA_HOST}:{CHROMA_PORT}  |  top_k: {RETRIEVAL_K}")

    try:
        chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        chroma_client.heartbeat()
    except Exception as e:
        raise RuntimeError(
            f"ChromaDB not reachable at {CHROMA_HOST}:{CHROMA_PORT}: {e}\n"
            "Start it with: docker-compose --profile full up -d"
        ) from e

    llm = build_llm(temperature=0)
    llamaindex_retriever = get_llamaindex_retriever(chroma_client)

    demo_integrated_pipeline(llm, llamaindex_retriever)
    demo_memory_pipeline(llm, llamaindex_retriever)
