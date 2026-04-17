# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- Fases 1–4 del editorial reform completadas en rama `meta/editorial-reform`
- Fases 1–4 cubren: profile rename (foundational/intermediate), LEVEL_MODE integrado en meta/, Engineering Takeaways en scaffold, proceso consolidado en CLAUDE.md §9, nuevos comandos (write-labs, audit-module, audit, enrich, dist), breadcrumbs de navegación en todos los scaffolds, reports/ reemplaza review-cache/
- Siguiente: Fase 5 (retrofit docs/ módulos 1–9) + Fase 6 (retrofit labs/ módulos 1–9) en rama nueva
- Fase 7: módulo `evaluation-testing` (primer módulo Advanced)

## Recent decisions

- Perfiles renombrados: `light` → `foundational`, `full` → `intermediate`, `advanced` TBD progresivo
- LEVEL_MODE.md es un execution contract en meta/system-design/ — leído antes que DOCS_LABS_MAP
- Engineering Takeaways = sección §11 en step-readme (absorbe .work/engineering-takeaways/), no documento separado
- Slash commands son delegaciones finas — CLAUDE.md §9 es la única fuente de procedimientos
- meta/session/reports/ reemplaza review-cache/ — recibe informes de /review-doc, /audit-module, /audit, /enrich
- /dist genera dist/ con contenido learner-facing sin meta/, .claude/, CLAUDE.md
- Navegación vertical (breadcrumb al parent) en todos los scaffolds; navegación horizontal diferida a /enrich
- .work/ excluido de git; contenido absorbido (LEVEL_MODE → meta/, engineering-takeaways → scaffold)

## Next task

Crear rama `retrofit/modules-1-9` y ejecutar Fase 5: añadir `## Navigation` breadcrumb + `## 11. Engineering Takeaways` a los 9 `docs/<module>/README.md`. Después /audit-module para validar.
