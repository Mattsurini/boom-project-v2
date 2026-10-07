---
name: hermes-slash-command-troubleshooting
description: Use when a Hermes slash command fails or errors out.
---

# Hermes slash command troubleshooting

Diagnose `4018 not a quick/plugin/bundle/skill command` and ambiguous-skill dispatch failures. Dispatch chain (tui_gateway/methods_tools.py `command.dispatch`): `quick → plugin → bundle → skill → built-in`.

## Core trap
`4018` is a **catch-all**: it is emitted when every stage returns None. The skill stage (`_dispatch_skill`) wraps scan + load in `contextlib.suppress(Exception)`, so a skill that **is registered** but **fails to load** (ambiguous name, missing file, quarantine) also surfaces as 4018. Never conclude "the command doesn't exist" from the 4018 text alone — the load stage can fail silently behind it.

## Procedure
1. **Grep the live log for the skill name first** — the real error is usually already there:
   `grep -n "<name>" logs/agent.log logs/errors.log`
   Look for: `Skill name collision for '<name>'`, `Ambiguous skill name`, `quarantined`, `collides with a core Hermes command`, `already claimed by`.
2. **Verify registration** in a fresh process (venv python):
   ```bash
   cd "C:/Users/Turbo/AppData/Local/hermes/hermes-agent"
   HERMES_HOME="C:/Users/Turbo/AppData/Local/hermes" HERMES_PLATFORM=desktop \
     venv/Scripts/python.exe -c "from agent.skill_commands import scan_skill_commands; c=scan_skill_commands(); print(len(c), '/<name>' in c)"
   ```
   Registered → the failure is in the **load** stage (step 3). Not registered → registration-level cause (table below).
3. **Test the load stage**:
   ```python
   from agent.skill_commands import build_skill_invocation_message
   msg = build_skill_invocation_message('/<name>')   # None = the failure point
   ```
   If None, call `tools.skills_tool.skill_view('<name>')` directly — its JSON `error`/`matches` fields are the real cause.
4. **Reproduce with both scopes in force** when the log shows a collision: run `scripts/repro_dispatch.py <name> --project-dir <dir>` with the venv python (exit 0 = would dispatch, 1 = would 4018).

## Root causes
| Symptom (log / skill_view) | Cause | Fix |
|---|---|---|
| `Ambiguous skill name 'X': 2 skills match` | Duplicate name across profile skills + project/external dir | `diff` the copies; delete one (drop the project copy if `/X` must work from any cwd; drop the profile copy if the project is canonical) or rename one |
| `collides with a core Hermes command; skipping auto-registration` | Name collides with a core command | Use `/skill X`; rename the skill |
| `already claimed by` | Two skills slugify to the same command | Rename one |
| Not in map, no log line | In `skills.disabled` config, platform/environment frontmatter gate, or quarantined project skill | Check `skills:` in config.yaml, frontmatter, project quarantine |

## Repro environment recipe
- Interpreter: `hermes-agent/venv/Scripts/python.exe`. Probing the desktop's bundled `.hermes-runtime` is a dead end — the live worker runs with the venv site-packages on PYTHONPATH, so the runtime's own site-packages do not reflect what the gateway can import.
- Env: `HERMES_HOME=<profile home>` (default profile: `C:\Users\Turbo\AppData\Local\hermes`), `HERMES_PLATFORM=desktop`.
- Project-tier scoping is session-gated (`skills.trusted_project_dirs` + cwd); an isolated repro with just `chdir` to the project may still see an empty project tier. Force it by monkeypatching `agent.skill_utils.get_project_skills_dirs` and `tools.skills_tool._skill_search_dirs` to include `<project>/.agents/skills` (repro_dispatch.py does this). Both are deferred imports inside the scan/load functions, so patching the module attributes at call time works.

## Red herrings
- `disable-model-invocation: true` in SKILL.md frontmatter (a Matt Pocock skill convention) is **not a Hermes flag** — zero code references; it does not affect dispatch.
- "The scan silently failed / missing yaml": disprove against the live log — if the live process logs any in-scan warning (e.g. the recurring `handoff` core-collision warning), the scan is running and the map is populated; the failure is downstream in the load stage.
