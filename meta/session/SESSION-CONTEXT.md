# SESSION-CONTEXT.md

Update this file at the end of each working session to capture:
- decisions made
- files modified
- pending items for the next session

---

## Last session

**Date:** 2026-04-15
**Phase:** Infrastructure cleanup — devcontainer and docker-compose

### Completed

- `infrastructure/docker-compose.yml` — finalized: two profiles (`light`, `full`), `ollama-init` service handles model pulling (depends on `ollama` healthcheck), ChromaDB and Open WebUI included, all config via env vars
- `.devcontainer/devcontainer.json` — updated to reference `Dockerfile` and `post-create.sh`, `remoteEnv` aligned with docker-compose env vars
- `.devcontainer/post-create.sh` — simplified: removed Ollama wait loop and model pull (steps 2–3); only installs Python dependencies; model pulling is now the responsibility of `ollama-init` in docker-compose

### Key decision

The devcontainer is responsible only for the dev environment (Python deps).
Ollama lifecycle (start, model pull) is handled by docker-compose, which is
optional and run separately. The devcontainer does not depend on Ollama being up.

---

## Pending — next session

### 1. Continue module content (Fase 3)

`llm-fundamentals` is complete. Next module: `llm-apis`.

Recommended task:
> `/write-module llm-apis`

### 2. Populate glossary incrementally

`docs/reference/glossary.md` is in progress (`🔄`).
Add entries as each module is written — never in one pass.

### 3. Infrastructure: verify docker-compose profiles before next lab

Run `docker compose --profile light up` and confirm `ollama-init` pulls the
model correctly before writing the first `llm-apis` lab.
