# CLAUDE.md — AI Dev Mastery

This file is the entry point for Claude Code in this repository.
Read it completely before doing anything.

---

## 1. What this repository is

A progressive tutorial for AI development aimed at enterprise software architects
with a Java background. It combines conceptual documentation and locally executable
labs across 16 modules.

```
docs/           → learner-facing documentation (modules + reference)
labs/           → executable labs
infrastructure/ → Docker / docker-compose
meta/           → standards, templates, workflow, system design
```

---

## 2. How to orient yourself

Before starting any task, read:

```
meta/system-design/REPOSITORY_LAYOUT.md   → full repo structure
meta/system-design/DOCS_LABS_MAP.md       → module sequence and docs↔labs alignment
meta/session/PROJECT_STATUS.md            → current project progress
```

These files are your source of truth for structure, alignment, and state.
If they are absent or incomplete, stop and report it.

---

## 3. Document types

Every file under `docs/<module>/` belongs to exactly one of these types:

| Type | Path pattern |
|------|-------------|
| `step-readme` | `docs/<module>/README.md` |
| `topic` | `docs/<module>/<concept>.md` |
| `architecture` | `docs/<module>/architecture.md` |
| `reference-architecture` | `docs/reference-architectures/<n>.md` |
| `implementation-reference` | `docs/<module>/implementation-reference.md` |
| `validation` | `docs/<module>/validation.md` |
| `lab-readme` | `labs/<module>/README.md` |

Each type has a template. Templates are authoritative over structure.
Do not invent structure outside the template.

```
meta/standards/templates/
├── topic-template.md
├── step-readme-template.md
├── architecture-template.md
├── reference-architecture-template.md
├── implementation-reference-template.md
├── validation-template.md
└── lab-readme-template.md
```

---

## 4. Frontmatter — mandatory

Every file under `docs/<module>/` must include valid YAML frontmatter.
Files under `docs/reference/` do not require module frontmatter.

Required fields: `id`, `title`, `type`, `step`, `path`, `status`, `level`,
`concepts`, `prerequisites`, `next`, `related`, `implementation_refs`,
`validation_refs`, `summary`.

Full spec: `meta/standards/frontmatter/frontmatter-spec.md`

Allowed `status` values: `draft` | `review` | `final`
Allowed `level` values: `foundational` | `intermediate` | `advanced`

No placeholders. No `TBD`. No `...`.

---

## 5. Language

All learner-facing output is written in **English** — without exception and regardless
of the language used in the conversation. This applies to every file under `docs/`,
`labs/`, `infrastructure/`, and any `README.md` at any level of the repository.
Files under `meta/` are internal and may use any language.

---

## 6. Writing rules

For `topic` documents, apply this mandatory structure in section 2 (Explanation):

1. **Why** — the design decision and problem being solved
2. **How** — phases or mechanisms with conceptual grounding
3. **Code example** — minimal, readable, with a comment referencing the lab

For other document types, follow the template structure.

Full rules:
- Prose: `meta/standards/writing/writing-style.md`
- Lab code: `meta/standards/writing/lab-code-style.md`

---

## 7. Glossary — mandatory check on every doc write

`docs/reference/glossary.md` is the canonical source of term definitions across all modules.

**When writing or fixing any document:**
1. Read the `concepts` field in the frontmatter of the document being written
2. For each concept, check if it exists in `docs/reference/glossary.md`
3. If it does not exist, add it following the entry format in the glossary `## Maintenance` section
4. If it exists, use the canonical term — do not paraphrase or rename it

Never modify an existing glossary entry without explicit instruction.
Only add new entries or flag conflicts for human review.

---

## 8. Validation

Before marking any task complete, validate the output.

**For documentation:** `meta/standards/validation/docs-checklist.md`
**For labs:** `meta/standards/validation/labs-checklist.md`

Acceptance threshold: score ≥ 8.0 and no critical failures.

Report the result in this format:

```
VALIDATION_RESULT
TARGET: <file>
TYPE: <document-type>
FINAL SCORE: <x.x>
STATUS: PASS | FAIL

CRITICAL FAILURES:
- ...

REQUIRED FIXES:
- ...
```

If the result is FAIL, fix the issues before finishing.

---

## 9. Tasks

**After completing any task — whether listed here or ad-hoc (infrastructure changes,
config edits, refactors, etc.) — update `meta/session/SESSION-CONTEXT.md` with:**
- what was done
- files modified
- key decisions made
- pending items for the next session

### Write a document

1. Read `meta/system-design/DOCS_LABS_MAP.md` to understand scope
2. Read the appropriate template from `meta/standards/templates/`
3. Read `meta/standards/frontmatter/frontmatter-spec.md`
4. Read `meta/standards/writing/writing-style.md`
5. Write the full document
6. Check `concepts` against `docs/reference/glossary.md` and update it
7. Validate with `meta/standards/validation/docs-checklist.md`
8. Write to the target path
9. Update `meta/session/PROJECT_STATUS.md`
10. Update `meta/session/SESSION-CONTEXT.md`

### Write a module (all docs for a module)

1. Read `meta/system-design/DOCS_LABS_MAP.md` for the module scope
2. Write documents in this order: README → topics → architecture → implementation-reference → validation
3. Validate each document before writing the next
4. Update `docs/reference/glossary.md` with all new concepts
5. Update `meta/session/PROJECT_STATUS.md`
6. Update `meta/session/SESSION-CONTEXT.md`

### Review a document

1. Read the document
2. Apply `meta/standards/validation/docs-checklist.md`
3. Produce a structured report following `meta/standards/review/review-protocol.md`
4. Write the report to `meta/session/review-cache/<filename>.review.md`
5. Do NOT modify the document

### Fix a document

1. Check if `meta/session/review-cache/<filename>.review.md` exists and read it
2. If no cached review exists, perform the review internally first
3. Apply fixes to the document
4. Re-validate with `meta/standards/validation/docs-checklist.md`
5. Write the corrected document to the target path
6. Delete the review cache file if it exists
7. Update `meta/session/PROJECT_STATUS.md`
8. Update `meta/session/SESSION-CONTEXT.md`

### Design labs for a module

1. Read the architecture and implementation-reference docs for that module
2. Read `meta/standards/templates/lab-readme-template.md`
3. Define each lab: name, type, objective, components, expected outputs
4. Write `labs/<module>/README.md`
5. Validate with `meta/standards/validation/labs-checklist.md`
6. Update `meta/session/PROJECT_STATUS.md`
7. Update `meta/session/SESSION-CONTEXT.md`

### Write a lab

1. Read the corresponding doc from `meta/system-design/DOCS_LABS_MAP.md`
2. Read `meta/standards/writing/lab-code-style.md`
3. Implement `main.py`, `README.md`, and `requests.http` if applicable
4. Validate with `meta/standards/validation/labs-checklist.md`
5. Update `meta/session/PROJECT_STATUS.md`
6. Update `meta/session/SESSION-CONTEXT.md`

---

## 10. Lab conventions

- Each lab lives in its own folder: `labs/<module>/lab-<n>/`
- Shared utilities go in `labs/<module>/shared/` — never in individual labs
- Entry point is always `main.py`
- FastAPI labs include a `requests.http` file
- Infrastructure profile options: `light` (Ollama + API) | `full` (+ ChromaDB)

---

## 11. What NOT to do

- Do not write content without reading the template first
- Do not invent document structure outside the template
- Do not leave `TBD`, `TODO`, or placeholder text in any output
- Do not mix document types in a single file
- Do not modify files under `meta/` unless explicitly asked
- Do not create lab files without a corresponding `README.md`
- Do not assume docs↔labs alignment — read `DOCS_LABS_MAP.md`
- Do not modify existing glossary entries without explicit instruction
- Do not commit files under `meta/session/review-cache/`

---

## 12. When you are blocked

If something is missing or ambiguous, stop and report:

```
BLOCKED
REASON: <what is missing or unclear>
NEEDS: <what is required to proceed>
```

Do not guess. Do not fill gaps with assumptions.
