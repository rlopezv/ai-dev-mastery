# step-readme-scaffold.md

## Frontmatter (MANDATORY)

```yaml
---
id: "<step>-readme"
title: "<Step Name>"
type: "step-readme"
step: "<NN-step-name>"
path: "docs/<NN-step-name>/README.md"
status: "draft"
level: "foundational | intermediate | advanced"

concepts:
  - "<core-concept-1>"
  - "<core-concept-2>"

prerequisites:
  - "<previous step or doc>"

next:
  - "<first topic of this step>"

related:
  - "<related step or topic>"

implementation_refs:
  - "labs/<step>/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Introduces the scope and structure of this step."
---
```

---

# <Module Name>

## Navigation

[Docs](../README.md) / <Module Name>

---

## 1. Overview

What this step is about, why it matters, and what capability it unlocks.

---

## 2. Scope

What is covered and what is NOT covered.

---

## 3. Key Concepts

The core ideas introduced in this step.

---

## 4. Concept Map

Relationships between concepts. Diagram preferred; structured list as fallback.

---

## 5. Learning Flow

Order of topics and dependencies between them.

---

## 6. Documentation Structure

```text
docs/<step>/
├── README.md
├── <topic-1>.md
├── <topic-2>.md
├── architecture.md
├── implementation-reference.md
└── validation.md
```

---

## 7. Labs Overview

| Lab | Purpose |
|-----|---------|
| lab-01 | observation |
| lab-02 | implementation |

---

## 8. How to Use This Step

Recommended path and any optional paths.

---

## 9. Relationship to Other Steps

What comes before and what comes after in the roadmap.

---

## 10. Next Steps

Direct link to the first topic or next step.

---

## 11. Engineering Takeaways

Architect-oriented synthesis. Focus on what to retain and apply, not on what to learn step by step.
Level contract: `meta/system-design/LEVEL_MODE.md`.

### What This Adds

- **Foundational:** What core capability does this introduce? What problem does it solve at a basic level? Why is it relevant in AI-powered systems? Keep this simple and concrete.
- **Intermediate:** What subsystem capability does this introduce? What components are added? How does this extend previous modules? Be explicit about system-level changes.
- **Advanced:** What architectural capability does this enable? How does it change system design or operation? What new responsibilities does it introduce (evaluation, monitoring, scaling)?

### Engineering Trade-offs

**Foundational** — basic trade-offs, 2–3 rows, no "When it breaks" column:

| Decision | Benefit | Cost |
|----------|---------|------|
|          |         |      |

**Intermediate / Advanced** — real design decisions with failure conditions:

| Decision | Benefit | Cost | When it breaks |
|----------|---------|------|----------------|
|          |         |      |                |

### When NOT to Use This

List scenarios where this approach is unnecessary, harmful, or premature.

- **Foundational:** When a simpler or deterministic solution is sufficient. When the problem does not require AI capabilities.
- **Intermediate:** When operational complexity outweighs the benefit. When required prerequisites (data, infra, observability) are missing.
- **Advanced:** When system complexity is not required. When operational overhead cannot be supported. When evaluation and monitoring cannot be implemented properly.

### Common Failure Modes

Recurring failure patterns an architect should recognize and diagnose.

- **Failure:** \<what goes wrong\>
  **Cause:** \<why it happens\>
  **Signal:** \<observable symptom\>

- **Foundational:** 2–3 basic patterns. Focus on simple misuse or misconfiguration.
- **Intermediate:** Integration failures across components. Data quality, retrieval, orchestration, state handling.
- **Advanced:** System-level failures. Silent degradation, evaluation gaps, scaling bottlenecks, cost explosion, architecture drift.

### What Changes vs Traditional Systems

The key architectural or mental shift introduced by this module.

- **Foundational:** Non-deterministic outputs vs deterministic logic. Prompt/input design vs fixed code paths. Behavior shaped by input rather than strict rules.
- **Intermediate:** Probabilistic pipelines vs deterministic flows. Integration of loosely coupled components. Emergent behavior from composition. Where traditional intuition fails.
- **Advanced:** Evaluation as a first-class concern. Probabilistic correctness vs binary correctness. Continuous validation vs static testing. Difficulty of strict guarantees.

### Operational Considerations

> Omit for foundational modules.

What is required to run this in practice:
- Required components (services, stores, tools)
- What needs to be observable (inputs, outputs, intermediate steps)
- Main sources of latency and cost
- What is required to debug issues
- Scaling constraints

### Minimal Adoption Heuristic

**Use this when:**
- \<condition specific to this module's capability\>

**Avoid this when:**
- \<condition specific to this module's constraints\>
