# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- Lab hardening pass complete: all 25 labs across 6 modules updated
- Each individual lab README now has `## What to observe`, `## Concepts verified`, `## Failure case`
- Each `main.py` now has a `# FAILURE CASE` comment block at the relevant modification point
- New templates created: `lab-entry-readme-template.md` (module-level) + `lab-individual-readme-template.md` (per-lab)
- Next task: write `ai-agents` module

## Recent decisions

- `## What to observe` added to all lab READMEs (behavioral guidance, not just correctness)
- `## Concepts verified` uses checkboxes for learner verification
- `## Failure case` + `# FAILURE CASE` in `main.py` are required in all labs; must be consistent
- Template naming: `lab-entry-readme-template.md` = module README, `lab-individual-readme-template.md` = per-lab README
- DA-4 validation rule: `## Failure case` description must match `# FAILURE CASE` block in `main.py`

## Next task

```
/write-module ai-agents
```
