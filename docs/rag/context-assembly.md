---
id: "rag-context-assembly"
title: "Context Assembly"
type: "topic"
step: "rag"
path: "docs/rag/context-assembly.md"
status: "draft"
level: "intermediate"

concepts:
  - "context-assembly"
  - "token-budget"
  - "chunk-deduplication"
  - "lost-in-the-middle"
  - "prompt-context-block"

prerequisites:
  - "docs/rag/retrieval-strategies.md"
  - "docs/rag/document-processing-and-chunking.md"

next:
  - "docs/rag/rag-evaluation-and-metrics.md"

related:
  - "docs/llm-fundamentals/context-window.md"
  - "docs/memory-context/context-management.md"

implementation_refs:
  - "labs/rag/lab-query-pipeline"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how retrieved chunks are selected, deduplicated, ordered, and assembled into a context block that fits within the model's token budget, and how ordering and framing affect generation quality."
---

# Context Assembly

## Navigation

[Docs](../README.md) / [Retrieval-Augmented Generation](README.md) / Context Assembly

---

## 1. Intuition

Retrieval hands back a ranked list of text chunks. Generation expects a single prompt. Between them lies context assembly: the step that decides which chunks make the cut, in what order they appear, and how they are framed within the prompt.

The decision is not trivial. The context window is finite. Including everything the retriever found may exceed the token budget. Dropping chunks arbitrarily may remove the most relevant information. Ordering the chunks wrong may cause the model to weight the wrong passages most heavily. Context assembly turns a list of candidates into a carefully constructed reading-order passage.

---

## 2. Explanation

### 2.1 Why

A retrieved chunk list is unoptimized for generation. It may contain:

- **Near-duplicates:** multiple chunks from the same source section, retrieved because several sentences in the section matched the query.
- **Low-relevance trailing entries:** top-k returns k results regardless of quality. The 4th and 5th entries may be weakly relevant.
- **Budget-exceeding total length:** the sum of all retrieved chunks may exceed the available token budget when combined with the system prompt, query, and output reservation.

The context assembler's job is to solve all three problems before constructing the prompt.

### 2.2 How

**Token budget allocation** divides the total context window across its competing consumers:

```
budget = context_window - system_prompt_tokens - query_tokens - output_reservation
```

The output reservation is the `max_tokens` parameter: the budget held for the model's response. The remainder is available for retrieved context. In practice, using 70–80% of the available context budget for retrieved content leaves margin for prompt framing overhead.

**Deduplication** removes near-duplicate chunks before insertion. Two chunks from the same document section may differ by a few sentences but represent the same information. A cosine similarity threshold applied to the retrieved chunk embeddings (e.g., drop any chunk with similarity ≥ 0.92 to an already-selected chunk) prevents redundancy from crowding the context.

**Selection** picks which chunks to include once the deduplicated candidate pool still exceeds the budget. Common approaches:

- **Score-ordered truncation:** include chunks in descending similarity order until the budget is consumed.
- **MMR (Maximal Marginal Relevance):** iteratively select the chunk that maximizes relevance to the query while minimizing similarity to already-selected chunks. This diversifies the context at the cost of a quadratic selection loop.

**Ordering** arranges the selected chunks within the context block. Research on LLM attention patterns shows that models weight information at the beginning and end of the context more heavily than information in the middle — the "lost-in-the-middle" effect. Practical orderings:

- **Relevance descending:** most similar chunk first. Works when the answer is self-contained in the top chunk.
- **Reverse relevance (best last):** most similar chunk last. Exploits the model's higher attention to recent tokens.
- **Source-coherent ordering:** chunks from the same document appear consecutively, preserving reading order even if individual chunks are not the top-ranked.

**Prompt framing** wraps the context block in instructions that tell the model how to use it:

```text
Context:
[1] <chunk_text>
[2] <chunk_text>
...

Answer the question using only the information in the Context above. If the context does not contain the answer, state that you don't know.

Question: <user_query>
```

Citation markers (`[1]`, `[2]`) enable the model to attribute claims to specific chunks in its response.

### 2.3 Code example

```python
# See: labs/rag/lab-query-pipeline/main.py
import tiktoken

def assemble_context(chunks: list[dict], query: str,
                     system_prompt: str, context_window: int = 8192,
                     output_reserve: int = 1024) -> str:
    """Build a context block that fits within the token budget."""
    enc = tiktoken.get_encoding("cl100k_base")

    def count(text: str) -> int:
        return len(enc.encode(text))

    budget = (context_window
              - count(system_prompt)
              - count(query)
              - output_reserve
              - 100)  # framing overhead

    selected, used = [], 0
    for chunk in chunks:  # chunks already deduplicated and sorted by score
        tokens = count(chunk["text"])
        if used + tokens <= budget:
            selected.append(chunk)
            used += tokens

    lines = [f"[{i+1}] {c['text']}" for i, c in enumerate(selected)]
    return "\n\n".join(lines)
```

---

## 3. Table

| Assembly step | Purpose | Common failure |
|--------------|---------|----------------|
| Token budget allocation | Prevent context overflow | Output reservation too small → generation truncated |
| Deduplication | Remove redundant chunks | Threshold too strict → diverse relevant chunks dropped |
| Selection | Fit within budget | Truncation drops the answer-bearing chunk |
| Ordering | Maximize model attention on key content | Relevant chunk buried in middle → ignored |
| Prompt framing | Guide model to use context | No framing → model falls back to parametric memory |

| Ordering strategy | Best for |
|------------------|---------|
| Relevance descending | Self-contained answers likely in top chunk |
| Reverse relevance (best last) | Model benefits from recency bias on key fact |
| Source-coherent | Multi-chunk answers from one document |

---

## 4. Engineering Implications

**Token counting must match the model's tokenizer.** Different models use different tokenizers. Counting characters or words produces incorrect budgets — a 400-character chunk may be 80 tokens in one model and 120 in another. Always count using the model's tokenizer (e.g., `tiktoken` for OpenAI models, Ollama's `/api/tokenize` endpoint for local models).

**The lost-in-the-middle effect is empirically validated.** Studies on GPT-4 and Llama-class models consistently show degraded retrieval from passages placed in the middle of long contexts. For critical applications, test whether reverse-ordering the context improves answer accuracy before choosing an ordering strategy.

**Context framing has strong effects.** An instruction that says "answer only from the provided context" significantly reduces hallucination on out-of-scope queries. Without this instruction, models blend retrieved content with parametric memory, making answer tracing unreliable.

**Dynamic context adjustment enables fallback behavior.** When no chunks pass a minimum relevance threshold, the assembler can switch to a fallback behavior — returning a standard "no information found" message rather than assembling an empty or low-quality context. This prevents the model from confidently answering from parametric memory when retrieval has failed.

---

## 5. Implementation Connection

`lab-query-pipeline` builds the complete RAG query pipeline end-to-end:

1. Load a ChromaDB collection built by `lab-chunking-strategies` or `lab-retrieval-playground`.
2. Embed the query, retrieve top-k chunks, deduplicate by cosine similarity.
3. Assemble the context with token counting using `tiktoken`.
4. Construct the prompt with context block and framing instructions.
5. Generate with the Ollama-hosted model and print the response alongside the source citations.

Observe: run a query where the relevant content is near the middle of the assembled context and one where it is last — compare whether the model correctly cites the right source in each case.

---

## 6. Failure Modes and Limitations

**Silent budget overflow.** If the assembler does not count tokens accurately, the full prompt can exceed the model's context window. The API may silently truncate the input from the end (dropping the user query) or return an error. This is a silent failure mode: the model receives a malformed prompt and returns a confusing response. Always validate the total token count before the API call.

**Deduplication removes paraphrased versions of the answer.** A strict cosine-similarity deduplication threshold may remove a chunk that expresses the answer in different words from a chunk that is already selected. This is a false duplicate: the second chunk adds a paraphrase that increases the probability the model extracts the correct answer. Tune the deduplication threshold empirically.

**Answer fragmented across dropped chunks.** When the answer requires synthesizing content from three chunks but only one fits in the budget, the assembled context contains an incomplete picture. The model either produces a partial answer or fills the gap from parametric memory. In such cases, increasing `max_tokens` for generation (to shrink the context budget available for retrieved text) is counterproductive — the budget problem is on the retrieval side, not the generation side.

**Framing instructions over-constrain the model.** A strict "answer only from context" instruction causes the model to refuse to answer for queries where the relevant information is clearly in the context but expressed in a form that requires mild inference. Calibrate the framing instruction to allow inference while preventing fabrication.

---

## 7. Summary

Context assembly converts a ranked list of retrieved chunks into a structured prompt-ready block. The core constraints are token budget (the context window minus the system prompt, query, and output reservation), deduplication (preventing near-duplicate chunks from crowding out diverse content), ordering (placing the most important chunks where the model attends most strongly), and framing (instructing the model to reason from the provided context rather than parametric memory). Token counting must use the target model's tokenizer to be accurate.
