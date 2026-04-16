# SESSION-CONTEXT.md

Portable briefing for cross-tool handoff. Rewritten at the end of every session — not accumulated.

---

## Current state

- `ai-agents` module complete: 9 docs + 6 labs, all validated (PASS)
- `labs/README.md` updated: devcontainer section added, ai-agents row complete
- `post-create.sh` updated: installs all 7 modules
- Every active module has `requirements.txt` + `.env.example`
- Next module: `frameworks-tools` (not started)

## Recent decisions

- One `requirements.txt` per module; `post-create.sh` installs all — devcontainer is the runtime
- When adding a new module: create `requirements.txt`, `.env.example`, and add `-r` line to `post-create.sh`
- MCP labs are async (`asyncio.run`); shared `loop.py` stays synchronous
- Each MCP lab owns its own `server.py` — no cross-lab file dependencies

## Next task

`/write-module frameworks-tools`
