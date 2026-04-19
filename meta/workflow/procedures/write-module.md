# Write a Module (all docs for a module)

1. Read `meta/system-design/DOCS_LABS_MAP.md` for the module scope
2. Verify the module's declared level against `meta/system-design/LEVEL_MODE.md` — confirm allowed runtime, abstraction, and infrastructure
3. Write documents in this order: README → topics → architecture → implementation-reference → validation
4. Validate each document before writing the next (see `meta/workflow/procedures/write-doc.md`)
5. If the module requires components outside its default level profile, document the exception per LEVEL_MODE G-5 in the module README, `labs/<module>/README.md`, and `infrastructure/README.md`
6. Update `docs/reference/glossary.md` with all new concepts
7. Update `meta/session/PROJECT_STATUS.md`
8. Update `README.md`, `docs/README.md`, and `labs/README.md` with the new module (status, lab names, descriptions)
9. Update `meta/session/SESSION-CONTEXT.md`
