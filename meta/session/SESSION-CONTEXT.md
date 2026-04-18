# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- Rama activa: `retrofit/editorial-reform`
- Auditoría de módulos **foundational completa** (3/3): `llm-fundamentals`, `llm-apis`, `prompt-engineering` — todos STATIC_PASS / EXECUTION_PENDING
  - Reports persistentes en `meta/audit/reports/`
- Módulos **intermediate pendientes de auditar** (6): `structured-outputs`, `rag`, `memory-context`, `ai-agents`, `frameworks-tools`, `ai-java`

## Recent decisions

- Patrón recurrente en cada módulo auditado:
  - `implementation-reference.md` tiene perfil `light` (legacy) → fix a `foundational`
  - Todos los lab READMEs individuales necesitaban restructuración al scaffold (secciones Concepts e Infrastructure ausentes)
- Glossary: entradas añadidas durante la auditoría — `### finish reason`, `### prompt pitfalls`, `### answer extraction`
- `audit.py` explícitamente diferido: se construye tras completar la auditoría manual de todos los módulos
- Niveles confirmados: foundational = `llm-fundamentals`, `llm-apis`, `prompt-engineering`; intermediate = los 6 restantes

## Next task

Iniciar auditoría de módulos intermediate, comenzando por `structured-outputs` — mismo proceso: docs + labs, static checks, fixes, report en `meta/audit/reports/structured-outputs.audit.md`.
