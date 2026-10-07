---
date: '2026-07-27'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/source-discipline-boom.md
---

# BooM Astrology Source Discipline

Use this reference whenever BooM asks for any astrology prediction, timing recommendation, transit reading, PAC timing, daily energy, or interpretation.

## Non-negotiable separation

Do not merge calculation, internal workflow notes, and interpretation sources.

| Layer | Allowed sources | What it can support |
|---|---|---|
| Calculation | `hermes_astro` (pyswisseph), Stellium for Uranian TN, `.ics` event files | Planet positions, houses, aspects, VOC, timing windows |
| Workflow guide | `integrated-astrology` references such as PAC timing/VOC notes | How to decide what to calculate and how to format/check it |
| Interpretation source | `ASTROLOGY-BOOKS-DATABASE` | Meanings of planets, houses, aspects, horary rules, prediction rationale |
| Fallback interpretation | `multi-search-engine` | Only when the database lacks a specific topic; cite as fallback, not database |

## Required order

1. Calculate the chart/timing with `hermes_astro` (pyswisseph) and Stellium if Uranian points are needed.
2. Open `ASTROLOGY-BOOKS-DATABASE` and extract relevant passages for the configurations being interpreted.
3. If the database has no passage for the exact topic, load/use `multi-search-engine` and cite the actual fallback source.
4. Answer with separate labels:
   - `[Calculation]`
   - `[Database-backed]`
   - `[Multi-search fallback]` when used, or `not used` when database was enough
   - `[Interpretation]`

## Hard pitfall from 27 Jul 2026

Do **not** treat `pick-a-card-timing.md`, `moon-voc.md`, or any skill reference as the interpretation database. These are workflow/calculation guides only. If a response says “best time to post PAC love reading,” the timing may come from calculation + PAC workflow, but the meaning behind Venus/H11, Sun/H10, Moon/H3, Saturn/H1, etc. must come from `ASTROLOGY-BOOKS-DATABASE` or from `multi-search-engine` fallback when the database is silent.

## Fallback handling

If `multi-search-engine` is loaded/attempted but search is blocked, captchaed, or yields no usable source, say so and do **not** cite it as support. The answer can proceed only if the Database already supports the core interpretation; otherwise label it incomplete.

## Minimal source line

```text
Calculation: Integrated Transit / hermes_astro (pyswisseph) [and Stellium if used]
Database-backed: <database file names and what each supported>
Multi-search fallback: <source names, “not used because DB covered it”, or “attempted but not used”>
```
