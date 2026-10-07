---
title: "Scripts And Usage"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "scripts-and-usage"
tags: [skill-reference, horary-astrology]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/horary-astrology/SKILL.md"
summary: "**Pitfall:** When running scripts from `execute_code` or `terminal`, use the venv's Python directly:"
---

# Scripts And Usage

_Moved verbatim out of SKILL.md so the trigger body stays small._

## Scripts

### Execution Method

**Pitfall:** When running scripts from `execute_code` or `terminal`, use the venv's Python directly:

```bash
"C:/Users/Turbo/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" scripts/horary_chart.py "question" 2026-07-12 23:51 19.91 99.83
```

Do NOT rely on `python` from execute_code (may not have hermes_astro) — always use the full path to the venv Python.

### Primary chart: `scripts/horary_chart.py`
Uses `hermes_astro` (shared calculation layer) for ephemeris, houses, aspects, and VOC detection. **Default: Tropical Whole Sign** (H1 = ASC sign). Outputs house cusps, planet table, radicality check (flatlib cross-sign VOC + ASC sign type Chara/Sthira/Dwisvabhava), significators with dignity + avastha, aspect analysis (incl. Translation/Collection of light), and a 72h Moon path with exact aspect times (Newton-refined, cross-sign).

```bash
# From the Hermes venv:
"C:/Users/Turbo/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" scripts/horary_chart.py "question" 2026-07-12 23:51 19.91 99.83
# Placidus houses instead of the whole-sign default:
"C:/Users/Turbo/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" scripts/horary_chart.py "question" 2026-07-12 23:51 19.91 99.83 --placidus
```

### Q2 Moon-Reference chart: `scripts/horary_2nd_q.py`
For the 2nd question in a series (rotates Moon to ASC per Prashna Tantra). Takes the same parameters as `horary_chart.py`. **Topic-generic**: maps the question to the quesited house via the shared `quesited_house()` keyword table (partner→H7, money→H2, weather/rain→H4, job→H10, …; default H7). Outputs the Q1→Q2 rotation, rotated house cusps, planet table in the new frame, significators (Moon = querent, ruler of quesited house = quesited) with dignity + avastha, the Moon↔quesited aspect, a **ruler-to-ruler essential-dignity aspect check with exact timing**, cross-sign VOC, and a 72h Moon path.

```bash
# From the Hermes venv:
"C:/Users/Turbo/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" scripts/horary_2nd_q.py "<question>" <YYYY-MM-DD> <HH:MM> <lat> <lon>
# With JSON output:
"C:/Users/Turbo/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" scripts/horary_2nd_q.py "<question>" <YYYY-MM-DD> <HH:MM> <lat> <lon> --json
```

If no args given, defaults to now at Chiang Rai (19.91, 99.83).

### JSON output
Both `horary_chart.py` and `horary_2nd_q.py` accept `--json` to emit a single machine-readable object (houses, planets, significators, aspects, timing, VOC, translation/collection) instead of the human-readable report. Use it for pipelines / other agents.

### Keeping the hub and profile copies in sync: `sync_skill_copies.py`
The horary-astrology skill exists as **independent copies** in the hub (`E:\Boom Project\hermes-astro-hub\skills\horary-astrology`) and the profile (`C:\Users\Turbo\AppData\Local\hermes\skills\horary-astrology`). After editing scripts or SKILL.md in either place, run the sync (hub root) to re-align them:

```bash
# dry-run: diff the 3 scripts + SKILL.md
~/AppData/Local/hermes/hermes-agent/venv/Scripts/python sync_skill_copies.py            # hub -> profile
~/AppData/Local/hermes/hermes-agent/venv/Scripts/python sync_skill_copies.py --from-profile   # profile -> hub
# actually copy:
~/AppData/Local/hermes/hermes-agent/venv/Scripts/python sync_skill_copies.py --from-profile --apply
```

The shared `hermes_astro` package lives only in the hub (`E:\Boom Project\hermes-astro-hub\hermes_astro`) as an editable install — both copies import the same live code, so no sync is needed for the calculation layer.

### Regression tests (shared layer)
A golden-fixture pytest suite guards the `hermes_astro` calculation layer (positions, ASC, Moon aspect timing, dignity/avastha, rulership, quesited mapping, closest_distance sign convention, VOC, translation/collection). It lives in the hub, not the skill copy:

```bash
cd "E:\Boom Project\hermes-astro-hub"
~/AppData/Local/hermes/hermes-agent/venv/Scripts/python -m pytest tests/ -v
```

Golden values come from the verified 2026-09-08 21:53 ICT / Chiang Rai cast ("Will my ex come back?"). Tolerances are tight (0.01° / 0.1h) — they catch logic regressions, not ephemeris drift.

### VOC timer: `scripts/voc_time.py`

Uses `hermes_astro` (shared flatlib algorithm). Scans forward for Moon VOC start/end.

```bash
~/AppData/Local/hermes/hermes-agent/venv/Scripts/python voc_time.py <YYYY-MM-DD> <HH:MM> <lat> <lon>
```

Outputs current VOC status, then scans forward to find when Moon becomes VOC (no applicative or exact aspects remaining) and when it changes signs.

VOC calculation must use flatlib personal orbs — NOT fixed aspect orbs. See "Moon VOC — Definition & Calculation" section for full methodology.

