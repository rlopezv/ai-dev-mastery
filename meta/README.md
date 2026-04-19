# meta/

## Purpose

`meta/` contains the **internal build system** used to design, validate, and evolve this repository.

It defines:

* repository structure (system-design)
* alignment between documentation and labs
* editorial and implementation standards
* workflow for working with Claude Code
* session state and progress tracking

This directory is **part of the authoring process only**.

It is **not included in the final learner-facing repository**, which consists of:

* `docs/`
* `labs/`
* `infrastructure/`

---

## Structure

```text
meta/
├── audit/
│   └── reports/                       # persistent audit reports (committed)
│       ├── <module>.audit.md          # one per audited module
│       ├── global.audit.md            # cross-module audit output
│       └── enrich.md                  # enrich run output
├── session/                           # execution state and continuity
│   ├── PROJECT_STATUS.md              # project progress tracker (canonical)
│   ├── SESSION-CONTEXT.md             # cross-session briefing
│   ├── WORKPLAN.md                    # phase planner for pending modules
│   └── reports/                       # ephemeral review cache — NOT committed
├── system-design/                     # canonical structure and alignment rules
├── standards/                         # contracts, templates, and validation rules
│   ├── audit/
│   │   └── audit-report-format.md    # canonical format for audit reports
│   ├── frontmatter/
│   │   └── frontmatter-spec.md        # frontmatter contract (mandatory)
│   ├── writing/
│   │   ├── writing-style.md           # writing style guide
│   │   ├── topic-guide.md             # topic writing guide
│   │   ├── step-readme-guide.md       # module README writing guide
│   │   ├── architecture-guide.md      # architecture writing guide
│   │   ├── implementation-reference-guide.md
│   │   ├── validation-guide.md        # validation writing guide
│   │   ├── lab-entry-readme-guide.md
│   │   └── lab-individual-readme-guide.md
│   ├── validation/
│   │   ├── docs-checklist.md          # docs validation checklist
│   │   └── labs-checklist.md          # labs validation checklist
│   └── review/
│       └── review-protocol.md         # human-facing diagnostic protocol
└── workflow/                          # operational model (Claude Code usage)
```

---

## Canonical vs Operational Files

### Canonical (source of truth)

These files define the system and MUST be consistent:

* `system-design/REPOSITORY_LAYOUT.md`
  → defines repository structure

* `system-design/DOCS_LABS_MAP.md`
  → defines module sequence and docs↔labs alignment

* `session/PROJECT_STATUS.md`
  → defines overall project completion status

---

### Operational (non-canonical)

These files support execution but are not authoritative:

* `session/WORKPLAN.md`
  → internal execution tracking (manual)

* `session/SESSION-CONTEXT.md`
  → session continuity and pending alignment

* `workflow/CLAUDE-CODE-WORKFLOW.md`
  → operational guidance for working with Claude Code

---

## Standards Layer

`meta/standards/` defines the **normative layer of the build system**.

It includes:

* **contracts**
  → frontmatter specification

* **templates**
  → reusable structures for docs and labs

* **validation**
  → checklists to enforce quality

* **review**
  → protocols for systematic review

These rules are **expected to be followed by both humans and Claude Code** during content creation.

---

## Usage Model

* `meta/` is used during **content construction**
* `docs/`, `labs/`, and `infrastructure/` form the **final deliverable**
* `CLAUDE.md` defines how the agent interacts with this system

---

## Important

* `meta/` is required for authoring
* `meta/` is not required for learners
* `meta/` is excluded from the final distribution repository

---

## Design Principle

This repository is built using a **separation of concerns between construction and delivery**:

* **Build system** → `meta/`, `CLAUDE.md`, `.claude/`
* **Delivery system** → `docs/`, `labs/`, `infrastructure/`

This separation ensures:

* consistency during authoring
* clarity for learners
* clean final distribution
