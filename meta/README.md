# Meta — Estándares y plantillas

Este directorio contiene los estándares de calidad, plantillas y protocolos de revisión del repositorio.

## Contenido

```text
meta/
└── standards/
    ├── frontmatter/
    │   └── frontmatter-spec.md        ← contrato de frontmatter (obligatorio)
    ├── writing/
    │   ├── writing-style.md           ← guía de estilo de escritura
    │   ├── topic-template.md          ← plantilla para topics
    │   ├── step-readme-template.md    ← plantilla para README de módulo
    │   ├── architecture-template.md   ← plantilla para architecture.md
    │   ├── implementation-reference-template.md
    │   ├── validation-template.md     ← plantilla para validation.md
    │   └── lab-readme-template.md     ← plantilla para README de labs
    ├── validation/
    │   ├── docs-checklist.md          ← checklist de validación de docs
    │   └── lab-checklist.md           ← checklist de validación de labs
    └── review/
        └── review-protocol.md         ← protocolo de revisión
```

## Reglas fundamentales

- Todo fichero bajo `docs/` debe incluir frontmatter válido según `frontmatter-spec.md`
- Todo artefacto debe seguir la plantilla correspondiente en `writing/`
- Los checklists en `validation/` son la referencia para aprobar un artefacto

## Pendientes

- [ ] `writing-style.md` — completar con reglas acordadas
- [ ] `docs-checklist.md` — definir criterios de validación
- [ ] `lab-checklist.md` — definir criterios de validación de labs
- [ ] `review-protocol.md` — definir protocolo de revisión
- [ ] `reference-architecture-template.md` — template para módulo 15
