# REPOSITORY_LAYOUT.md

## Purpose

This document defines the canonical structure of the repository.
It is the authoritative reference for file placement, naming conventions, and layer separation.

---

## Top-Level Layout

```text
ai-dev-mastery/
├── .claude/
│   └── commands/                 ← custom Claude Code slash commands
├── .devcontainer/
├── .env.example
├── .gitignore
├── README.md                     ← master index (Modules table + Labs table with status)
├── docs/
│   └── README.md                 ← docs section index (document types + module descriptions)
├── labs/
│   └── README.md                 ← labs section index (infrastructure profiles + conventions + module index)
├── infrastructure/
└── meta/
```

### README hierarchy

Three README files serve distinct roles and must not duplicate each other:

| File | Audience | Content |
|------|----------|---------|
| `README.md` | Entry point for anyone | Module sequence, status (✅/⬜), links to docs and labs |
| `docs/README.md` | Learners navigating docs | Document types, how to read a module, module descriptions |
| `labs/README.md` | Learners running labs | Infrastructure profiles, runtime conventions, lab index per module |

Status shown in `README.md` and `labs/README.md` is derived from `meta/session/PROJECT_STATUS.md`, which is the authoritative source.

---

## Layer Responsibilities

| Layer | Responsibility |
|-------|----------------|
| `docs/` | Learner-facing conceptual documentation |
| `labs/` | Executable, locally-runnable implementations |
| `infrastructure/` | Shared runtime services (Docker, Ollama, DBs) |
| `meta/` | Build system (session state, system design, standards, workflow) |

---

## docs/

One folder per module plus a `reference/` folder for cross-module content.

```text
docs/
├── reference/                    ← cross-module reference content (no labs)
│   └── glossary.md
├── llm-fundamentals/
├── llm-apis/
├── prompt-engineering/
├── structured-outputs/
├── rag/
├── memory-context/
├── ai-agents/
├── frameworks-tools/
├── ai-java/
├── evaluation-testing/
├── safety-guardrails/
├── performance-optimization/
├── deployment-scaling/
├── observability-mlops/
├── reference-architectures/
└── real-world-projects/
```

### docs/reference/

Contains cross-module reference material. Not a learning module — no frontmatter,
no labs, no module sequence. Content here is consulted, not studied in order.

| File | Purpose |
|------|---------|
| `glossary.md` | Canonical definitions for all concepts used across modules |

### Internal structure per module

```text
docs/<module-name>/
├── README.md                     ← type: step-readme
├── <topic>.md                    ← type: topic (one file per concept)
├── architecture.md               ← type: architecture
├── implementation-reference.md   ← type: implementation-reference
└── validation.md                 ← type: validation
```

### Module reference-architectures exception

`reference-architectures` replaces `architecture.md` with `reference-architecture.md`
given its purpose is to document full system architectures, not a single module architecture.

---

## labs/

Mirror structure of `docs/` modules. No `reference/` equivalent.

```text
labs/
├── llm-fundamentals/
├── llm-apis/
├── prompt-engineering/
├── structured-outputs/
├── rag/
├── memory-context/
├── ai-agents/
├── frameworks-tools/
├── ai-java/                      ← README only (see note)
├── evaluation-testing/
├── safety-guardrails/
├── performance-optimization/
├── deployment-scaling/
├── observability-mlops/
├── reference-architectures/
└── real-world-projects/
```

### Note on ai-java

Module `ai-java` is documentation-only. The lab folder exists for structural
consistency but contains only a README explaining that no labs are planned for this module.

### Internal structure per module

```text
labs/<module-name>/
├── README.md                     ← type: lab-readme
├── lab-<n>/
│   ├── README.md
│   ├── main.py
│   └── requests.http             ← only for FastAPI labs
└── shared/                       ← utilities shared across labs in this module
```

### Module real-world-projects exception

```text
labs/real-world-projects/
└── <project-name>/
    ├── config/
    ├── src/<project-name>/
    └── tests/
```

---

## infrastructure/

```text
infrastructure/
├── README.md
├── docker-compose.yml            ← profiles: light | full
└── .env.example
```

| Profile | Services |
|---------|----------|
| `light` | Ollama (mistral), Open WebUI |
| `full`  | light + ChromaDB |

---

## meta/

Repository operating system. Do not modify without explicit instruction.

```text
meta/
├── README.md
├── session/
│   ├── PROJECT_STATUS.md         ← project progress tracker
│   ├── SESSION-CONTEXT.md
│   └── review-cache/             ← temporary review files (not committed)
├── standards/
│   ├── frontmatter/
│   │   └── frontmatter-spec.md
│   ├── writing/
│   │   ├── writing-style.md
│   │   └── lab-code-style.md
│   ├── templates/
│   │   ├── topic-scaffold.md
│   │   ├── step-readme-scaffold.md
│   │   ├── architecture-scaffold.md
│   │   ├── reference-architecture-scaffold.md
│   │   ├── implementation-reference-scaffold.md
│   │   ├── validation-scaffold.md
│   │   ├── lab-entry-readme-scaffold.md
│   │   └── lab-individual-readme-scaffold.md
│   ├── validation/
│   │   ├── docs-checklist.md
│   │   └── labs-checklist.md
│   └── review/
│       └── review-protocol.md
├── system-design/
│   ├── REPOSITORY_LAYOUT.md
│   └── DOCS_LABS_MAP.md
└── workflow/
    └── CLAUDE-CODE-WORKFLOW.md
```

### meta/session/review-cache/

Temporary storage for review reports generated by `/review-doc`.
Used by `/fix-doc` to load the previous review without requiring an active session.
This folder is excluded from git — see `.gitignore`.

---

## .claude/commands/

Custom slash commands for Claude Code. Each file is a markdown prompt
invokable with `/command-name` from the Claude Code CLI.

```text
.claude/commands/
├── write-doc.md
├── write-module.md
├── review-doc.md
├── fix-doc.md
├── design-labs.md
└── write-lab.md
```

---

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Module folders | `kebab-case` | `rag`, `frameworks-tools` |
| Doc files | `kebab-case.md` | `retrieval-strategies.md` |
| Lab folders | `lab-kebab-case` | `lab-retrieval-playground` |
| Shared utilities | `shared/` | `labs/rag/shared/` |
| Frontmatter `id` | `<module>-<concept>` | `rag-retrieval-strategies` |
| Review cache files | `<filename>.review.md` | `retrieval-strategies.review.md` |

Rules:
- All names in English
- No spaces, no uppercase
- No numeric prefixes — module order is defined in `DOCS_LABS_MAP.md` and `README.md`
- The `lab-` prefix distinguishes lab folders from `shared/` within a module
- Doc filenames are never prefixed with numbers

---

## Constraints

- Every file under `docs/<module>/` must include valid frontmatter
- Files under `docs/reference/` do not require module frontmatter
- Every lab folder must contain a `README.md`
- `docs/` and `labs/` use identical module folder names
- No content may be placed outside the defined layer structure
- `meta/` must not contain tutorial content
- `infrastructure/` must not contain lab-specific code
- `meta/session/review-cache/` must not be committed to git
