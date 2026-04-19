# Audit Module

Runs the full module audit in two explicit phases. Report format: `meta/standards/audit/audit-report-format.md`.
Check result states: PASS | FAIL | FIXED | PENDING | SKIP (see format spec for definitions).

---

## Phase 1 — Static

Structure, alignment, and glossary — no content reading required.

1. Read `meta/system-design/LEVEL_MODE.md` for the module's level policy
2. For each doc in `docs/<module>/`: apply SC-1 to SC-6, IQ-5, IQ-6
3. For each lab README in `labs/<module>/`: check required sections and optional/required alignment
4. Check docs↔labs alignment against `meta/system-design/DOCS_LABS_MAP.md`
5. Check all frontmatter cross-references point to real files
6. Fix any FAIL findings or flag for human review — for items that cannot be resolved without human input, append to `meta/session/PENDING.md` under `## Review`
7. Run `python .work/scripts/sync-frontmatter-status.py <module> review` to update frontmatter; verify output shows no unexpected WARN lines
8. Write `meta/audit/reports/<module>.audit.md` with Phase 1 results; mark cohesion and execution checks as PENDING
9. Update Overall Status to `STATIC_PASS | COHESION_PENDING | EXECUTION_PENDING` (use `EXECUTION_SKIP` for modules with no labs); for modules with labs, also append to `meta/session/PENDING.md` under `## Execute`

---

## Phase 2 — Cohesion

Reads content for correctness, pedagogy, and engineering quality.

1. For each doc in `docs/<module>/`: apply CQ-1 to CQ-5, PQ-1 to PQ-5, EQ-1 to EQ-5, IQ-1 to IQ-4, LC-1 to LC-5
2. Fix any FAIL findings or flag for human review — for items that cannot be resolved without human input, append to `meta/session/PENDING.md` under `## Review`
3. Run `python .work/scripts/sync-frontmatter-status.py <module> final` to update frontmatter; verify output shows no unexpected WARN lines
4. Append Phase 2 section to `meta/audit/reports/<module>.audit.md` — do not rewrite Phase 1
5. Update Overall Status to `STATIC_PASS | COHESION_PASS | EXECUTION_PENDING`

---

## Phase 2 — Finalization

Use after targeted `audit-doc` re-audits, not after a full Phase 2 run.

1. Read all Phase 2 rows in `meta/audit/reports/<module>.audit.md`
2. If all checks are PASS or FIXED (no FAIL, no PENDING) → update Overall Status to `STATIC_PASS | COHESION_PASS | EXECUTION_PENDING`
3. If any FAIL remains → leave Overall Status as `COHESION_PENDING` and list the failing checks

---

## Phase 3 — Execution

Requires live infrastructure: Ollama running, devcontainer active.

If infrastructure is not available in the current session: append this module to
`meta/session/PENDING.md` under `## Execute` and emit `HUMAN_ACTION_REQUIRED`. Do not proceed.

1. For each lab in `labs/<module>/`: run `python lab-<n>/main.py` and verify exit 0
2. Verify expected output matches what the lab README describes
3. Fix any lab failures or flag for human review — unfixable failures go to `meta/session/PENDING.md` under `## Review`
4. Fill in `## Phase 3 — Execution` in `meta/audit/reports/<module>.audit.md` — do not rewrite Phase 1 or Phase 2
5. Update Overall Status to `FULL_PASS`
6. Remove this module's `## Execute` entry from `meta/session/PENDING.md`
