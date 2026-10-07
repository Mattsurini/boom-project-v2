---

---

---
date: '2026-10-06'
tags: [operations, commands]
---

# Operating the rebuilt system

```bash
cd "E:/Boom Project"

python -m core.validator     # 14 rebuild criteria — must be 14/14
python -m core.tests         # routing regression suite — must be 100%
python -m core.skill         # skill inventory + preloaded prompt cost
python -m core.script        # script inventory, flags undiscoverable ones
python -m core.project       # mounts, stages, boundary containment
python -m core.memory <q>    # layered retrieval (index → notes)
python -m core.router "<q>"  # explain a routing decision
python -m core.policy explain   # JEV escalation policy
```

## Rebuild sequence (for reference, already executed)

audit → backup → deconstruct → design → migrate → rebuild → validate → remove legacy.
Evidence: `.rebuild/LEGACY_INVENTORY.md`, `.rebuild/backup/20261006T125645/`.

## After any change

Run `python -m core.skill` then `publish_all()` if you touched SKILL.md
frontmatter, then `python -m core.tests`. Routing aliases live in
`core/skill.py:ROUTE_ALIASES` and are the thing most likely to need updating.

## Known debt (deliberately not hidden)

- **8 unloadable SKILL.md files** (>20k chars, over ContextManager's
  `DEFAULT_MAX_SINGLE_BODY_CHARS`, so `ContextManager.load()` refuses them) —
  largest is horary-astrology at 54k. Gated by validator criterion `loadable`,
  so it now fails visibly instead of warning forever. Split depth into
  `references/`.
- **18 further SKILL.md files over the 12k style cap** — these DO load; the
  split is housekeeping, not a defect. Listed under `OVER THE STYLE CAP` in
  `python -m core.skill`.
- **20 scripts without module docstrings** — undiscoverable by AST scan.
  `python -m core.script` lists them.
- **Overlapping transit engines** (`transit_timeline_v3.py` canonical;
  `transit_timeline_exact.py`, `today_transit_check.py`, `transit_timeline_check.py`
  also present; `transit_timeline_v2.py` no longer exists) — the non-canonical ones
  should be registered as deprecated aliases in one `transit_timeline` entry.
- **Notes folder was empty after teardown** — this file set is the first content.
  The Obsidian vault exists but has no read path from Hermes yet.
