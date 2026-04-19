# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- Rama activa: `meta/editorial-reform`
- Revisión del sistema de auditoría y del procedimiento editorial completada
- Todos los cambios pendientes de commitear (lo hace el usuario)

## Recent decisions

- PENDING = deferred; SKIP = genuinely not applicable
- `/audit-doc` no toca Overall Status — solo rows + frontmatter
- Phase 2 Finalization = procedimiento ligero post-`/audit-doc` para recalcular Overall Status
- `sync-frontmatter-status.py <module> <review|final>` — script bulk-update frontmatter
- `audit-doc` determina la fase por `status` del doc (`draft`→Phase 1, `review`→Phase 2)
- `review-protocol.md` ahora cubre 7 categorías (añadida §1.6 Integration para IQ-1..4)
- `fix-doc` step 7: PROJECT_STATUS update condicional a que avance el `status` del doc

## Archivos modificados (sin commitear)

- `CLAUDE.md`
- `meta/standards/audit/audit-report-format.md`
- `meta/standards/review/review-protocol.md`
- `meta/workflow/CLAUDE-CODE-WORKFLOW.md`
- `meta/session/PROJECT_STATUS.md`
- `meta/session/WORKPLAN.md`
- `.work/scripts/migrate-audit-reports.py`
- `.work/scripts/sync-frontmatter-status.py`
- `meta/audit/reports/` (9 reports migrados)

## Next task

Revisión del proceso editorial completo para cerrarlo — revisar writing-style.md,
lab-code-style.md, templates y su alineamiento con los procedimientos actualizados.
