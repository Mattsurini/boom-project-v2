---

---

---
date: '2026-10-06'
tags: [architecture, rebuild, decision]
status: authoritative
---

# Boom Hermes — Architecture Decisions (v2)

Post-rebuild. Supersedes HERMES_ORCHESTRATOR.md, HERMES_SYSTEM_PROMPT.md,
HERMES_SYSTEM_AUDIT.md (archived in `.rebuild/legacy_skill_texts.txt`).

## Roles

| Component | Role |
|---|---|
| Hermes | Orchestrator. Upstream git product — **configured, never forked.** |
| Notes (this folder) | Source of truth. Human-written, human-read. |
| `boom_project_registry.sqlite3` | Index + retrieval. Disposable, rebuildable from Notes. |
| Hermes holographic provider | Always-on runtime context, char-budgeted. |
| MCP | Integration layer. Currently `docker` (tools) + `ask-jev` (decision support). |
| Ask JEV | Decision Support Layer, gated by `core/policy.py`. Never unconditional. |
| Sub-agent | Specialist worker, isolated context, compact findings only. |
| Skill | Methodology. One live root, lazy-loaded. |
| Script | Execution. Registry-discovered. |
| Registry | Discovery. The only index of what exists. |
| Project | Context boundary. Reference by ID, never duplicate. |
| Artifact | Output with id, version, source lineage. |
| Knowledge Graph | Relationships, via `registry.link()`. |

## Hard rules

1. Never preload. SEARCH → RETRIEVE → LOAD → EXECUTE → COMPRESS → RELEASE.
2. Hermes is not a database of record. Writes go to Notes.
3. The index is disposable. If lost, rebuild from Notes.
4. Sub-agents return Finding/Files/Symbol/Evidence/Confidence, nothing else.
5. Delegate only when context absorbed > overhead (`core/agent.py`).
6. One load-bearing skill root. New skills go there and are published.
7. JEV escalates only on a declared policy trigger. Never for chart reads.
8. Sub-agent isolation is enforced by `validate_finding()`, not by convention.

## Measured outcome

| Metric | Before | After |
|---|---|---|
| Load-bearing skill roots | 4 (3 inert) | 1 |
| Skill names across roots | 81 (54 dup, 14 divergent) | 153, 0 duplicates |
| Preloaded skill prompt | 9,120c (~2.3k tok) | 10,699c (~2.7k tok, 153 skills) |
| Forced router preload | ~26 KB/turn (4 docs) | ~1 KB (one 2.8 KB skill) |
| Governance docs with overlapping authority | 8 | 3 (SOUL / this / boom-project) |
| Memory stores with no clear owner | 4 | 3, each owned |
| Dead integration surface | 46 MB TencentDB, 162 MB stale copy | removed |
| Routing accuracy | unmeasured | 22/22 (core/tests.py) |
| Rebuild criteria | none | 12/12 (core/validator.py) |
