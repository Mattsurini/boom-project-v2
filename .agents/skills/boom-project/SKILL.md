---
name: boom-project
description: How the Boom Project is structured — core/, registry, context boundaries, artifact lineage, and the commands to operate it.
---

# Boom Project — context boundary and operations

Boom Project is a **context boundary**, not a folder. Everything inside it is
addressable by ID from anywhere; content is referenced, never copied.

This skill **merges** the old `boom-project`, `boom-project-v2` and
`boom-workflows` skills. Their content is archived at
`.rebuild/legacy_skill_texts.txt`.

## Architecture (v2, post-rebuild)

```
request
  │
  ├─ core/router.py      route to cheapest sufficient component
  ├─ core/policy.py      does this decision earn Ask JEV? (usually no)
  ├─ core/registry.py    discovery — the only index of what exists
  ├─ core/context.py     budgeted load / release (never preload)
  ├─ core/skill.py       methodology catalogue, lazy-load
  ├─ core/script.py      execution layer, registry-discovered
  ├─ core/agent.py       specialist workers, isolated context
  ├─ core/memory.py      Notes = truth, index = retrieval, runtime = context
  ├─ core/project.py     scope resolution + write containment
  └─ core/validator.py   named criteria + evidence before "done"
```

Hermes itself is an upstream git-installed product and is **configured, never
forked**. All BooM-specific behaviour lives in `core/` and the live skill root.

## Operating commands

```bash
python -m core.skill            # skill inventory + prompt cost
python -m core.script           # script inventory, finds undiscoverable ones
python -m core.project          # mounts, stages, boundary check
python -m core.memory <query>   # layered retrieval
python -m core.validator        # the rebuild criteria
python -m core.router "<req>"   # explain a routing decision
python -m core.policy explain   # JEV escalation policy
```

## Locations

| What | Where |
|---|---|
| Core (new architecture) | `E:\Boom Project\core\` |
| Live skills (the only root) | `C:\Users\Turbo\AppData\Local\hermes\skills\` |
| Registry / artifact lineage | `E:\Boom Project\cache\registry.sqlite3` |
| Config (agents, policy, projects) | `E:\Boom Project\config\*.json` |
| Verified backup of the legacy system | `E:\Boom Project\.rebuild\backup\<ts>\` |
| Knowledge corpus | `Knowledge/` — **never bulk-load**, route via `Knowledge/indexes/` |
| Generated output | `Output/` — canonical stages only |

Canonical output stages: `Plawan, Nut, CK, Arm, Nan, Bella, Sandee, Ekae, PAC,
Transit, Sources`. Stage **alias folders are forbidden** — the old
`config/agents.yaml` listed aliases that violated the project's own rule, which
is why it was deleted.

## Index rebuild sequence (Eng/Libby)

```bash
python scripts/libby/cli.py --once          # classify + frontmatter
python scripts/build-output-index.py        # legacy pipeline indexes
python scripts/project_index.py             # manifest + router
python scripts/memory_db.py sync-manifest   # sync into registry
python scripts/memory_db.py status          # verify counts
```

## Rules

1. Never duplicate content across folders — reference by ID.
2. Never bulk-read `Knowledge/` or `Output/`. Search → retrieve → load.
3. PDFs stay in place; content-read them on demand, never index-scan them.
4. Only one load-bearing skill root exists. If you add a skill, it goes in the
   live root and gets published to the registry.
5. Every artifact carries `artifact_id`, source lineage, and version.
6. Sub-agents return compact findings only — never raw context.
7. Ask JEV is a decision-support layer, gated by `core/policy.py`. Never
   unconditional, never for chart interpretation.