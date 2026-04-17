# lab-individual-readme-scaffold.md

## Purpose

This template defines the structure for individual lab README files:

```text
labs/<module>/lab-<name>/README.md
```

Each section is mandatory unless marked optional.

---

## Frontmatter (MANDATORY)

```yaml
---
id: "lab-<name>"
title: "<Lab Title>"
type: "lab-readme"
step: "<module-name>"
path: "labs/<module>/lab-<name>/README.md"
status: "draft"
level: "foundational | intermediate | advanced"

concepts:
  - "<concept-1>"
  - "<concept-2>"

prerequisites:
  - "docs/<module>/<topic>.md"

related:
  - "docs/<module>/architecture.md"

summary: "<One sentence: what the lab implements and what it demonstrates.>"
---
```

---

## Navigation

[Labs](../../README.md) / [<Module Name> Labs](../README.md) / <Lab Title>

---

## Overview

What this lab implements, what the learner will observe, and what is explicitly out of scope.

---

## Concepts

Table mapping each concept demonstrated to where it appears in the code.

| Concept | Where it appears |
|---------|-----------------|
| `<concept>` | `<function or variable name>` — one-line description |

---

## Setup

Infrastructure and dependency commands required before running the lab.

```bash
docker-compose --profile <profile> up -d
pip install <dependencies>
```

---

## Run

```bash
cd labs/<module>/lab-<name>
python main.py
```

Environment variable overrides if applicable.

---

## Expected Output

Annotated sample output showing what a successful run produces.
Use `...` to omit repetitive lines. Annotate non-obvious values inline.

```
[turn 01] tokens: 87 / 7220 (remaining: 7133) | ok
...
[turn NN] *** KEY EVENT: description ***
...
Final result line
```

---

## What to observe

Interpretive guidance — what to actively look for while the lab runs.
Focus on behavioral differences, not just that the script completed.

- What changes as the lab progresses (e.g. token count, output format, retrieval distance)
- What signals indicate the concept is working correctly
- What to compare across runs or configurations
- What failure looks like even when the script exits cleanly

Do not just read the final result — observe the intermediate outputs.

---

## Concepts verified

Checklist of what a successful run confirms.

- [ ] `<concept-1>` — observable as `<what to look for>`
- [ ] `<concept-2>` — observable as `<what to look for>`

---

## Failure case

Active experiment: modify `main.py` at the marked `# FAILURE CASE` block and re-run.

- **What to change:** `<specific modification>`
- **Expected degradation:**
  - `<symptom 1>`
  - `<symptom 2>`

Restore the original values after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| `<service>` | `<what it does in this lab>` |
