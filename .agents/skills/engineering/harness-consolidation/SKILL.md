---
name: harness-consolidation
description: Use when reducing a project to one agent harness.
---

# Harness Consolidation

Reduce a project to a single agent harness (Hermes) without breaking pipelines, subprojects, or dependencies. Everything is reversible: files go to a dated quarantine folder, never deleted.

## Standing rules
1. **Migrate before quarantining.** Port reusable content (agent roles, skill definitions, pipeline specs, command templates) into Hermes profile skills FIRST. Quarantine only what Hermes cannot use: harness config, harness-DSL scripts, other harnesses' agent definitions.
2. **Quarantine, never delete.** Dated folder under the project root: `.quarantine/<task>-<YYYY-MM-DD>/`. One `BATCH-N-MANIFEST.json` per batch (format in references/scan-recipe.md).
3. **Show the target list for approval before moving** — per subproject, each path + reason. The user approves batch by batch; do not bulk-move without the list being shown.
4. **Subprojects: never move whole.** Quarantine only the harness-specific files inside them (CLAUDE.md, .claude-plugin/, agents/, agents-codex/, other-harness skill variants). Keep code, .git, dependencies, SKILL.md, README.
5. **Check hidden dependencies before moving.** Grep the target harness's skills for references to files being moved (agent roles, scripts, home-dir paths like `~/.claude/...`). Migrate the referenced content and fix dead paths in the target skills — a role that exists only in the quarantined harness breaks every skill that launches it.
6. **Quarantine is not cleanup.** After moving: fix references in project docs, rebuild generated indexes, then verify.

## Procedure
1. **Audit** — full tree scan of harness locations (root + subprojects) plus a reference scan (who mentions what). Write scan output to a file and read it back; inline stdout truncates on large scans. Name lists + scripts: references/scan-recipe.md.
2. **Classify** each hit: harness-only (quarantine) / reusable (migrate first) / same-name content (keep — e.g. a "claude.md" design template inside a web-design skill is content, not config).
3. **Migrate** reusable content into Hermes profile skills. Strip other-harness frontmatter (`model:`, `tools:`) and rewrite home-dir paths to real project paths.
4. **Quarantine batch by batch.** Preflight: if an earlier batch already created a quarantine subdirectory, merge subdirs individually — never re-move a directory whose destination already exists.
5. **Fix references** in project docs. Leave generic documentation references (e.g. Claude Code usage docs inside reusable skills) alone.
6. **Rebuild indexes** per the project's index workflow (Boom: the 5-step Eng/Libby sequence in .hermes.md).
7. **Verify** — see below.

## Verification
- Re-scan the project: harness hits should be zero (except kept content).
- `git status --short` inside each touched subproject: expect only `D` for quarantined files; pre-existing `M` are the user's — leave them, never commit them.
- Key runtime deps still exist (scripts, venv, knowledge DBs).
- Migrated skills load (skill_view) and their references resolve.
- Regenerated manifest has zero references to quarantined paths.

## Pitfalls
- **The patch tool mangles Windows backslash paths** — it interprets escapes (`\r` becomes CR, splitting the line). Edit text containing `E:\...` paths via execute_code/Python (raw strings), not the patch tool.
- **shutil.move onto an existing directory** moves the source *inside* the destination, not a merge. Check destination existence first; merge children individually (helper in references/scan-recipe.md).
- **Generated indexes reference everything** — after moves they are full of dead refs; rebuild them, never hand-edit.
- **Empty dir trees** (e.g. a .codex/ left with only subdirs after a file move) — remove them and record the removal in the manifest.
- **Terminal/execute_code output can truncate to one line** on this host — for any scan/audit, write results to a file in the scratch dir and read_file it.
