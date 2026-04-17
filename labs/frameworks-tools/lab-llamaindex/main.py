# Lab: lab-llamaindex
# Module: frameworks-tools
# Doc reference: docs/frameworks-tools/llamaindex.md

import sys
import time
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import (
    LLM_PROVIDER, MODEL, OLLAMA_URL,
    CHROMA_HOST, CHROMA_PORT, RESET_INDEX,
    OPENAI_API_KEY, OPENAI_MODEL,
    load_corpus, assert_ollama_ready, assert_openai_key,
)
from shared.utils import print_separator, print_section, print_response

import chromadb
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Settings,
    Document,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COLLECTION_NAME = "frameworks-tools-corpus"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

# top_k values for the comparison demo
TOP_K_LOW = 1
TOP_K_HIGH = 5


# ---------------------------------------------------------------------------
# LlamaIndex settings (LLM + embedding model)
# ---------------------------------------------------------------------------

def configure_settings() -> None:
    """Set global LlamaIndex Settings for LLM and embed model."""
    if LLM_PROVIDER == "openai":
        from llama_index.llms.openai import OpenAI
        from llama_index.embeddings.openai import OpenAIEmbedding
        Settings.llm = OpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0)
        Settings.embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY)
    else:
        from llama_index.llms.ollama import Ollama
        from llama_index.embeddings.ollama import OllamaEmbedding
        Settings.llm = Ollama(model=MODEL, base_url=OLLAMA_URL, temperature=0)
        # Concept: embedding model — must be consistent between index build and query time
        Settings.embed_model = OllamaEmbedding(model_name=MODEL, base_url=OLLAMA_URL)

    Settings.chunk_size = CHUNK_SIZE
    Settings.chunk_overlap = CHUNK_OVERLAP


# ---------------------------------------------------------------------------
# ChromaDB client
# ---------------------------------------------------------------------------

def get_chroma_client() -> chromadb.HttpClient:
    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        client.heartbeat()
        return client
    except Exception as e:
        raise RuntimeError(
            f"ChromaDB not reachable at {CHROMA_HOST}:{CHROMA_PORT}: {e}\n"
            "Start it with: docker-compose --profile full up -d"
        ) from e


# ---------------------------------------------------------------------------
# Demo 1: index construction from corpus
# ---------------------------------------------------------------------------

def build_index(chroma_client: chromadb.HttpClient) -> VectorStoreIndex:
    corpus = load_corpus()
    print(f"\nCorpus loaded: {len(corpus)} documents")
    for doc in corpus:
        print(f"  • {doc['source']}")

    # Concept: node — LlamaIndex Document wraps raw text with metadata
    documents = [
        Document(text=doc["text"], metadata={"source": doc["source"]})
        for doc in corpus
    ]

    # Concept: node parser — SentenceSplitter chunks documents into nodes
    parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    nodes = parser.get_nodes_from_documents(documents)
    print(f"Nodes created: {len(nodes)}")
    for node in nodes[:3]:
        source = node.metadata.get("source", "unknown")
        print(f"  Node sample [{source}]: {node.get_content()[:80]}...")

    # Concept: index — VectorStoreIndex stores nodes in ChromaDB for persistence
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    t0 = time.time()
    index = VectorStoreIndex(nodes, storage_context=storage_context)
    build_time = time.time() - t0

    print(f"\nIndex built and persisted to ChromaDB in {build_time:.2f}s")
    print(f"Collection: '{COLLECTION_NAME}'  |  Vectors stored: {collection.count()}")
    return index


def load_index(chroma_client: chromadb.HttpClient) -> VectorStoreIndex:
    """Reload the index from ChromaDB without re-ingesting documents."""
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    t0 = time.time()
    # Concept: index — reloaded from the vector store; no re-embedding needed
    index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )
    reload_time = time.time() - t0
    print(f"Loaded index from ChromaDB in {reload_time:.3f}s (no re-ingestion)")
    return index


# ---------------------------------------------------------------------------
# Demo 2: query engine with configurable top_k
# ---------------------------------------------------------------------------

def demo_query_engine(index: VectorStoreIndex) -> None:
    print_separator("DEMO 2 — Query engine with configurable top_k")

    query = "How does HNSW enable fast approximate nearest-neighbor search?"
    print(f"Query: {query}\n")

    for top_k in [TOP_K_LOW, TOP_K_HIGH]:
        print_section(f"top_k = {top_k}")

        # Concept: query engine — wraps retriever + synthesizer; top_k controls recall
        query_engine = index.as_query_engine(similarity_top_k=top_k)
        t0 = time.time()
        response = query_engine.query(query)
        elapsed = time.time() - t0

        print(f"Nodes retrieved: {len(response.source_nodes)}  |  Time: {elapsed:.2f}s")
        for i, node in enumerate(response.source_nodes, 1):
            source = node.metadata.get("source", "unknown")
            score = node.score or 0.0
            snippet = node.get_content()[:100].replace("\n", " ")
            print(f"  {i}. [{source}]  score={score:.3f}  — {snippet}...")
        print_response(f"Answer (top_k={top_k})", str(response))

    # --------------------------------------------------
    # FAILURE CASE
    # --------------------------------------------------
    # Failure case:
    # - Replace the Settings.embed_model assignment in configure_settings() with:
    #   Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url=OLLAMA_URL)
    #   (only if 'nomic-embed-text' is NOT pulled in Ollama — to simulate a mismatch)
    # - Rebuild the index (set RESET_INDEX=true), then reload with the original model
    # - Observe:
    #   * Retrieval returns semantically random nodes — wrong files surfaced for the query
    #   * Similarity scores are near 0.0 or uniformly distributed, not ranked
    #   * Responses become incoherent because the retrieved context is irrelevant
    #   * This demonstrates that the embedding model must be identical at build and query time


# ---------------------------------------------------------------------------
# Demo 3: direct retriever (without synthesis)
# ---------------------------------------------------------------------------

def demo_retriever(index: VectorStoreIndex) -> None:
    print_separator("DEMO 3 — Direct retriever")
    print("Retrieves nodes without LLM synthesis — faster, lower cost.\n")

    # Concept: retriever — decoupled from query engine; returns raw nodes with scores
    retriever = index.as_retriever(similarity_top_k=3)

    queries = [
        "What are the retry strategies for LLM API rate limiting?",
        "How does context isolation work in multi-agent orchestrator patterns?",
    ]

    for query in queries:
        print_section(f"Query: {query[:65]}")
        nodes = retriever.retrieve(query)
        for i, node in enumerate(nodes, 1):
            source = node.metadata.get("source", "unknown")
            score = node.score or 0.0
            snippet = node.get_content()[:120].replace("\n", " ")
            print(f"  {i}. score={score:.3f}  [{source}]")
            print(f"     {snippet}...")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if LLM_PROVIDER == "ollama":
        assert_ollama_ready(models=[MODEL])
    else:
        assert_openai_key()

    configure_settings()
    chroma_client = get_chroma_client()

    # Demo 1 — build or reload index
    print_separator("DEMO 1 — Index construction and reload")
    print(f"Provider: {LLM_PROVIDER}  |  Model: {MODEL}")
    print(f"ChromaDB: {CHROMA_HOST}:{CHROMA_PORT}  |  Collection: {COLLECTION_NAME}")
    print(f"Chunk size: {CHUNK_SIZE}  |  Overlap: {CHUNK_OVERLAP}")

    existing_count = chroma_client.get_or_create_collection(COLLECTION_NAME).count()

    if RESET_INDEX or existing_count == 0:
        if RESET_INDEX:
            print("\nRESET_INDEX=true — deleting existing collection...")
            try:
                chroma_client.delete_collection(COLLECTION_NAME)
            except Exception:
                pass
        print("\nBuilding index from corpus...")
        index = build_index(chroma_client)
    else:
        print(f"\nExisting index found ({existing_count} vectors). Reloading...")
        index = load_index(chroma_client)

    demo_query_engine(index)
    demo_retriever(index)
