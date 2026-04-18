---
id: "rag-rag-fundamentals"
title: "RAG Fundamentals"
type: "topic"
step: "rag"
path: "docs/rag/rag-fundamentals.md"
status: "draft"
level: "intermediate"

concepts:
  - "retrieval-augmented-generation"
  - "parametric-memory"
  - "non-parametric-memory"
  - "knowledge-grounding"
  - "hallucination"

prerequisites:
  - "docs/structured-outputs/README.md"
  - "docs/llm-fundamentals/llm-architecture.md"

next:
  - "docs/rag/embeddings-and-vector-search.md"

related:
  - "docs/rag/context-assembly.md"
  - "docs/memory-context/README.md"

implementation_refs: []

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains what Retrieval-Augmented Generation is, why it exists, and how it decouples knowledge from model weights to enable grounded generation from external sources."
---

# RAG Fundamentals

## Navigation

[Docs](../README.md) / [Retrieval-Augmented Generation](README.md) / RAG Fundamentals

---

## 1. Intuition

A language model's knowledge is frozen at training time. Ask it about last quarter's earnings report or your company's internal API, and it cannot answer — those facts were never in its training data. One solution is retraining the model, but that is expensive, slow, and has to be repeated every time the knowledge changes.

RAG takes a different approach: instead of teaching the model new facts, bring the facts to the model at query time. Before generating a response, the application retrieves the relevant documents from an external store and includes them in the prompt. The model reasons over the provided content rather than trying to recall facts it may never have learned.

---

## 2. Explanation

### 2.1 Why

Language models store knowledge in two ways:

**Parametric memory** — facts and patterns encoded in model weights during training. These are always available but static: they do not change unless the model is retrained or fine-tuned.

**Non-parametric memory** — content provided at inference time in the prompt's context window. This content is transient: it exists only for the duration of a single call and must be re-supplied on every request.

RAG exploits non-parametric memory deliberately. By retrieving relevant documents and placing them in the context window, the application converts an open-domain knowledge problem into a reading-comprehension problem. The model does not need to recall the answer — it needs to extract or synthesize it from the text it has been given.

This design decision has two important consequences:

1. **Knowledge can be updated without retraining.** Updating the document store immediately changes what the model can say.
2. **Answers can be traced back to sources.** Because the model reasons from retrieved content, citations are possible and answers are auditable.

### 2.2 How

The RAG pipeline has two phases:

**Indexing phase** (offline, run once per corpus or on update):
1. Load source documents — PDFs, web pages, database records, code files.
2. Chunk documents into segments sized for retrieval (see `document-processing-and-chunking.md`).
3. Encode each chunk with an embedding model to produce a dense vector.
4. Store vectors in a vector database alongside the original chunk text.

**Query phase** (online, run on each user request):
1. Encode the user's query with the same embedding model.
2. Search the vector index for the top-k chunks most similar to the query.
3. Assemble the retrieved chunks into a context block (see `context-assembly.md`).
4. Construct a prompt with the context block and the original query.
5. Call the LLM and return the grounded response.

### 2.3 Code example

```python
# See: labs/rag/lab-query-pipeline/main.py
# Minimal RAG query phase — assumes index already built

def rag_query(query: str, retriever, llm_client, top_k: int = 5) -> str:
    # Step 1: retrieve
    chunks = retriever.retrieve(query, top_k=top_k)

    # Step 2: assemble context
    context = "\n\n".join(f"[{i+1}] {c.text}" for i, c in enumerate(chunks))

    # Step 3: generate
    messages = [
        {"role": "system", "content": "Answer based only on the provided context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
    ]
    response = llm_client.chat.completions.create(
        model="llama3.2", messages=messages
    )
    return response.choices[0].message.content
```

---

## 3. Table

| Approach | Knowledge source | Update cost | Traceability | Use case |
|----------|-----------------|-------------|--------------|----------|
| Parametric only | Model weights | Full retrain | None | General knowledge, stable facts |
| Fine-tuning | Weights + task data | Expensive, periodic | None | Domain style adaptation |
| RAG | External document store | Document update only | Full (source chunks) | Dynamic, private, or large corpora |
| RAG + fine-tuning | Both | Both costs | Partial | High-frequency domain with style requirements |

| RAG pipeline phase | Input | Output |
|-------------------|-------|--------|
| Indexing — chunking | Raw document | Chunks |
| Indexing — embedding | Chunks | Chunk vectors |
| Query — embedding | User query | Query vector |
| Query — retrieval | Query vector + index | Top-k chunks |
| Query — assembly | Chunks + budget | Context block |
| Query — generation | Prompt + context | Grounded response |

---

## 4. Engineering Implications

**RAG changes where failures occur.** A pure LLM system fails when the model doesn't know an answer or hallucinates. A RAG system can fail at retrieval (wrong chunks returned), at assembly (relevant chunks dropped due to token budget), or at generation (model ignores the retrieved content). Each failure mode requires different tooling to detect and fix.

**Retrieval quality is the bottleneck.** If the retrieval step returns irrelevant chunks, the generation step cannot compensate — there is no correct information in the context to reason from. Improving prompt engineering on the generation side provides no benefit when retrieval is broken.

**Token budget constrains context.** A context window is finite. When many chunks are retrieved, some must be dropped. Dropping the wrong chunks produces incorrect or incomplete answers even when the correct information exists in the store. Context assembly is an active engineering problem, not a formatting step.

**The embedding model must match at index and query time.** Vectors produced by different models are not comparable. Switching the embedding model requires rebuilding the entire index.

**Cost scales with index size and query volume.** Each query requires one embedding call and one vector search. At scale, embedding API costs and vector database query throughput become operational constraints.

---

## 5. Implementation Connection

RAG fundamentals have no dedicated lab — the concept is developed incrementally across the labs for embeddings, chunking, retrieval, and context assembly. The conceptual picture assembled here maps directly to the full pipeline built in `lab-query-pipeline`, where indexing and query phases are implemented end-to-end.

When reading the subsequent topics, refer back to the two-phase model in section 2.2 to anchor each topic's role in the overall pipeline.

---

## 6. Failure Modes and Limitations

**Retrieval-generation mismatch.** A model may produce an answer that contradicts the retrieved content — not because retrieval failed, but because the model's parametric memory overrides what it has been given. This is especially common for facts the model has seen frequently in training. Mitigation: instruct the model explicitly to answer only from the provided context.

**Out-of-scope queries.** If the user's query requires knowledge that is not in the document store, RAG cannot answer correctly — the model will either generate from parametric memory (potentially hallucinating) or correctly state that no relevant information was found. The pipeline must handle both outcomes.

**Chunk boundary loss.** Chunking splits documents at arbitrary points. A fact that spans two chunks may be retrieved in incomplete form, producing an answer that is partially wrong. Overlap-aware chunking and sliding-window strategies mitigate this at the cost of index size.

**Index staleness.** Documents updated in the source system are not reflected in the index until the corresponding chunks are re-embedded and re-inserted. Long-lived indexes drift from the source of truth unless an update pipeline is maintained.

**Embedding model capability ceiling.** The embedding model determines how well semantic similarity reflects query relevance. A weak embedding model produces poor rankings regardless of how well the rest of the pipeline is engineered.

---

## 7. Summary

RAG decouples knowledge from model weights by retrieving relevant documents at query time and placing them in the context window. The pattern converts a recall problem into a reading-comprehension problem: the model reasons from provided text rather than from parametric memory. The pipeline has two phases — indexing (offline) and querying (online) — and its failure modes are distinct from those of pure generation. Retrieval quality is the dominant constraint: downstream generation cannot recover from retrieval failures.
