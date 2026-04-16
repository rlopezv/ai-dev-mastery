You are performing a system-level audit of a repository that is built and maintained using Claude Code.

Your task is to evaluate the role and necessity of the file:

meta/session/SESSION-CONTEXT.md

---

## Context

* The repository uses Claude Code as the primary execution agent

* Claude Code maintains internal context across tasks

* The repository already defines:

  * canonical structure (`REPOSITORY_LAYOUT.md`)
  * docs↔labs alignment (`DOCS_LABS_MAP.md`)
  * project status (`PROJECT_STATUS.md`)
  * workflow (`CLAUDE-CODE-WORKFLOW.md`)

* `SESSION-CONTEXT.md` is currently used as a human-readable continuity log between sessions

---

## Objective

Determine whether `SESSION-CONTEXT.md`:

1. Adds real value to the system
2. Is redundant with Claude Code's internal context handling
3. Introduces ambiguity or maintenance overhead
4. Should be:

   * kept as-is
   * simplified
   * redefined
   * removed

---

## Evaluation Criteria

Analyze the file along these dimensions:

### 1. Functional Role

* What function does this file actually serve?
* Is that function already covered elsewhere?

### 2. Redundancy

* Does it duplicate:

  * Claude Code internal context?
  * PROJECT_STATUS.md?
  * WORKPLAN.md?

### 3. Risk

* Does it introduce:

  * conflicting interpretations?
  * stale information risk?
  * ambiguity in execution?

### 4. Dependency

* Does the system depend on it?
* What breaks if it is removed?

### 5. Cost vs Value

* Is the maintenance cost justified by its utility?

---

## Output Requirements

Provide a structured response with:

1. Clear classification:

   * essential
   * useful but optional
   * redundant
   * harmful

2. Recommendation:

   * keep / simplify / redefine / remove

3. Justification grounded in system behavior (not opinion)

4. If changes are recommended:

   * provide minimal viable modification (not redesign)

---

## Important Constraints

* Do NOT assume the file must exist
* Do NOT propose improvements unless justified
* Do NOT redesign the system
* Focus only on necessity and role

---

## Final Instruction

Be critical and precise.

This is not a documentation review.
This is a system design decision.
