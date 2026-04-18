# Shared: external memory store (episodic + semantic)
# Doc reference: docs/memory-context/external-memory.md

import time
import chromadb
from openai import OpenAI
from shared.config import CHROMA_PATH, embed


class MemoryStore:
    """
    ChromaDB-backed store for episodic and semantic memory.

    Concept: external memory — persists facts and conversation episodes outside
    the context window. Cross-session recall is possible because
    chromadb.PersistentClient() writes to disk.

    Two collections:
    - episodes: conversation turns stored as timestamped documents
    - facts: semantic key/value pairs (upserted by key)
    """

    def __init__(self, path: str = CHROMA_PATH) -> None:
        # Concept: PersistentClient — data written to disk, survives process exit
        self._client = chromadb.PersistentClient(path=path)
        self._episodes = self._client.get_or_create_collection("episodes")
        self._facts = self._client.get_or_create_collection("facts")

    # ------------------------------------------------------------------
    # Episodic memory
    # ------------------------------------------------------------------

    def add_episode(
        self,
        client: OpenAI,
        text: str,
        episode_id: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        """
        Concept: episodic memory — store a conversation turn with a timestamp.

        Returns the ID used to store the episode.
        """
        eid = episode_id or f"ep-{int(time.time() * 1000)}"
        embedding = embed(client, text)
        meta = {"timestamp": time.time()}
        if metadata:
            meta.update(metadata)
        self._episodes.add(
            documents=[text],
            embeddings=[embedding],
            ids=[eid],
            metadatas=[meta],
        )
        return eid

    def retrieve_episodes(
        self,
        client: OpenAI,
        query: str,
        n_results: int = 3,
    ) -> list[dict]:
        """
        Concept: retrieve from external memory — similarity search over episodes.

        Returns a list of dicts with 'text', 'id', 'distance', and 'metadata'.
        """
        query_embedding = embed(client, query)
        results = self._episodes.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )
        return [
            {
                "text": doc,
                "id": eid,
                "distance": dist,
                "metadata": meta,
            }
            for doc, eid, dist, meta in zip(
                results["documents"][0],
                results["ids"][0],
                results["distances"][0],
                results["metadatas"][0],
            )
        ]

    # ------------------------------------------------------------------
    # Semantic memory (key/value facts)
    # ------------------------------------------------------------------

    def upsert_fact(self, client: OpenAI, key: str, value: str) -> None:
        """
        Concept: semantic memory — store or update a named fact.

        Uses the key as the ChromaDB document ID so repeated calls update
        the same entry rather than creating duplicates.
        """
        text = f"{key}: {value}"
        embedding = embed(client, text)
        # upsert: add or overwrite by ID
        self._facts.upsert(
            documents=[text],
            embeddings=[embedding],
            ids=[key],
            metadatas=[{"key": key, "value": value, "timestamp": time.time()}],
        )

    def retrieve_facts(
        self,
        client: OpenAI,
        query: str,
        n_results: int = 3,
    ) -> list[dict]:
        """
        Retrieve semantic facts most similar to query.

        Returns a list of dicts with 'key', 'value', 'distance'.
        """
        query_embedding = embed(client, query)
        results = self._facts.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )
        return [
            {
                "key": meta.get("key", ""),
                "value": meta.get("value", ""),
                "distance": dist,
            }
            for meta, dist in zip(
                results["metadatas"][0],
                results["distances"][0],
            )
        ]

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def episode_count(self) -> int:
        return self._episodes.count()

    def fact_count(self) -> int:
        return self._facts.count()

    def format_for_injection(self, items: list[dict]) -> str:
        """
        Concept: inject retrieved memory — format retrieved items as a bullet list
        suitable for appending to a system prompt.
        """
        lines = []
        for item in items:
            if "value" in item:
                lines.append(f"- {item['key']}: {item['value']}")
            else:
                lines.append(f"- {item['text']}")
        return "\n".join(lines)
