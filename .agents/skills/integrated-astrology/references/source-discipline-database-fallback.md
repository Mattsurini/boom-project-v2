---
date: '2026-08-01'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/source-discipline-database-fallback.md
---

# Source Discipline — Database vs Skill vs Fallback

Use this whenever BooM asks for any astrology prediction, transit reading, electional/PAC timing, horary answer, or auspicious timing.

## Non-negotiable distinction

| Layer | What it is | Can it support prediction? |
|---|---|---|
| Calculation | `hermes_astro` (pyswisseph) / Stellium / .ics SUMMARY | Supports positions, timing, aspects only |
| Workflow guide | `integrated-astrology`, `horary-astrology`, internal `references/*.md` | Tells how to work; **not** a source of meaning by itself |
| Database source | `ASTROLOGY-BOOKS-DATABASE` opened/extracted in the session | Primary interpretation support |
| Fallback research | `multi-search-engine` loaded/used when DB lacks a specific topic | Secondary interpretation support, must be labeled |

## Required order

1. Calculate the chart/timing/VOC.
2. Open `ASTROLOGY-BOOKS-DATABASE` and extract relevant meanings for the actual factors used.
3. If DB covers planet/house/aspect but not the specific application (example: Pick A Card upload timing), keep the DB meanings and use `multi-search-engine` for the application-specific bridge.
4. In the answer, label sections:
   - `[Calculation]`
   - `[Database-backed]`
   - `[Multi-search fallback]` or `Multi-search fallback: not used because DB covered it`
   - `[Interpretation]`

## Pitfall from 27 Jul 2026

Do not treat `pick-a-card-timing.md` or any skill reference as if it were `ASTROLOGY-BOOKS-DATABASE`. It can shape the workflow, but prediction wording must still come from Database or clearly labeled fallback search.

If Database/fallback was not actually performed, say: `this is not yet a complete prediction, because Database/fallback has not been checked` before giving any draft.
