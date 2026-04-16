# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- `memory-context` module: complete — docs ✅, shared module ✅, all 5 labs ✅
- Next module: `ai-agents` — write-module ai-agents

## Recent decisions

- `SESSION-CONTEXT.md` is a compact portable briefing — rewritten each session, not accumulated
- `module-integration` lab type added — one per module tied to `architecture.md`, named `lab-integration`
- MCP integrated without new module: `mcp.md` in `ai-agents`, `lab-mcp-server`, reference architecture, real-world project
- `corpus/` is per-module technical knowledge base, independent of docs/, deeper than docs content
- Modules with required integration lab: `structured-outputs`, `rag`, `memory-context`, `evaluation-testing`, `safety-guardrails`, `performance-optimization`, `observability-mlops`, `ai-agents`
- ChromaDB `PersistentClient` used for cross-session persistence in labs — no Docker beyond `light` profile

## Next task

```
/write-module ai-agents
```
