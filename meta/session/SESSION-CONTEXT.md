# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- Template rename pass complete: 15 files renamed, 6 reference files updated
  - `templates/*-template.md` → `templates/*-scaffold.md` (8 files)
  - `writing/*-template.md` → `writing/*-guide.md` (7 files)
  - References updated in: `CLAUDE.md`, `meta/README.md`, `REPOSITORY_LAYOUT.md`, `design-labs.md`, `labs-checklist.md`, `SESSION-CONTEXT.md`
- Next: `/write-module ai-agents`

## Recent decisions

- `templates/` stores structural scaffolds (`*-scaffold.md`); `writing/` stores authoring guides (`*-guide.md`)
- `## What to observe`, `## Concepts verified`, `## Failure case` are mandatory in all lab READMEs
- `## Failure case` description must match `# FAILURE CASE` block in `main.py` (DA-4 rule)

## Next task

`/write-module ai-agents`
