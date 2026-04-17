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
meta/system-design/LEVEL_MODE.md          → normative level contracts (runtime, infrastructure, abstraction)
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
├── topic-scaffold.md
├── step-readme-scaffold.md
├── architecture-scaffold.md
├── reference-architecture-scaffold.md
├── implementation-reference-scaffold.md
├── validation-scaffold.md
├── lab-entry-readme-scaffold.md
└── lab-individual-readme-scaffold.md
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

**After completing any task — whether listed here or ad-hoc — rewrite
`meta/session/SESSION-CONTEXT.md` as a compact briefing with three sections:**
- **Current state** — next module/task, any blockers
- **Recent decisions** — design decisions from the last 1–2 sessions not yet reflected in `meta/` files
- **Next task** — the immediate next action

Do not accumulate history. Replace the full content each time. Target: under 20 lines.

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
2. Verify the module's declared level against `meta/system-design/LEVEL_MODE.md` — confirm allowed runtime, abstraction, and infrastructure
3. Write documents in this order: README → topics → architecture → implementation-reference → validation
4. Validate each document before writing the next
5. If the module requires components outside its default level profile, document the exception per LEVEL_MODE G-5 in the module README, `labs/<module>/README.md`, and `infrastructure/README.md`
6. Update `docs/reference/glossary.md` with all new concepts
7. Update `meta/session/PROJECT_STATUS.md`
8. Update `README.md`, `docs/README.md`, and `labs/README.md` with the new module (status, lab names, descriptions)
9. Update `meta/session/SESSION-CONTEXT.md`

### Review a document

1. Read the document
2. Apply `meta/standards/validation/docs-checklist.md`
3. Produce a structured report following `meta/standards/review/review-protocol.md`
4. Write the report to `meta/session/reports/<filename>.review.md`
5. Do NOT modify the document

### Fix a document

1. Check if `meta/session/reports/<filename>.review.md` exists and read it
2. If no cached review exists, perform the review internally first
3. Apply fixes to the document
4. Re-validate with `meta/standards/validation/docs-checklist.md`
5. Write the corrected document to the target path
6. Delete the report file if it exists
7. Update `meta/session/PROJECT_STATUS.md`
8. Update `meta/session/SESSION-CONTEXT.md`

### Design labs for a module

1. Read the architecture and implementation-reference docs for that module
2. Read `meta/standards/templates/lab-entry-readme-scaffold.md`
3. Define each lab: name, type, objective, components, expected outputs
4. Write `labs/<module>/README.md`
5. Validate with `meta/standards/validation/labs-checklist.md`
6. Update `meta/session/PROJECT_STATUS.md`
7. Update `meta/session/SESSION-CONTEXT.md`

### Write a lab

1. Read the corresponding doc from `meta/system-design/DOCS_LABS_MAP.md`
2. Read `meta/standards/writing/lab-code-style.md`
3. Read `meta/standards/templates/lab-individual-readme-scaffold.md`
4. Implement `main.py`, `README.md`, and `requests.http` if applicable
5. Ensure `labs/<module>/requirements.txt` exists; add a `-r labs/<module>/requirements.txt` line to `.devcontainer/post-create.sh` if not already present
6. Verify the lab's infrastructure profile matches the module's level policy (LEVEL_MODE); document any exception per G-5
7. Validate with `meta/standards/validation/labs-checklist.md`
8. Update `meta/session/PROJECT_STATUS.md`
9. Update `meta/session/SESSION-CONTEXT.md`

### Write labs (all labs for a module)

1. Read `labs/<module>/README.md` for the lab inventory
2. Execute "Write a lab" for each required lab in listed order
3. Verify all `required` labs per `meta/system-design/DOCS_LABS_MAP.md` are complete
4. Update `meta/session/PROJECT_STATUS.md`
5. Update `README.md`, `docs/README.md`, and `labs/README.md`
6. Update `meta/session/SESSION-CONTEXT.md`

### Audit module

1. Read `meta/system-design/LEVEL_MODE.md` for the module's level policy
2. Validate all `docs/<module>/` files with `meta/standards/validation/docs-checklist.md`
3. Validate all `labs/<module>/` with `meta/standards/validation/labs-checklist.md`
4. Check docs↔labs alignment against `meta/system-design/DOCS_LABS_MAP.md`
5. Check all frontmatter cross-references point to real files
6. Write report to `meta/session/reports/<module>.audit.md`
7. Display results — PASS / FAIL per file with severity

### Audit (global)

1. Run "Audit module" for each module marked ✅ in `meta/session/PROJECT_STATUS.md`
2. Check cross-module prerequisites form a valid DAG (no circular dependencies)
3. Check terminology consistency across modules against `docs/reference/glossary.md`
4. Check `README.md`, `docs/README.md`, and `labs/README.md` are in sync with `PROJECT_STATUS.md`
5. Write report to `meta/session/reports/audit.md`
6. Report as structured observations — requires human review, not PASS/FAIL

### Enrich

1. Read `meta/session/reports/audit.md` if available, or derive a global view from current state
2. Apply horizontal navigation improvements: enrich `next` and `related` fields with cross-module references where concepts overlap
3. Build or update reading paths by audience profile (developer / architect)
4. Write report of all changes made to `meta/session/reports/enrich.md`

### Dist

Produce a clean learner-facing distribution of the repository in `dist/`.

1. Delete `dist/` if it exists, then recreate it
2. Copy into `dist/`: `docs/`, `labs/`, `infrastructure/`, `README.md`, `.devcontainer/`, `.env.example`
3. Do NOT copy: `CLAUDE.md`, `.claude/`, `meta/`, `.work/`, `meta/session/reports/`, `.gitignore`
4. In `dist/README.md`, remove any references to `CLAUDE.md`, `.claude/`, or `meta/`
5. Verify all internal links in `dist/` resolve correctly within the dist tree

---

## 10. Lab conventions

- Each lab lives in its own folder: `labs/<module>/lab-<n>/`
- Shared utilities go in `labs/<module>/shared/` — never in individual labs
- Entry point is always `main.py`
- FastAPI labs include a `requests.http` file
- Infrastructure profile options: `foundational` (Ollama + Open WebUI) | `intermediate` (+ ChromaDB) | `advanced` (TBD per module)
- Each module has exactly one `labs/<module>/requirements.txt`; `.devcontainer/post-create.sh` installs all of them — the devcontainer is the Python runtime

### implementation-reference scope

`implementation-reference.md` covers **design patterns and architectural decisions only**:
patterns, component mappings, data structures, design-level trade-offs, and failure modes
caused by wrong design choices.

**Do not** put setup commands, `pip install` instructions, operational failure modes
(service not running, model not found), or expected lab outputs in `implementation-reference.md`.
Those belong in `labs/<module>/README.md`.

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
- Do not commit files under `meta/session/reports/`

---

## 12. When you are blocked

If something is missing or ambiguous, stop and report:

```
BLOCKED
REASON: <what is missing or unclear>
NEEDS: <what is required to proceed>
```

Do not guess. Do not fill gaps with assumptions.
