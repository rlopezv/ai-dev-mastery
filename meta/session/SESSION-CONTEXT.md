# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- `frameworks-tools` module fully complete: 9 docs + 5 labs + workflow-tools.md, all validated PASS
- `ai-java` module fully complete: 8 docs, all validated PASS; concept-only (no labs)
- `ai-java` ampliado post-cierre: Quarkus/Micronaut/Dropwizard cubiertos en java-ai-landscape.md y langchain4j.md
- README.md, docs/README.md y labs/README.md actualizados a módulos 07–09
- Next module after meta/ work: `evaluation-testing` (module 10, Advanced)

## Next task — meta/ review + housekeeping (do this before evaluation-testing)

### 1. meta/ standards review (6 items)

Verificar y corregir donde haya gaps:

1. `meta/system-design/REPOSITORY_LAYOUT.md` — refleja la estructura de tres READMEs (root / docs/ / labs/)
2. Solapamiento entre READMEs — templates definen claramente qué va en cada nivel
3. Convención `corpus/` — verificar en `lab-code-style.md` §9, `DOCS_LABS_MAP.md` y `labs-checklist.md`
4. Regla de idioma — añadir a `lab-code-style.md` si no está (ya está en CLAUDE.md y writing-style.md)
5. Status columns — verificar que PROJECT_STATUS.md es fuente autoritativa sin contradicciones con los READMEs
6. `infrastructure/README.md` — descrito correctamente en REPOSITORY_LAYOUT.md y linkeado desde labs/README.md

### 2. Migrar memorias locales a CLAUDE.md

Las memorias en `~/.claude/` son locales a la máquina. Migrar a `CLAUDE.md` como sección `## Session conventions`:

- Actualizar README.md, docs/README.md y labs/README.md al cerrar cada módulo
- `implementation-reference` contiene patrones de diseño, no setup operacional
- Un `requirements.txt` por módulo; `post-create.sh` los instala todos

Después borrar los ficheros de memoria redundantes en `~/.claude/projects/`.

### 3. project_meta_review_pending memory

Borrar `project_meta_review_pending.md` de memoria una vez completada la revisión de meta/.

## Recent decisions

- `ai-java` es concept-only: sin JDK/Maven en devcontainer; labs/ai-java/README.md documenta el rationale
- java-ai-landscape.md incluye tabla "Application framework → AI integration path" (Spring Boot, Quarkus, Micronaut, Dropwizard, standalone)
- langchain4j.md incluye bloque "Framework integration" + ejemplo Quarkus (@RegisterAiService) + tabla Maven por framework
- Los tres READMEs de nivel (root / docs/ / labs/) deben actualizarse al cerrar cada módulo
