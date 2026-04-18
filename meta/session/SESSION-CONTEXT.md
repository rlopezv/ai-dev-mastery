# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- Rama activa: `retrofit/editorial-reform`
- Auditoría foundational completa (3/3): `llm-fundamentals`, `llm-apis`, `prompt-engineering`
- Auditoría intermediate en progreso (3/6 completos): `structured-outputs`, `rag`, `memory-context` — todos STATIC_PASS / EXECUTION_PENDING
- Módulos intermediate pendientes de auditar (3): `ai-agents`, `frameworks-tools`, `ai-java`

## Recent decisions

- **rag — correcciones post-auditoría:**
  - `lab-integration` añadido en todos los lugares que faltaban: `labs/README.md`, `labs/rag/README.md` (frontmatter `implementation_refs`, `summary`, §1, §3, §4, §9), `docs/rag/README.md`, `docs/rag/validation.md` (§1, §4, §7)
  - `lab-chunking-strategies/main.py` refactorizado para usar `load_corpus()` de `shared/config.py` (clave `'source'` en lugar de `'filename'` local)
  - Patrón aprendido: ante cualquier cambio estructural (añadir/quitar lab), hacer grep de contadores y listas en todos los archivos afectados antes de cerrar la tarea
- **memory-context audit:** STATIC_PASS. 3 glossary entries added: `memory-types`, `memory-retrieval`, `summarization-based-compression`.
- Execution checks remain PENDING para todos los módulos auditados — requiere Ollama + ChromaDB en vivo.

## Next task

Auditar módulo `ai-agents` — mismo proceso: leer LEVEL_MODE, validar docs + labs, check alineación DOCS_LABS_MAP, check IQ-6 glossary, aplicar fixes, escribir `meta/audit/reports/ai-agents.audit.md`.
