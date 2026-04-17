# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- Fase 5 completada: Navigation breadcrumb + §11 Engineering Takeaways añadidos a los 9 `docs/<module>/README.md`
- Perfil `light` → `foundational` corregido en §7 de los 3 módulos foundational (llm-fundamentals, llm-apis, prompt-engineering)
- Rama activa: `retrofit/modules-1-9` (creada por el usuario antes de comenzar fase 5)
- Siguientes: Fase 6 (retrofit labs/ módulos 1–9 para perfil foundational/intermediate) + /audit-module post-retrofit

## Recent decisions

- Engineering Takeaways es §11 en step-readme, inline, con estructura nivel-aware según scaffold
- Intermediate modules incluyen columna "When it breaks" en la tabla de trade-offs; foundational no
- Foundational modules omiten §Operational Considerations (per scaffold guidance)
- Perfiles `light` → `foundational` corregidos también en docs/ README §7 (no solo en labs/)

## Next task

Fase 6: retrofit labs/ — actualizar `.env.example`, `main.py` comments y `README.md` de cada lab para reflejar `foundational`/`intermediate` en lugar de `light`/`full`. Comenzar por `labs/llm-fundamentals/` y avanzar en orden de módulo.
