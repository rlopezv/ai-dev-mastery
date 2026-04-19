# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- Rama activa: `retrofit/editorial-reform`
- Auditoría estática completa para los 9 módulos intermediate (llm-fundamentals → ai-java): todos STATIC_PASS / EXECUTION_PENDING (ai-java: STATIC_PASS sin labs)
- Glossary entries añadidas en esta sesión: 13 términos en 4 módulos (memory-context ×3, ai-agents ×3, frameworks-tools ×4, ai-java ×0)
- Correcciones rag aplicadas: lab-integration añadido en labs/README.md, labs/rag/README.md (×6 secciones), docs/rag/validation.md; lab-chunking-strategies refactorizado para usar shared load_corpus() con clave 'source'

## Recent decisions

- **Scope de auditoría estática vs. cohesión:** la pasada actual cubre solo validación estática (frontmatter, H1, glossary IQ-6, DOCS_LABS_MAP, cross-refs, secciones de labs). La cohesión (code-doc alignment, lab outputs) queda para segunda pasada con /audit-module.
- **Patrón aprendido:** antes de cerrar cualquier tarea estructural (añadir/quitar lab), hacer grep de contadores y listas en todos los archivos afectados. Evita ciclos de re-review.

## Next task

Segunda pasada con `/audit-module` aplicando cohesión completa — empezar por el módulo que el usuario indique. Execution checks siguen PENDING (requieren Ollama + ChromaDB en vivo).
