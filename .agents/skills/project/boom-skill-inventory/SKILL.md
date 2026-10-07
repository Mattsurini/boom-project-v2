---
name: boom-skill-inventory
description: Use when syncing or regenerating the Boom skill inventory.
---
# Boom Skill Inventory

Managing the Boom Project's skill library: four locations, one load path, one inventory file.

## Skill locations (project root `E:\Boom Project`)

| Location | Contents | Loaded by Hermes? |
|---|---|---|
| `skills/` | Main library (~100, category subdirs + singletons) | Only via trusted_project_dirs AND git repo — project has no `.git`, so NO |
| `.agents/skills/` | Matt Pocock engineering set (37) | Via `external_dir` (current env) — name-collides with profile copies |
| `.claude/skills/` | Claude Code lane (10) | NO |
| `.hermes/skills/` | 1 real dir + symlinks to `.agents/skills/*` | NO (inert) |

**The working set is the profile dir**: `C:\Users\Turbo\AppData\Local\hermes\skills` — copies of the project skills live there (36 Matt Pocock skills + project singletons like `boom-project`). Project-dir skills never auto-load because `E:\Boom Project` is not a git work tree, so `skills.trusted_project_dirs` matching fails.

Copies are **independent** of the project source — edits in one place do not propagate. Re-sync on request; never assume they match. When **improving** a skill that has both a project source and a profile copy, edit the **project source** (`.agents/skills/<name>`) and re-sync source → profile — editing the copy directly diverges it, and the next sync overwrites your change.

## Syncing project skills into the profile dir

1. Enumerate `E:\Boom Project\.agents\skills\*/SKILL.md` (and any other source set).
2. Check each name against existing profile dirs first — on collision, skip (or rename the copy, e.g. `research` → `research-matt`) and report it. A silent overwrite destroys the profile version.
3. `cp -r` each non-colliding dir into the profile skills dir.
4. Verify: count landed `SKILL.md` files, check every one starts with `---` frontmatter, report `verified=N/N`.

## Syncing the astro-hub skills (horary-astrology, natal-chart, astro-*)

The astrology skills exist in **two copies** that must be kept in sync:
- **Profile** (the copy Hermes loads): `C:\Users\Turbo\AppData\Local\hermes\skills\<name>`
- **Hub** (`hermes-astro-hub`): `E:\Boom Project\hermes-astro-hub\skills\<name>`

Unlike the Matt Pocock skills (source → profile), these are edited in the **profile copy** and propagated to the hub.

1. Before editing, confirm the two copies are in sync (or note the diff you intend to keep) — a one-direction sync overwrites the other copy.
2. Edit the profile copy.
3. From `E:\Boom Project\hermes-astro-hub`, propagate with the `--from-<copy>` flag matching the copy you edited: `python sync_skill_copies.py --from-profile --apply`.
4. Verify with a dry-run (no `--apply`): `python sync_skill_copies.py --from-profile` — every file should read `[SAME]`.

Pitfall: a plain `diff -r` between the two copies can report a **false positive from Windows backslash path handling** — read the actual lines before chasing a "difference."

## Regenerating `AGENTS.md` (complete skill inventory)

The user expects ALL skills in the inventory, not a curated subset.

1. Enumerate every `SKILL.md` under `skills/` and `.agents/skills/`; parse frontmatter `name:` + `description:` (first ~4KB suffices). Do this in code, not by hand.
2. Group by top-level category: `skills/<cat>/<skill>`, top-level `skills/<skill>`, `.agents/skills/<skill>`.
3. **Assert 100% coverage before writing**: every enumerated path appears exactly once in the planned output — zero missing, zero extra. An unasserted hand-grouped list always drops a few (top-level `research-*` singletons and nested duplicates are the usual casualties).
4. Entry format: `- **name** — `path/` — description`, description trimmed to ~120 chars.
5. Keep the tail stub sections (Issue tracker / Triage labels / Domain docs) filled with one-liners pointing at the real `docs/agents/*.md` files — do not leave `[one-line summary]` placeholders.

## Installing external (community) skills from GitHub

When the user asks to "install" a GitHub repo that ships agent skills:

1. The repo's README install instructions usually target Claude Code (CLAUDE.md / `/plugin marketplace`) — ignore them for Hermes. The Hermes-native artifact is the repo's `SKILL.md`; locate it with the GitHub API contents listing (`curl -s https://api.github.com/repos/<owner>/<repo>/contents/`), typically under `skills/<name>/SKILL.md`.
2. Install with `hermes skills install <raw.githubusercontent.com/.../SKILL.md URL>` (direct-URL form). If it reports "already installed", do NOT `--force` — diff the local profile copy against the upstream raw file and patch only the delta, then re-diff to confirm identical.
3. Verify the skill loads via `skill_view(name)` and that `hermes skills list` shows status `enabled`.
4. Register it in the inventory: add a row to `AGENTS.md` (appropriate category) and a bullet to `.hermes.md` under "Hermes Skills for This Project" — the user expects the inventory to be complete.

## Pitfalls

- **The `execute_code` kernel runs native Windows Python: MSYS paths are NOT translated.** A write to `/e/Boom Project/AGENTS.md` lands at `E:\e\Boom Project\AGENTS.md` (a stray tree), while the real file stays untouched. Use `E:\...` paths in kernel code; bash `terminal` still accepts `/e/...`. After any kernel file write, verify the REAL target's size/mtime — a clean exit code proves nothing.
- Frontmatter `description:` may be empty (e.g. `natal-chart`, `tarot-reading`) — have a fallback one-liner or the inventory row reads broken.
- The stray `E:\e\` tree from an earlier path bug still exists (a `.venv` + smoke-test sqlite); it is junk but pre-dates any given session — flag it, don't delete without asking.
- **Name collision across load paths.** A skill name present in both the profile dir and a loaded `external_dir` (the project's `.agents/skills` is one in the current env) makes `skill_view(name='...')` refuse with "Ambiguous skill name." Load by full categorized path, or rename one copy. This is why the 36 Matt Pocock profile copies collide with their `.agents/skills` sources.
- **Skills are not plugins** — there is no "enable for plugins" toggle for a skill; once installed and `enabled` it is active on every Hermes surface. Per-platform availability is `hermes skills config` (interactive TUI, no flags). If the user asks to "enable for plugins", clarify the distinction instead of hunting for a setting.

## Related user-owned skills (do NOT edit)

`boom-project`, `boom-workflows`, and the 36 Matt Pocock copies in the profile dir are user-owned — patching them is refused. If one is wrong or outdated, tell the user and suggest `hermes curator adopt <name>`.
