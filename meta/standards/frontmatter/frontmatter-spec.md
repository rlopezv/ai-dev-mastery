# meta/standards/frontmatter/frontmatter-spec.md

## 1. Purpose

This document defines the **canonical frontmatter contract** for learner-facing documentation in the repository.

Its goals are to:

- standardize document metadata
- enable structural validation
- support navigation across steps
- make document relationships explicit
- reduce ambiguity during authoring and review

This specification applies to:

- learner-facing documentation under `docs/`
- lab entry-point documents under `labs/<step>/README.md`

unless explicitly stated otherwise.

---

## 2. Scope

This specification governs:

- required metadata fields
- field types
- allowed values
- document-type variants
- validation rules

It does NOT define writing quality.

Writing quality is governed by:

```text
meta/standards/writing/writing-style.md
```

---

## 3. Canonical Document Types

The following learner-facing document types are recognized:

- `step-readme`
- `topic`
- `architecture`
- `reference-architecture`
- `implementation-reference`
- `validation`
- `lab-readme`

Every document under `docs/<module>/` MUST declare one of these values in frontmatter.

---

## 4. General Rules

### 4.1 Format

Frontmatter MUST be written as YAML at the beginning of the Markdown file.

Example:

```yaml
---
id: "rag-embeddings-and-vector-search"
title: "Embeddings and Vector Search"
type: "topic"
step: "rag"
path: "docs/05-rag/embeddings-and-vector-search.md"
status: "draft"
level: "intermediate"
concepts:
  - "embeddings"
  - "vector-search"
prerequisites:
  - "structured-outputs"
next:
  - "05-rag/context-assembly"
related:
  - "05-rag/rag-system-components"
implementation_refs:
  - "labs/05-rag/lab-02-retrieval-playground"
validation_refs:
  - "meta/standards/validation/docs-checklist.md"
summary: "Explains how embeddings represent text and how vector search powers retrieval."
---
```

---

### 4.2 Required Presence

All learner-facing documentation files under `docs/` MUST include frontmatter.

Files without frontmatter are non-compliant.

---

### 4.3 Canonical Path Ownership

The `path` field MUST reflect the repository-relative path of the current file.

It is required to support validation and navigation integrity.

---

## 5. Required Fields

The following fields are required for all recognized document types unless explicitly exempted below.

| Field | Type | Required | Description |
|------|------|----------|-------------|
| `id` | string | yes | Unique canonical identifier for the document |
| `title` | string | yes | Human-readable document title |
| `type` | enum | yes | Document type |
| `step` | string | yes | Step identifier (e.g. `05-rag`) |
| `path` | string | yes | Repository-relative file path |
| `status` | enum | yes | Lifecycle state |
| `level` | enum | yes | Intended difficulty level |
| `concepts` | list[string] | yes | Main concepts introduced or covered |
| `prerequisites` | list[string] | yes | Required prior docs or steps |
| `next` | list[string] | yes | Suggested next docs or steps |
| `related` | list[string] | yes | Related documents |
| `implementation_refs` | list[string] | yes | Related lab or implementation references |
| `validation_refs` | list[string] | yes | Related validation references |
| `summary` | string | yes | One-sentence purpose summary |

---

## 6. Field Definitions

### 6.1 `id`

**Type:** `string`  
**Required:** yes

#### Rule

`id` MUST be globally unique within `docs/`.

#### Naming rule

Use lowercase kebab-case and include the step prefix.

#### Example

```yaml
id: "03-prompt-engineering-context-management"
```

#### Invalid examples

```yaml
id: "Prompt Engineering"
id: "context_management"
```

---

### 6.2 `title`

**Type:** `string`  
**Required:** yes

#### Rule

Must be a human-readable title matching the document purpose.

#### Example

```yaml
title: "Context Management"
```

---

### 6.3 `type`

**Type:** `enum`  
**Required:** yes

#### Allowed values

- `step-readme`
- `topic`
- `architecture`
- `reference-architecture`
- `implementation-reference`
- `validation`

#### Example

```yaml
type: "topic"
```

---

### 6.4 `step`

**Type:** `string`  
**Required:** yes

#### Rule

Must match the parent step directory.

#### Format

```text
kebab-case
```

#### Examples

```yaml
step: "llm-fundamentals"
step: "rag"
```

---

### 6.5 `path`

**Type:** `string`  
**Required:** yes

#### Rule

Must be the repository-relative path of the current file.

#### Example

```yaml
path: "docs/05-rag/embeddings-and-vector-search.md"
```

---

### 6.6 `status`

**Type:** `enum`  
**Required:** yes

#### Allowed values

- `draft`
- `review`
- `final`

#### Meaning

- `draft` → written but not yet accepted
- `review` → under active validation/review
- `final` → validated and accepted

---

### 6.7 `level`

**Type:** `enum`  
**Required:** yes

#### Allowed values

- `foundational`
- `intermediate`
- `advanced`

#### Rule

`level` is both a pedagogical classification and a normative execution contract.
It governs allowed runtime complexity, infrastructure footprint, abstraction layers,
observability requirements, and acceptable failure surface for the module.

Full contract definition: `meta/system-design/LEVEL_MODE.md`

---

### 6.8 `concepts`

**Type:** `list[string]`  
**Required:** yes

#### Rule

Must list the primary concepts covered in the document.

#### Constraints

- minimum length: 1
- each entry should be lowercase kebab-case or a stable canonical phrase
- avoid vague items like `llm` unless the document is explicitly about that concept

#### Example

```yaml
concepts:
  - "embeddings"
  - "vector-search"
  - "retrieval"
```

---

### 6.9 `prerequisites`

**Type:** `list[string]`  
**Required:** yes

#### Rule

Must identify prior material required to understand the document.

#### Allowed values

- step identifiers
- repository-relative document references
- empty list when no prerequisite exists

#### Example

```yaml
prerequisites:
  - "01-foundations"
  - "04-tools-and-structured-outputs/structured-outputs.md"
```

---

### 6.10 `next`

**Type:** `list[string]`  
**Required:** yes

#### Rule

Must identify likely next reading targets.

#### Allowed values

- step identifiers
- repository-relative document references
- empty list only for terminal documents in a sequence

---

### 6.11 `related`

**Type:** `list[string]`  
**Required:** yes

#### Rule

Must identify conceptually related documents.

This field is not for navigation sequence; it is for semantic adjacency.

---

### 6.12 `implementation_refs`

**Type:** `list[string]`  
**Required:** yes

#### Rule

Must point to concrete implementation or lab artifacts when applicable.

#### Allowed values

- `labs/...`
- empty list only if there is intentionally no implementation relation

#### Example

```yaml
implementation_refs:
  - "labs/05-rag/lab-02-retrieval-playground"
```

---

### 6.13 `validation_refs`

**Type:** `list[string]`  
**Required:** yes

#### Rule

Must point to the standards or validation artifacts used to assess the document.

#### Minimum expectation

At least one validation reference is required.

#### Example

```yaml
validation_refs:
  - "meta/standards/validation/docs-checklist.md"
```

---

### 6.14 `summary`

**Type:** `string`  
**Required:** yes

#### Rule

Must summarize the document in one sentence.

#### Constraints

- one sentence preferred
- must describe purpose, not marketing value
- should remain under 200 characters when practical

---

## 7. Document-Type Rules

The following rules refine expectations by document type.

### 7.1 `step-readme`

#### Role

Entry point to a step.

#### Additional expectations

- `concepts` should summarize the step, not every subtopic
- `implementation_refs` may contain multiple labs
- `next` should usually point to the first topic(s) in the step or the next step

---

### 7.2 `topic`

#### Role

Primary conceptual teaching unit.

#### Additional expectations

- `concepts` should be specific
- `implementation_refs` should exist for core engineering topics
- `related` should connect to nearby conceptual material

---

### 7.3 `architecture`

#### Role

System-level view for the step.

#### Additional expectations

- `related` should connect to core topics in the same step
- `implementation_refs` should point to system-oriented labs or shared infrastructure when applicable

---

### 7.4 `implementation-reference`

#### Role

Bridge between concept and execution.

#### Additional expectations

- `implementation_refs` should not be empty
- `prerequisites` should include concept topics needed to understand implementation choices

---

### 7.5 `validation`

#### Role

Assessment and completion criteria for the step.

#### Additional expectations

- `validation_refs` should explicitly reference the relevant checklist(s)
- `implementation_refs` may be empty if the document is purely evaluative

---

### 7.6 `lab-readme`

#### Role

Entry point for lab execution within a step.

#### Purpose

- Explain how to run labs
- Describe available lab implementations
- Provide execution context
- Connect labs to documentation

#### Additional expectations

- `implementation_refs` should reference actual lab folders
- `prerequisites` should reference required documentation or steps
- `related` should connect to corresponding docs
- `validation_refs` may reference lab-specific validation when defined

#### Structure note

Unlike `topic` documents, `lab-readme` does NOT follow the full explanatory pattern.

It is operational, not pedagogical.

It may include:

- setup instructions
- execution steps
- expected outputs
- troubleshooting notes
- 

---

## 8. Optional Fields

The following fields are optional and may be added when useful.

| Field | Type | Purpose |
|------|------|---------|
| `tags` | list[string] | Search and grouping support |
| `audience_notes` | string | Special audience constraints |
| `sandbox_refs` | list[string] | Explicit runtime/sandbox references |
| `review_notes` | string | Temporary review-related metadata |

### Rule

Optional fields MUST NOT redefine the meaning of required fields.

---

## 9. Validation Rules

A frontmatter block is valid only if all of the following are true:

1. YAML parses successfully
2. All required fields exist
3. All enum fields use allowed values
4. All required list fields are lists, even when empty
5. `step` matches the parent step directory
6. `path` matches the actual repository-relative path
7. `id` is unique across `docs/`
8. `type` is one of the recognized canonical values
9. `summary` is non-empty
10. no required field contains placeholder text such as:
   - `TBD`
   - `...`
   - `example`
   - `todo`

---

## 10. Non-Compliant Examples

### 10.1 Missing required fields

```yaml
---
title: "Embeddings"
type: "topic"
---
```

Reason:
- missing `id`, `step`, `path`, `status`, `level`, `concepts`, `prerequisites`, `next`, `related`, `implementation_refs`, `validation_refs`, `summary`

---

### 10.2 Invalid enum values

```yaml
---
status: "done"
level: "medium"
type: "chapter"
---
```

Reason:
- invalid enum values

---

### 10.3 Wrong path/step alignment

```yaml
---
step: "structured-outputs"
path: "docs/05-rag/embeddings-and-vector-search.md"
---
```

Reason:
- step and path are inconsistent

---

## 11. Minimal Valid Examples

### 11.1 Step README

```yaml
---
id: "05-rag-readme"
title: "RAG"
type: "step-readme"
step: "rag"
path: "docs/05-rag/README.md"
status: "draft"
level: "intermediate"
concepts:
  - "rag"
  - "retrieval"
  - "context-assembly"
prerequisites:
  - "structured-outputs"
next:
  - "05-rag/rag-system-components.md"
related:
  - "06-memory/README.md"
implementation_refs:
  - "labs/05-rag/"
validation_refs:
  - "meta/standards/validation/docs-checklist.md"
summary: "Introduces retrieval-augmented generation and the structure of this step."
---
```

### 11.2 Topic File

```yaml
---
id: "rag-embeddings-and-vector-search"
title: "Embeddings and Vector Search"
type: "topic"
step: "rag"
path: "docs/05-rag/embeddings-and-vector-search.md"
status: "draft"
level: "intermediate"
concepts:
  - "embeddings"
  - "vector-search"
prerequisites:
  - "05-rag/rag-system-components.md"
next:
  - "05-rag/retrieval-strategies.md"
related:
  - "05-rag/document-processing-and-chunking.md"
implementation_refs:
  - "labs/05-rag/lab-02-retrieval-playground"
validation_refs:
  - "meta/standards/validation/docs-checklist.md"
summary: "Explains how text is represented numerically and searched by semantic similarity."
---
```

---

## 12. Final Rule

If a learner-facing document under `docs/` does not satisfy this specification, it MUST be treated as structurally invalid.

The document may still contain useful content, but it is not compliant with the repository standard until frontmatter is corrected.

### Special Case — `lab-readme`

For `lab-readme`:

- `step` MUST match the lab step directory
- `path` MUST point to `labs/<step>/README.md`
- `implementation_refs` SHOULD reference sub-labs within the step