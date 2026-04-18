# topic-scaffold.md

## Frontmatter (MANDATORY)

```yaml
---
id: "<module>-<topic-name>"
title: "<Human-readable title>"
type: "topic"
step: "<module-name>"
path: "docs/<module-name>/<topic-name>.md"
status: "draft"
level: "foundational | intermediate | advanced"

concepts:
  - "<concept-1>"
  - "<concept-2>"

prerequisites:
  - "<module or doc>"

next:
  - "<next topic or module>"

related:
  - "<related topic>"

implementation_refs:
  - "labs/<module>/lab-<n>"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "<One-sentence explanation of the topic>"
---
```

---

# <Title>

## Navigation

[Docs](../README.md) / [<Module Name>](README.md) / <Title>

---

## 1. Intuition

Provide an immediate mental model. No heavy technical language yet.

---

## 2. Explanation

Structure this section in three parts:

**2.1 Why** — the design decision and the problem this concept solves.

**2.2 How** — phases or mechanisms with conceptual grounding. Causal, not descriptive.

**2.3 Code example** — minimal and readable. Include a comment referencing the lab:

```python
# See: labs/<module>/lab-<n>/main.py
```

---

## 3. Table (MANDATORY)

A synthesis table: comparison, component breakdown, input/output mapping, or trade-offs.
Must compress information, not decorate.

---

## 4. Engineering Implications

How this concept affects system design. Include trade-offs and real-world constraints.

---

## 5. Implementation Connection

What the lab demonstrates and what to observe.
Must reference `implementation_refs`.

---

## 6. Failure Modes and Limitations

At least one limitation or failure condition. Avoid presenting the concept as universally valid.

---

## 7. Summary

Restate the core idea concisely. Connect to system usage.
