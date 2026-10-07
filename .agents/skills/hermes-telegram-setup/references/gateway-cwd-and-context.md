# Gateway working directory, context discovery, and verification

Depth behind `SKILL.md`. Read when a messaging gateway replies but "does not know about the
project", or when you must prove a config change actually reached the running process.

## Which cwd each surface uses

| Surface | cwd source |
|---|---|
| CLI / TUI / desktop | launch directory; `terminal.cwd` ignored for the local backend |
| Gateway (Telegram, Discord, …) | `terminal.cwd` from config; else the legacy `MESSAGING_CWD`; else `$HOME` |
| Cron | the job's own `workdir` when set, else `terminal.cwd` |
| Delegated subagents | inherits the parent's resolved cwd |

Consequence: `terminal.cwd` is the single anchor for every non-interactive surface. Anchor it once
and cron jobs inherit it too.

## Placeholder semantics

`.`, `auto`, and `cwd` are placeholders, not relative paths. Under a gateway they resolve to
`$HOME`, because a background service has no launch directory to inherit. Setting
`terminal.cwd: "."` therefore means "run in the home directory", which is never what someone
meaning "use my project" intends.

Read the resolution helper directly to assert behavior instead of reimplementing it — it is the
same function the gateway calls at startup:

```python
from gateway.cwd_placeholder import resolve_placeholder_terminal_cwd
resolved = resolve_placeholder_terminal_cwd(
    configured_cwd=<terminal.cwd from the real config>,
    terminal_backend=<terminal.backend>,
    messaging_cwd=os.getenv("MESSAGING_CWD"),
    docker_mount_cwd_to_workspace=<terminal.docker_mount_cwd_to_workspace>,
    home_fallback=os.path.expanduser("~"),
)
```

## What the anchor buys you

Context discovery walks up from the resolved cwd, so anchoring is what makes project rules load:

- `.hermes.md` / `HERMES.md` — nearest match from cwd up to the git root (cwd only when there is no git root).
- `AGENTS.md` — directory chain from git root down to cwd; first non-empty of `AGENTS.override.md` / `AGENTS.md` / `agents.md` per directory.

Both are optional; an unanchored gateway loads neither and silently runs context-free.

## Project skills are a separate gate

`skills.trusted_project_dirs` entries are only consulted for a resolved *project root*, and a
project root is the nearest ancestor containing `.git`. So for a non-repo project folder:

- `trusted_project_dirs` lists the path, but it can never match
- `.hermes/skills/` and `.agents/skills/` under that folder never load

Cwd anchoring fixes context files but NOT project skills. Copy those skills into the profile skills
directory, or initialize a repo — offer the choice, do not silently run `git init` for the user.

## Verification recipes

Importing Hermes internals needs the install venv (`<hermes-install>/venv/Scripts/python.exe`),
which carries the config-parsing dependencies; the bundled runtime interpreter under
`.hermes-runtime/python/` does not, and fails on the YAML layer before reaching your code.

**1 — the running process, not the file:**

```python
import psutil, subprocess
pid = int(subprocess.run(["hermes", "gateway", "status"], capture_output=True, text=True)
          .stdout.split("PID:")[1].split()[0].strip(" )"))
env = psutil.Process(pid).environ()
assert env.get("TERMINAL_CWD") == r"E:\Boom Project"
```

**2 — the real config, not defaults:** parse `config.yaml` with the project loader
(`utils.fast_safe_load`, or `hermes config get <key>`) and feed it to the resolver above. Compare
the resolved value against the intended path and assert it is not in the placeholder set.

**3 — context discovery actually finds the files:**

```python
from pathlib import Path
from agent.prompt_builder import _agents_md_candidates, _find_hermes_md
cwd = Path(resolved)
print(_find_hermes_md(cwd), [p for _l, p, _c in _agents_md_candidates(cwd)])
```

**4 — real delivery:** `hermes send -t telegram:<chat_id> "..."` returns `sent` without an agent
loop, so it isolates transport from model and context problems.

## Reading gateway state

- Inbound/outbound activity: `<hermes-home>/logs/gateway.log`, filter `inbound message: platform=`.
- Pairing approvals: `<hermes-home>/platforms/<platform>-approved.json`.
- Sessions: `<hermes-home>/sessions/sessions.json`; keys are shaped like
  `agent:main:<platform>:dm:<chat_id>`.
- Cron definitions: `<hermes-home>/cron/jobs.json`.

Network flapping that self-recovers on a retry (a hostname path timing out, then succeeding via a
resolved IP) is normal and needs no action — confirm recovery in the log before treating it as a
fault.