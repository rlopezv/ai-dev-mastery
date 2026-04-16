---
id: "rag-document-processing-and-chunking"
title: "Document Processing and Chunking"
type: "topic"
step: "rag"
path: "docs/rag/document-processing-and-chunking.md"
status: "draft"
level: "intermediate"

concepts:
  - "chunking"
  - "chunk-size"
  - "chunk-overlap"
  - "recursive-chunking"
  - "document-loader"

prerequisites:
  - "docs/rag/embeddings-and-vector-search.md"

next:
  - "docs/rag/retrieval-strategies.md"

related:
  - "docs/rag/context-assembly.md"

implementation_refs:
  - "labs/rag/lab-chunking-strategies"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how source documents are loaded, cleaned, and split into retrievable units, covering the trade-offs between chunk size, overlap, and split strategy on retrieval quality."
---

## 1. Intuition

A vector database does not store full documents — it stores segments. Retrieval returns segments, not pages. The question is: how do you cut a document so that each segment contains a complete, self-contained thought that matches what a user might query?

Cut too coarsely (large chunks) and the retrieved segment contains many sentences, only a few of which are relevant — the signal is diluted. Cut too finely (small chunks) and a single concept is split across multiple segments, none of which is fully informative on its own. Chunking is the problem of finding the right granularity.

---

## 2. Explanation

### 2.1 Why

Embedding models produce a single vector for an entire input text. When the text is long and covers multiple topics, the resulting vector is a blend of all those topics — it is a good match for none of them. A query about a specific subtopic will score poorly against a chunk whose vector averages that topic with several others.

Chunking solves this by ensuring that each vector represents a focused, coherent unit. The granularity of a chunk determines the precision of retrieval: smaller, more focused chunks allow the retrieval step to identify exactly the relevant passage, at the cost of losing surrounding context.

### 2.2 How

**Document loading** is the first step. Source documents come in many formats — PDF, Markdown, HTML, plain text, database records. Each format requires a loader that extracts clean text: PDF loaders must handle multi-column layouts and footnotes; HTML loaders must strip navigation and boilerplate; Markdown loaders may preserve or strip headers and code fences.

**Chunking strategies:**

**Fixed-size chunking** splits text at a fixed character or token count, regardless of sentence or paragraph boundaries. It is simple and predictable but breaks sentences mid-thought. Chunk size of 256–512 tokens is common.

**Sentence-boundary chunking** respects sentence endings, accumulating sentences until the chunk reaches a target size. This preserves syntactic completeness but produces variable-length chunks.

**Recursive character chunking** applies a priority-ordered list of split delimiters — paragraph break → sentence ending → word boundary — and uses the coarsest delimiter that keeps chunks within the size limit. This is the most commonly used strategy in practice because it balances completeness with predictable size.

**Semantic chunking** groups sentences by their embedding similarity, splitting when similarity drops below a threshold. This produces semantically coherent chunks but requires an embedding pass during indexing and is significantly slower.

**Chunk overlap** solves the boundary problem: consecutive chunks share a fixed number of tokens (typically 10–20% of chunk size). When a relevant sentence falls at the boundary between two chunks, overlap ensures at least one chunk contains it in full. Overlap increases index size proportionally.

**Metadata attachment** augments each chunk with source information — filename, section heading, page number, creation date. This metadata enables filtered retrieval and source attribution in answers.

### 2.3 Code example

```python
# See: labs/rag/lab-chunking-strategies/main.py
# Recursive character chunking with overlap

def recursive_chunk(text: str, chunk_size: int = 512,
                    overlap: int = 64) -> list[str]:
    """Split text using paragraph → sentence → word priority."""
    separators = ["\n\n", "\n", ". ", " ", ""]
    for sep in separators:
        parts = text.split(sep) if sep else list(text)
        if max(len(p) for p in parts) <= chunk_size:
            break
    chunks, current = [], ""
    for part in parts:
        candidate = current + sep + part if current else part
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # carry overlap into next chunk
            current = current[-overlap:] + sep + part if current else part
    if current:
        chunks.append(current)
    return chunks
```

---

## 3. Table

| Strategy | Boundary awareness | Chunk size variance | Indexing cost | Use case |
|----------|--------------------|--------------------|--------------| ---------|
| Fixed-size | None | Low | Minimal | Simple pipelines, known token distributions |
| Sentence-boundary | Sentence | Medium | Low | Factual documents with clear sentences |
| Recursive character | Paragraph → sentence → word | Low | Low | General purpose default |
| Semantic | Meaning shift | High | High (embedding pass) | High-quality corpora where cost is acceptable |

| Parameter | Typical range | Effect of increasing |
|-----------|--------------|---------------------|
| `chunk_size` (tokens) | 128–1024 | More context per chunk, lower retrieval precision |
| `chunk_overlap` (tokens) | 0–200 | Fewer boundary misses, larger index |
| `top_k` (retrieval) | 3–20 | More candidates retrieved, higher context cost |

---

## 4. Engineering Implications

**Chunk size is the primary retrieval quality lever.** Larger chunks increase the probability of including the relevant passage but reduce the embedding's focus. Smaller chunks improve embedding precision but increase the risk of retrieving an incomplete answer. Empirically tune chunk size against a representative evaluation set rather than using defaults.

**Overlap trades index size for boundary recall.** An overlap of 10% increases the index size by 10% but recovers a meaningful fraction of cross-boundary misses. For corpora where facts frequently span sentence boundaries — legal text, technical specifications — overlap is not optional.

**Headings and structure should survive chunking.** In structured documents, stripping headers to reduce token count also removes the semantic signal that identifies a chunk's topic. Prepending the section heading to each chunk ("**Section 3.2: Authentication** ...") significantly improves embedding quality for hierarchical documents.

**Metadata filtering multiplies the value of chunking.** A well-chunked index with source, section, and date metadata enables filtered retrieval — "find the most recent installation guide" — that pure similarity search cannot express.

**Re-chunking is expensive.** Changing the chunk size or strategy requires re-embedding the entire corpus. Treat chunking strategy as an architectural decision made before the first production index is built.

---

## 5. Implementation Connection

`lab-chunking-strategies` demonstrates:

1. Loading a plain-text document and applying fixed-size, sentence-boundary, and recursive chunking.
2. Indexing all three chunk sets into separate ChromaDB collections.
3. Running a fixed set of queries against each collection and comparing top-1 cosine similarity scores.
4. Observing that recursive chunking returns more semantically complete matches for paragraph-spanning facts.

After the lab, compare how the score distributions differ across strategies for the same query set. The goal is not to find the universally best strategy but to observe the trade-off between chunk cohesion and retrieval precision empirically.

---

## 6. Failure Modes and Limitations

**PDF extraction noise.** PDF parsing is lossy. Multi-column layouts, tables, and inline images produce garbled text when extracted linearly. Chunks derived from poorly extracted PDFs contain characters from adjacent columns mixed together, producing nonsensical vectors. Validate extraction quality before indexing.

**Code chunk fragmentation.** Source code does not follow natural language sentence structure. Splitting code at character boundaries fragments function bodies and produces chunks that are syntactically incomplete. Code-specific chunkers that respect function or class boundaries are required for code-heavy corpora.

**Very long documents without natural breaks.** Some documents — legal contracts, transcripts — contain paragraphs of several thousand words with no natural break points. Recursive chunking falls back to word boundaries in these cases, producing arbitrary splits with no structural meaning.

**Chunk deduplication neglect.** Corpora with many similar documents (multiple versions of a specification) produce near-duplicate chunks that crowd the top-k results for many queries. Deduplication at indexing time — checking cosine similarity against existing chunks before inserting — keeps the index lean and improves retrieval diversity.

---

## 7. Summary

Chunking converts source documents into retrievable units whose granularity determines retrieval precision. The recursive character strategy is the practical default: it respects natural text boundaries while producing predictably sized chunks. Overlap mitigates boundary misses at the cost of index size. Chunk size, overlap, and splitting strategy are architectural parameters that must be validated empirically and are expensive to change after an index is built.
