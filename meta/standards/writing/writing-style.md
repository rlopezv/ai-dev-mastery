# writing-style.md

## Purpose

This document defines the writing rules for all learner-facing content in the
repository: `docs/`, `labs/`, `README.md` files at any level, and
`infrastructure/`. Writing style is separate from document structure — structure
is governed by templates. This document governs tone, language, and content
quality within each section.

---

## 1. Language

All documentation is written in English. No exceptions.

---

## 2. Audience

Enterprise software architects with a Java background. Assume strong engineering
fundamentals. Do not assume prior ML or AI knowledge beyond what the prerequisites
of the document declare.

---

## 3. Tone

Technical and direct. No marketing language. No filler phrases.

Avoid:
- "In today's world..."
- "It is important to note that..."
- "As we can see..."

Prefer:
- Direct statements
- Causal explanations ("X happens because Y")
- Concrete examples over abstract descriptions

---

## 4. Document-Type Rules

### 4.1 topic

The mandatory writing structure for section 2 (Explanation) is:

**2.1 Why** — the design decision and the problem this concept solves.
Not a definition. A reason.

**2.2 How** — phases or mechanisms with conceptual grounding. Causal, not
descriptive. Explain what happens internally, not just what the API looks like.

**2.3 Code example** — minimal and readable. The minimum necessary to interpret
the lab. Include a comment referencing the lab:

```python
# See: labs/<module>/lab-<n>/main.py
```

This structure is mandatory for `topic` documents and does not apply to other types.

### 4.2 Other document types

Follow the template structure. Apply the general writing principles below.
Do not force the topic pattern where it does not fit.

---

## 5. General Writing Principles

### 5.1 Causal over descriptive

Every explanation must answer *why* or *how*, not only *what*.

| Avoid | Prefer |
|-------|--------|
| "Embeddings are vector representations of text." | "Embeddings represent text as vectors so that semantic similarity can be computed as geometric distance." |
| "RAG retrieves documents before generating a response." | "RAG retrieves documents first because the LLM has no access to external knowledge at inference time." |

### 5.2 Concrete over abstract

Ground every concept in system behavior or implementation consequence.

- Prefer real numbers, real services, real failure modes
- Avoid purely theoretical descriptions with no engineering grounding
- Reference the local infrastructure where applicable (Ollama, ChromaDB, FastAPI)

### 5.3 Tables for synthesis, not decoration

Use tables to compress comparative or structured information.
Do not use tables as a substitute for explanation.

Valid uses:
- Comparison of approaches or strategies
- Component breakdown with roles
- Input/output mapping
- Trade-off summary

Invalid uses:
- Repeating prose content in table form
- Single-column tables
- Tables with vague or empty cells

### 5.4 Terminology consistency

Use the same term for the same concept throughout a document and across modules.
Do not alternate between synonyms. Consult `docs/reference/glossary.md` for
canonical terms before writing.

### 5.5 No placeholders

No `TBD`, `TODO`, `...`, or incomplete sentences in any published document.
A document with placeholders is not ready for review.

---

## 6. Code Examples

- Use Python unless the module is explicitly Java-focused
- Minimal: only the lines needed to understand the concept
- No error handling unless error handling is the concept being taught
- Always include a comment referencing the corresponding lab
- No invented APIs or services — only reference what exists in the infrastructure

```python
# Minimal example — see labs/rag/lab-embeddings/main.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
embedding = model.encode("What is RAG?")
```

---

## 7. Diagrams and Visual Aids

- Use text-based diagrams (ASCII or Mermaid) when possible
- Keep diagrams simple — one concept per diagram
- Always follow a diagram with a prose explanation
- Do not use diagrams as a substitute for explanation

---

## 8. Section Length

These rules apply to `topic` documents (§4.1). Other document types follow their template structure.

- Intuition: 2–4 sentences. Short by design.
- Explanation: as long as needed, structured in the three parts defined above
- Tables: no minimum, but every row must be meaningful
- Engineering Implications: at least one concrete consequence
- Summary: 3–5 sentences maximum

---

## 9. What to Avoid

| Anti-pattern | Why |
|--------------|-----|
| Copying documentation from official sources | Adds no pedagogical value |
| Explaining the API before explaining the concept | Inverts the learning sequence |
| Generic examples not tied to the module context | Does not help readers connect theory to practice |
| Sections that only restate the title | Empty content, adds no understanding |
| Overuse of bullet lists | Breaks causal flow, hides reasoning |
