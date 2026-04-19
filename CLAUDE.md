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

### Write a document

1. Read `meta/system-design/DOCS_LABS_MAP.md` to understand scope
2. Read the appropriate template from `meta/standards/templates/`
3. Read `meta/standards/frontmatter/frontmatter-spec.md`
4. Read `meta/standards/writing/writing-style.md`
5. Read existing docs in the same module to confirm terminological consistency before writing
6. Write the full document
7. Check `concepts` against `docs/reference/glossary.md` and update it
8. Validate with `meta/standards/validation/docs-checklist.md`
9. Write to the target path
10. Update `meta/session/PROJECT_STATUS.md`
11. Update `meta/session/SESSION-CONTEXT.md`

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
4. Check any new concepts introduced by fixes against `docs/reference/glossary.md`; add missing entries; if an existing entry conflicts with the document's usage, append to `meta/session/PENDING.md` under `## Decide` rather than modifying the glossary
5. Re-validate with `meta/standards/validation/docs-checklist.md`
6. Write the corrected document to the target path
7. Delete the report file if it exists
8. Update `meta/session/PROJECT_STATUS.md` only if the fix advances the document's `status` (e.g., from `draft` to `review`)
9. Update `meta/session/SESSION-CONTEXT.md`

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

### Audit a document

Audits a single document and updates its `status` in frontmatter and its rows in the module
audit report. Use for targeted re-audits after fixes or to advance a document through phases.

**Does NOT update Overall Status** — that is the exclusive responsibility of `/audit-module`.
After using `/audit-doc` on multiple documents, run "Phase 2 — Finalization" (see below) to
recalculate Overall Status without re-auditing.

1. Read the document
2. Determine the audit phase from the document's current `status`: `draft` → apply Phase 1; `review` → apply Phase 2 (cohesion). Override if the user specifies a phase explicitly.
3. Phase 1: apply SC-1 to SC-6 and IQ-5, IQ-6 from `meta/standards/validation/docs-checklist.md`
4. Phase 2 (cohesion): apply CQ-1 to CQ-5, PQ-1 to PQ-5, EQ-1 to EQ-5, IQ-1 to IQ-4, LC-1 to LC-5
5. Update `status` in the document's frontmatter:
   - Static checks all PASS → `status: review`
   - Cohesion checks all PASS → `status: final`
6. Update the document's rows in `meta/audit/reports/<module>.audit.md` — do not touch Overall Status

### Audit module

Runs the full module audit in two explicit phases. Report format: `meta/standards/audit/audit-report-format.md`.
Check result states: PASS | FAIL | FIXED | PENDING | SKIP (see format spec for definitions).

**Phase 1 — Static** (structure, alignment, and glossary — no content reading required):

1. Read `meta/system-design/LEVEL_MODE.md` for the module's level policy
2. For each doc in `docs/<module>/`: apply SC-1 to SC-6, IQ-5, IQ-6
3. For each lab README in `labs/<module>/`: check required sections and optional/required alignment
4. Check docs↔labs alignment against `meta/system-design/DOCS_LABS_MAP.md`
5. Check all frontmatter cross-references point to real files
6. Fix any FAIL findings or flag for human review — for items that cannot be resolved without human input, append to `meta/session/PENDING.md` under `## Review`
7. Run `python .work/scripts/sync-frontmatter-status.py <module> review` to update frontmatter; verify output shows no unexpected WARN lines
8. Write `meta/audit/reports/<module>.audit.md` with Phase 1 results; mark cohesion and execution checks as PENDING
9. Update Overall Status to `STATIC_PASS | COHESION_PENDING | EXECUTION_PENDING` (use `EXECUTION_SKIP` for modules with no labs); for modules with labs, also append to `meta/session/PENDING.md` under `## Execute`

**Phase 2 — Cohesion** (reads content for correctness, pedagogy, and engineering quality):

1. For each doc in `docs/<module>/`: apply CQ-1 to CQ-5, PQ-1 to PQ-5, EQ-1 to EQ-5, IQ-1 to IQ-4, LC-1 to LC-5
2. Fix any FAIL findings or flag for human review — for items that cannot be resolved without human input, append to `meta/session/PENDING.md` under `## Review`
3. Run `python .work/scripts/sync-frontmatter-status.py <module> final` to update frontmatter; verify output shows no unexpected WARN lines
4. Append Phase 2 section to `meta/audit/reports/<module>.audit.md` — do not rewrite Phase 1
5. Update Overall Status to `STATIC_PASS | COHESION_PASS | EXECUTION_PENDING`

**Phase 2 — Finalization** (use after targeted `/audit-doc` re-audits, not after a full Phase 2 run):

1. Read all Phase 2 rows in `meta/audit/reports/<module>.audit.md`
2. If all checks are PASS or FIXED (no FAIL, no PENDING) → update Overall Status to `STATIC_PASS | COHESION_PASS | EXECUTION_PENDING`
3. If any FAIL remains → leave Overall Status as `COHESION_PENDING` and list the failing checks

**Phase 3 — Execution** (requires live infrastructure: Ollama running, devcontainer active):

If infrastructure is not available in the current session: append this module to
`meta/session/PENDING.md` under `## Execute` and emit `HUMAN_ACTION_REQUIRED`. Do not proceed.

1. For each lab in `labs/<module>/`: run `python lab-<n>/main.py` and verify exit 0
2. Verify expected output matches what the lab README describes
3. Fix any lab failures or flag for human review — unfixable failures go to `meta/session/PENDING.md` under `## Review`
4. Fill in `## Phase 3 — Execution` in `meta/audit/reports/<module>.audit.md` — do not rewrite Phase 1 or Phase 2
5. Update Overall Status to `FULL_PASS`
6. Remove this module's `## Execute` entry from `meta/session/PENDING.md`

### Pending

Show items awaiting human intervention accumulated across sessions.

1. Read `meta/session/PENDING.md`
2. Display unchecked items grouped by section: `## Execute` / `## Review` / `## Decide`
3. Report count per section and total
4. Do NOT modify the file — items are cleared by the user or automatically when the corresponding command completes (e.g., Phase 3 removes its `## Execute` entry)

### Audit (global)

1. Run "Audit module" Phase 1 for each module marked ✅ in `meta/session/PROJECT_STATUS.md`
2. Check cross-module prerequisites form a valid DAG (no circular dependencies)
3. Check terminology consistency across modules against `docs/reference/glossary.md`
4. Check `README.md`, `docs/README.md`, and `labs/README.md` are in sync with `PROJECT_STATUS.md`
5. Write persistent report to `meta/audit/reports/global.audit.md`
6. Report as structured observations — requires human review, not PASS/FAIL

### Enrich

1. Read `meta/audit/reports/global.audit.md` if available, or derive a global view from current state
2. Apply horizontal navigation improvements: enrich `next` and `related` fields with cross-module references where concepts overlap
3. Build or update reading paths by audience profile (developer / architect)
4. Write report of all changes made to `meta/audit/reports/enrich.md`

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
