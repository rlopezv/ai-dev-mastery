# CLAUDE-CODE-WORKFLOW.md

## Purpose

This document explains how to work with Claude Code in this repository day to day.
It is the practical companion to `CLAUDE.md`, which defines the rules and task steps.

---

## 1. What Claude Code is

Claude Code is a command-line agent that operates directly on the repository.
Unlike a chat assistant, it reads files, writes files, and executes commands
autonomously within the scope of the task you give it.

| Chat assistant | Claude Code |
|----------------|-------------|
| Works in conversation turns | Works autonomously on the repo |
| No access to files | Reads and writes files directly |
| Context lost between sessions | Repository is the persistent memory |
| You copy-paste outputs | Outputs go directly to the right path |

---

## 2. How to Start a Session

Navigate to the repository root and launch Claude Code:

```bash
cd ai-dev-mastery
claude
```

You do not need to explain the project in each interaction.

Claude Code is expected to load repository context from:

- `CLAUDE.md`
- `meta/system-design/REPOSITORY_LAYOUT.md`
- `meta/system-design/DOCS_LABS_MAP.md`
- `meta/session/PROJECT_STATUS.md`

These files define:

- repository structure
- module sequencing and alignment
- project state

If any of these sources are missing, incomplete, or inconsistent,
Claude Code should stop and request clarification before proceeding.

---

## 3. How to Give Tasks

Talk to Claude Code naturally. You do not need a rigid command format — describe
what you want and it will figure out the steps.

Some examples:

> "Escribe el topic de retrieval strategies para el módulo RAG"

> "Vamos a por el módulo de prompt engineering, empieza por el README"

> "Revisa el fichero que acabamos de escribir"

> "Diseña los labs del módulo de embeddings"

> "¿Qué tenemos hecho y qué sigue?"

For repetitive or precise tasks you can use slash commands. This repository defines
the following custom commands:

| Command | What it does |
|---------|-------------|
| `/write-doc <path>` | Write a single document to the given path |
| `/write-module <module>` | Write all docs for a module in sequence |
| `/review-doc <path>` | Review a document and save the report to review-cache |
| `/fix-doc <path>` | Load cached review, apply fixes, re-validate |
| `/design-labs <module>` | Design the lab set for a module |
| `/write-lab <path>` | Implement a single lab |

These commands are defined in `.claude/commands/`. Claude Code loads them automatically.

---

## 4. How Claude Code Uses the Repository

Claude Code treats these files as its operating context:

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Rules, conventions, task definitions |
| `meta/system-design/REPOSITORY_LAYOUT.md` | Where everything lives |
| `meta/system-design/DOCS_LABS_MAP.md` | Module sequence and docs↔labs alignment |
| `meta/session/PROJECT_STATUS.md` | Current project progress |
| `meta/session/review-cache/` | Persisted review reports for /fix-doc |
| `meta/standards/templates/` | Document structure for each type |
| `meta/standards/frontmatter/frontmatter-spec.md` | Frontmatter rules |
| `meta/standards/writing/writing-style.md` | Prose writing rules |
| `meta/standards/writing/lab-code-style.md` | Lab code conventions |
| `meta/standards/validation/docs-checklist.md` | Acceptance criteria for docs |
| `meta/standards/validation/labs-checklist.md` | Acceptance criteria for labs |
| `meta/standards/review/review-protocol.md` | Review structure and output format |
| `docs/reference/glossary.md` | Canonical term definitions |

Claude Code reads the relevant files at the start of each task.
You do not need to paste their contents.

---

## 5. Project Status

`meta/session/PROJECT_STATUS.md` tracks the progress of the entire tutorial.
Claude Code updates it automatically at the end of every completed task.

Check it at any time:

> "¿Qué tenemos completado hasta ahora?"

> "¿Qué falta del módulo RAG?"

---

## 6. The Review / Fix Flow

Review and fix are designed to work across sessions safely:

```
/review-doc docs/rag/retrieval-strategies.md
  → produces structured report
  → saves it to meta/session/review-cache/retrieval-strategies.review.md

/fix-doc docs/rag/retrieval-strategies.md
  → reads the cached report
  → applies fixes
  → re-validates
  → deletes the cache file
```

If you close and reopen the project between review and fix, the report is still
there. The repository is the only memory that matters.

---

## 7. Iterating on Output

If the output needs changes, be specific:

> "La sección 2.2 es demasiado abstracta, añade un ejemplo concreto con Ollama"

> "Falta el trade-off de latencia en la tabla de la sección 3"

> "El campo next del frontmatter apunta al fichero equivocado, debería ser context-assembly.md"

Vague feedback like "mejora esto" does not give Claude Code enough direction.
The more specific you are, the faster it converges.

---

## 8. Committing Work

Claude Code does not commit automatically. After reviewing the output:

```bash
git add docs/rag/retrieval-strategies.md
git add meta/session/PROJECT_STATUS.md
git commit -m "docs(rag): add retrieval-strategies topic"
```

Recommended commit message format:

```
<type>(<module>): <description>

types: docs | labs | meta | infra | fix
```

Examples:
```
docs(rag): add retrieval-strategies topic
labs(rag): implement lab-retrieval-playground
meta: update PROJECT_STATUS
fix(prompt-engineering): correct frontmatter in few-shot.md
```

Do not commit files under `meta/session/review-cache/` — they are excluded by `.gitignore`.

---

## 9. Git Workflow

### Branch strategy

| Situation | Approach |
|-----------|----------|
| Work fits in one session, affects limited files | Commit directly to `main` |
| Work spans multiple sessions or affects transversal files | Use a branch |

### Branch naming convention

| Type | Format | Example |
|------|--------|---------|
| Module docs | `docs/<module>` | `docs/rag` |
| Module labs | `labs/<module>` | `labs/rag` |
| Meta changes | `meta/<description>` | `meta/simplify-templates` |
| Fixes | `fix/<description>` | `fix/rag-frontmatter` |

### When branches make sense

- Structural changes to `meta/` that affect the whole repo
- Modules that span multiple sessions
- Template changes (allows clean before/after diff)

---

## 10. Claude Code Operational Tips

### Context management

Claude Code shows context usage during a session. When it reaches 70–90%, run:

```
/compact
```

This compresses the session context without losing the working state.
Relevant when writing full modules in a single session.

### Keep CLAUDE.md under 500 lines

Context bloat is a real problem. The current `CLAUDE.md` is ~150 lines — keep it that way.
If new rules are needed, prefer updating the referenced standards files
rather than adding content to `CLAUDE.md` directly.

---

## 11. Recommended Session Flow

```
1. Launch:        claude
2. Check status:  "¿qué tenemos hecho y qué sigue?"
3. Give task:     naturally or with a slash command
4. Review output: in the editor
5. Iterate:       be specific about what needs changing
6. Commit:        git add + git commit
```

Start with one task per session until you are comfortable with how Claude Code
works and how much output to review at once. As you gain confidence you can ask
it to write an entire module in one go.

---

## 12. When Claude Code Gets Blocked

If Claude Code stops and reports:

```
BLOCKED
REASON: ...
NEEDS: ...
```

Provide the missing information and continue. Do not ask it to proceed without
resolving the block — the output will be unreliable.
