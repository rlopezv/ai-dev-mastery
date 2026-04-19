# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- Rama activa: `meta/procedure-extraction`
- Procedure extraction completo: 13 ficheros en `meta/workflow/procedures/`, CLAUDE.md §9 reducido a tabla, 13 command files actualizados, `REPOSITORY_LAYOUT.md` y `CLAUDE-CODE-WORKFLOW.md` actualizados
- llm-fundamentals: COHESION_PASS. 8 módulos restantes en COHESION_PENDING.

## Recent decisions

- Bug en `sync-frontmatter-status.py` corregido: quoted YAML status values
- Separación política (CLAUDE.md) / procedimiento (`meta/workflow/procedures/`) / invocación (`.claude/commands/`)
- `.claude/commands/` son ahora one-line delegators; los pasos reales están en `meta/workflow/procedures/`
- `REPOSITORY_LAYOUT.md` actualizado: árbol `meta/workflow/procedures/`, `PENDING.md` en session, descripción `.claude/commands/`

## Next task

Commit + PR de la rama `meta/procedure-extraction` a master.
Luego continuar con `/audit-module llm-apis`.
