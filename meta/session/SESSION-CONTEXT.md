# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- Reforma editorial completada en rama `retrofit/editorial-reform`
  - Fase 6: profile rename (`light`→`foundational`, `full`→`intermediate`) + breadcrumbs en 46 labs
  - Fase 7a: H1 añadido/corregido en 129 archivos vía `add_h1.py`
  - Fase 7b: breadcrumbs añadidos en 74 docs/labs vía `add_breadcrumbs.py`
  - Total: 131 archivos con navegación, 0 bloqueados, 11 sin frontmatter (legítimos)
- Scripts en `.work/scripts/`: `add_h1.py`, `add_breadcrumbs.py`, `audit_labs_breadcrumbs.py`
- Checklist actualizado: SC-6 (H1 Critical en docs), LS-7 + LS-8 (frontmatter + H1 Critical en labs)
- Templates actualizados: H1 rule añadida, paths corregidos (`../README.md`)

## Recent decisions

- Scripts bulk: proponer en `.work/scripts/`, usuario ejecuta localmente — no Claude vía Bash
- Dry-run → apply → dry-run es el patrón de validación para scripts de bulk edit
- 11 archivos sin frontmatter son legítimos: `docs/README.md`, `docs/guides/`, `docs/reference/glossary.md`, `labs/README.md`, `labs/common/shared/`, corpus files

## Next task

Fase 8: ejecutar `/audit-module` para cada módulo marcado ✅ en `meta/session/PROJECT_STATUS.md` y consolidar hallazgos en `meta/session/reports/`.
