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
meta/session/PENDING.md                   → items awaiting human intervention from prior sessions
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

- `draft` — written but not yet audited
- `review` — Phase 1 (static) audit complete
- `final` — Phase 2 (cohesion) audit complete

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

**When a task generates items requiring human intervention**, append them to
`meta/session/PENDING.md` under the appropriate section (`## Execute`, `## Review`,
or `## Decide`) and emit a `HUMAN_ACTION_REQUIRED` block at the end of the response:

```
HUMAN_ACTION_REQUIRED
ITEMS ADDED TO PENDING.md:
- [Execute] <module> — <what to run and why>
- [Review] <file> — <reason for escalation>
- [Decide] <topic> — <what needs deciding>
```

Only emit this block when items are actually added. Do not emit it speculatively.

### Available procedures

Full procedure steps live in `meta/workflow/procedures/`. Each slash command delegates to the corresponding file.

| Command | Procedure file | Scope |
|---------|---------------|-------|
| `/write-doc` | `meta/workflow/procedures/write-doc.md` | Single document |
| `/write-module` | `meta/workflow/procedures/write-module.md` | All docs for a module |
| `/review-doc` | `meta/workflow/procedures/review-doc.md` | Single document |
| `/fix-doc` | `meta/workflow/procedures/fix-doc.md` | Single document |
| `/design-labs` | `meta/workflow/procedures/design-labs.md` | Labs for a module |
| `/write-lab` | `meta/workflow/procedures/write-lab.md` | Single lab |
| `/write-labs` | `meta/workflow/procedures/write-labs.md` | All labs for a module |
| `/audit-doc` | `meta/workflow/procedures/audit-doc.md` | Single document |
| `/audit-module` | `meta/workflow/procedures/audit-module.md` | Full module (3 phases) |
| `/pending` | `meta/workflow/procedures/pending.md` | Show pending items |
| `/audit` | `meta/workflow/procedures/audit-global.md` | All modules |
| `/enrich` | `meta/workflow/procedures/enrich.md` | Cross-module navigation |
| `/dist` | `meta/workflow/procedures/dist.md` | Learner distribution |

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

## 12. Prefer scripts over direct edits for bulk changes

When a task requires modifying more than ~5 files in a repetitive or mechanical way
(renaming strings, inserting blocks, reformatting structure), **do not apply the changes
directly**. Instead:

1. Propose writing a script (Python preferred) that the user can run locally
2. Place the script in `.work/scripts/<descriptive-name>.py`
3. Include a brief comment at the top explaining what it does and how to run it
4. Wait for the user to confirm before writing the script

**The user runs the script locally — Claude does not execute it via Bash.**
The token saving only exists if execution stays on the user's machine.
If the user pastes output back, review it and respond; do not re-execute.

---

## 13. When you are blocked

If something is missing or ambiguous, stop and report:

```
BLOCKED
REASON: <what is missing or unclear>
NEEDS: <what is required to proceed>
```

Do not guess. Do not fill gaps with assumptions.
