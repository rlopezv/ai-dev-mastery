# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- Fase 5 completada y commiteada: Navigation breadcrumb + §11 Engineering Takeaways en los 9 `docs/<module>/README.md`
- Perfil `light` → `foundational` corregido en §7 de los 3 módulos foundational
- Rama activa: `retrofit/editorial-reform`

## Recent decisions

- Engineering Takeaways es §11 inline en step-readme; intermediate incluye columna "When it breaks"; foundational omite Operational Considerations
- `/audit-module` se ejecuta después de Fase 6 (labs + docs forman una unidad de auditoría)
- No commitear por cuenta propia — solo `git add` y proponer el mensaje

## Next task

Fase 6: retrofit `labs/` — dos tipos de cambios:
1. Profile rename: `light` → `foundational`, `full` → `intermediate` en 8 `labs/<module>/README.md`, ~20 `labs/<module>/lab-<n>/README.md` individuales, y `.env.example` donde aplique
2. Navigation breadcrumbs: `[Labs](../README.md) / <Module> Labs` en module-level READMEs; `[Labs](../../README.md) / [<Module> Labs](../README.md) / <Lab Title>` en lab-level READMEs
