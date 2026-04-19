# Dist

Produce a clean learner-facing distribution of the repository in `dist/`.

1. Delete `dist/` if it exists, then recreate it
2. Copy into `dist/`: `docs/`, `labs/`, `infrastructure/`, `README.md`, `.devcontainer/`, `.env.example`
3. Do NOT copy: `CLAUDE.md`, `.claude/`, `meta/`, `.work/`, `meta/session/reports/`, `.gitignore`
4. In `dist/README.md`, remove any references to `CLAUDE.md`, `.claude/`, or `meta/`
5. Verify all internal links in `dist/` resolve correctly within the dist tree
