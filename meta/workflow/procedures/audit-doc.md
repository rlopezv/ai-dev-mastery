# Audit a Document

Audits a single document and updates its `status` in frontmatter and its rows in the module
audit report. Use for targeted re-audits after fixes or to advance a document through phases.

**Does NOT update Overall Status** — that is the exclusive responsibility of `audit-module`.
After using `audit-doc` on multiple documents, run "Phase 2 — Finalization" (see
`meta/workflow/procedures/audit-module.md`) to recalculate Overall Status without re-auditing.

1. Read the document
2. Determine the audit phase from the document's current `status`: `draft` → apply Phase 1; `review` → apply Phase 2 (cohesion). Override if the user specifies a phase explicitly.
3. Phase 1: apply SC-1 to SC-6 and IQ-5, IQ-6 from `meta/standards/validation/docs-checklist.md`
4. Phase 2 (cohesion): apply CQ-1 to CQ-5, PQ-1 to PQ-5, EQ-1 to EQ-5, IQ-1 to IQ-4, LC-1 to LC-5
5. Update `status` in the document's frontmatter:
   - Static checks all PASS → `status: review`
   - Cohesion checks all PASS → `status: final`
6. Update the document's rows in `meta/audit/reports/<module>.audit.md` — do not touch Overall Status
