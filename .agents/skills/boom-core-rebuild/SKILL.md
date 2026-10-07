---
name: boom-core-rebuild
description: Operate and debug the rebuilt Boom Hermes core.
---

# Boom Hermes Core (post-2026-10-06 rebuild)

The Boom user layer was rebuilt into `E:\Boom Project\core\`. Hermes itself is
an upstream git product (`hermes-agent` v0.21.5+7331) — **configure it, never
fork it**. All BooM-specific behaviour lives in `core/` and the single live
skill root `%HERMES_HOME%\skills`.

Authoritative detail lives in the project, not here:
- `core/SPEC.md` (generated) — component contracts and invariants
- `wiki/ARCHITECTURE.md` and `wiki/OPERATING.md` — decisions and commands
- `.rebuild/LEGACY_INVENTORY.md` — what was removed and why

## When to Use

Load this skill when the task touches any of:

- `E:\Boom Project\core\` — router, registry, policy, context, skill, script,
  agent, memory, project, validator, tests, spec
- the live skill root `%HERMES_HOME%\skills` — adding, merging or splitting skills
- `config/agents.json` / `config/agents.yaml` — agent registry or libby pipeline
- the memory stores — `wiki/` notes, `boom_project_registry.sqlite3`,
  `hermes_memory.sqlite3`
- Ask JEV / decision escalation policy
- "why does routing pick X?", "a skill is duplicated", "token bloat"

Not needed for: chart calculations, tarot, transit running, content drafting.
For those, load `daily-transit`, `astro-natal-chart`, `tarot-reading`,
`pac-transit-timing` instead.

## Non-negotiable invariants

- **One load-bearing skill root.** Project-local skill roots never load (the
  project is not a git repo, so `trusted_project_dirs` cannot register them).
  The old `skills/`, `.hermes/skills`, `.agents/skills` roots were pure dead
  weight with 54 identical and 14 divergent copies.
- **Never preload.** Search → retrieve → load → execute → compress → release.
  `ContextManager.load()` refuses over-budget bodies and traces `load_denied`.
- **Notes are the source of truth** (`wiki/`). The sqlite index is disposable —
  `prune_missing()` drops rows whose file is gone; `reindex_all_notes()` rebuilds.
  `.rebuild/` and `.quarantine/` must be excluded from retrieval.
- **Hermes is never a database of record.**
- **JEV never unconditional.** `core/policy.py` defaults to NOT escalating;
  astrology interpretation and routine navigation are denylisted.
- **Sub-agents return compact findings only.** `validate_finding()` rejects raw
  payloads (4000-char cap, no `raw`/`dump`/`transcript` keys).
- **Methodology lives in skills, execution in scripts.** Never both in one place.

## Commands

```bash
cd "E:/Boom Project"
python -m core.validator      # 12 criteria — must be 12/12
python -m core.tests          # routing accuracy — must be 100%
python -m core.skill          # inventory + preloaded prompt cost
python -m core.spec           # regenerate SPEC.md + SKILL_REGISTRY.md
python -m core.router "<req>" # explain routing
python -m core.policy explain # JEV policy
python -m core.memory "<q>"   # layered retrieval
```

Use `./.venv/Scripts/python` for `scripts/libby/*` and `scripts/memory_db.py`
(they need PyYAML); plain `python` works for `core/*`.

## What to change when

| Symptom | Change |
|---|---|
| route picks the wrong skill | `core/skill.py:ROUTE_ALIASES` (add a phrase), then `python -m core.tests` |
| route picks a raw script over a skill | `_kind_bonus()` in `core/router.py` |
| a skill body is too big | split into `references/` (cap 12k chars for SKILL.md) |
| description too long | trim frontmatter to <=200 chars; cap is enforced at publish |
| new agent | edit `config/agents.json`, then `python scripts/export_agents_yaml.py` |

## Pitfalls that cost real time

- **`config/agents.yaml` is GENERATED** by `scripts/export_agents_yaml.py` from
  `config/agents.json`. `scripts/libby/classifier.py` requires the YAML, and it
  also reads top-level `flow_stages` and `topic_keywords` — those were recovered
  verbatim from `.rebuild/backup/` and must not be inferred or dropped.
- **Router alias matching is two-tier:** exact substring (8.0) and all
  significant words present (5.5), so "rebuild the output index" hits "rebuild
  index". Bare name-token matches score 3.0, which is why a specific multi-word
  alias gets +3.0 to beat a generic name match.
- **`find()` returns FTS rank order**, so a low-ranked hit can fall outside a
  small limit. The router unions per-keyword results with limit=6 before scoring.
- **Skill `scan()` walks recursively.** `<category>/<name>/SKILL.md` is normal
  Hermes layout. A name at BOTH top level and nested is a genuine duplicate —
  compare with `is_top_level`, not by path string tricks.
- **Stale registry rows outlive deleted skills.** After a teardown, purge rows
  whose `path` no longer exists, or routing returns ghosts.
- **Thai requests never reach FTS.** `registry.find()` builds an FTS5 MATCH, and
  FTS5 tokenises a whole Thai run as ONE token — "สีเสื้อมงคลวันนี้" never
  matches the indexed token "สีเสื้อมงคล". `Router._substring_candidates()`
  exists for exactly that (alias substring scan, runs only when FTS finds
  nothing). Practical rule: an ASCII keyword alias does NOT make a skill
  reachable — put the Thai phrases in `ROUTE_ALIASES` and add a Thai case to
  `core/tests.py`.
- **`.agents/skills` is tier0; the profile mirror is copied by hand.** There is
  no sync script. `check_no_divergent_skills` fails on drift AND on mirror-only
  rows, so after editing or adding any SKILL.md, `cp` it into
  `%HERMES_HOME%\skills\<category>\<name>\` before reporting done. Note that
  `skill_manage` edits the *profile* copy, not tier0 — sync the other way.
- **A new skill needs three touches, not one.** `cp` into tier0 + mirror, then
  `SkillManager().publish_all()` to register it (there is no CLI —
  `python -m core.skill` only reports), then `python -m core.tests`. Same for
  scripts: `ScriptRegistry().publish_all()`. A file in the folder is not a
  routable component.
- `execute_code` keeps a persistent kernel: after editing a module, either call
  with `reset=true` or delete `core/__pycache__`, or you debug stale bytecode.
- The `patch` tool drifts indentation on deep Python edits; when a lint error
  appears, read the file and rewrite the block via `execute_code` instead of
  re-patching.

## Validation standard

A change is not done until `python -m core.validator` reports 12/12 AND
`python -m core.tests` reports 100%. Report what changed, what is verified,
what is left — not the process.