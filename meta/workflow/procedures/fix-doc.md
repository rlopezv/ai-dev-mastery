# Fix a Document

1. Check if `meta/session/reports/<filename>.review.md` exists and read it
2. If no cached review exists, perform the review internally first (see `meta/workflow/procedures/review-doc.md`)
3. Apply fixes to the document
4. Check any new concepts introduced by fixes against `docs/reference/glossary.md`; add missing entries; if an existing entry conflicts with the document's usage, append to `meta/session/PENDING.md` under `## Decide` rather than modifying the glossary
5. Re-validate with `meta/standards/validation/docs-checklist.md`
6. Write the corrected document to the target path
7. Delete the report file if it exists
8. Update `meta/session/PROJECT_STATUS.md` only if the fix advances the document's `status` (e.g., from `draft` to `review`)
9. Update `meta/session/SESSION-CONTEXT.md`
