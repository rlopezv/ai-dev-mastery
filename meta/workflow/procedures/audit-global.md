# Audit (Global)

1. Run "Audit module" Phase 1 for each module marked ✅ in `meta/session/PROJECT_STATUS.md` (see `meta/workflow/procedures/audit-module.md`)
2. Check cross-module prerequisites form a valid DAG (no circular dependencies)
3. Check terminology consistency across modules against `docs/reference/glossary.md`
4. Check `README.md`, `docs/README.md`, and `labs/README.md` are in sync with `PROJECT_STATUS.md`
5. Write persistent report to `meta/audit/reports/global.audit.md`
6. Report as structured observations — requires human review, not PASS/FAIL
