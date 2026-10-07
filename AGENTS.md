# AGENTS.md

> **Rebuilt 2026-10-06.** The hand-maintained 139-skill inventory this file used
> to contain is now GENERATED from the live registry: see **`core/SKILL_REGISTRY.md`**
> (regenerate with `python -m core.spec`). The architecture and routing contract
> live in **`core/SPEC.md`** and **`wiki/ARCHITECTURE.md`**.
>
> Routing entry point: `boom-router` skill -> `python -m core.router "<request>"`.

## Agent skills

The skill inventory is **generated**, not hand-written:

```bash
python -m core.skill          # live counts + preloaded prompt cost
python -m core.spec           # regenerate core/SKILL_REGISTRY.md
```

See `core/SKILL_REGISTRY.md` for the full list with categories, sizes and
flags. Routing entry point: the `boom-router` skill, backed by `core/router.py`.

### Removed in the 2026-10-06 rebuild

| Removed | Replacement |
|---|---|
| `boom-auto-workflow-router` | `boom-router` + `core/router.py` |
| `boom-project`, `boom-project-v2`, `boom-workflows` | `boom-project` |
| `daily-transit-update`, `morning-transit-briefing`, `transit-pac-pipeline` | `daily-transit` |
| `natal-chart` | `astro-natal-chart` |
| `chinese-almanac-scraper` | `astrology/boom-chinese-almanac` |
| `astro-agent-arm/-bed/-bella/-ck/-nan/-nut/-plawan` | `astro-pipeline` + `config/agents.json` |
| `post-mortem`, `debug-mantra`, `scrutinize` | `boom-post-mortem`, `boom-debug-mantra`, `boom-scrutinize` |
| project skill roots (`skills/`, `.hermes/skills/`, `.agents/skills/`) | single live root at `%HERMES_HOME%\skills` |
