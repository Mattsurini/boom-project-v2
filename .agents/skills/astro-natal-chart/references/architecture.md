---
title: "Architecture"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "architecture"
tags: [skill-reference, astro-natal-chart]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/astro-natal-chart/SKILL.md"
summary: "All astrological calculations flow through a single source of truth:"
---

# Architecture

_Moved verbatim out of SKILL.md so the trigger body stays small._

## Architecture


All astrological calculations flow through a single source of truth:


```

natal_chart_swe.py --json  →  JSON data  →  draw_wheel.py  →  PNG image

                                  ↕

                          natal_chart_swe.py  →  text output

```


`natal_chart_swe.py` is the **sole calculation engine**. `draw_wheel.py` only renders — it calls `natal_chart_swe.py --json` via subprocess and draws the wheel from that data. This guarantees text and graphical output always match.

**CLI is `<date> <time> <city>`** — cities resolve by hyphenated lowercase key
(`chiang-rai`, `bangkok`, `izhevsk`, `moscow`). `ChiangRai` **fails** with
`City 'ChiangRai' not found in the database`. `find_city()` also has a substring
fallback (`if key in k or k in key`), so ambiguous input can silently resolve to
the wrong city — use exact keys.

**Charts are tropical, Placidus, no ayanamsa.** `calc_houses()` hardcodes
`swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SWIEPH)`; there is no sidereal/Lahiri
flag in the file. Do not use this engine for Vedic work — use Boom's
`scripts/natal_chart.py` (supports `--house-system "Vedic (Equal from Asc)"`) or
`hermes_astro`.

**Timezones are a fixed static table** (`TZ_OFFSETS`), not historical. A birth with
DST in effect, or a date before/after a zone's DST rule changes, gets the wrong
UTC instant (Europe/Samara is hardcoded to +4 even in winter). Flag this for
pre-1990 or DST-affected births.

**Independent cross-check (no local ephemeris):** `hermes_astro.myhora.get_chart(date, time, city=..., tropical=...)` fetches a server-computed chart (natal + 12 cusps + aspects) from myhora.com via POST — see `myhora-chart` skill. Use it to verify positions or when pyswisseph is unavailable. Note: local swisseph/xalen sidereal (Lahiri) values run ~0.88° high on this host; myhora's sidereal output is the correct standard Lahiri. `hermes_astro` is editable-installed in the **Hermes** venv — the Boom `.venv` python cannot `import hermes_astro` (verified 2026-10-06).

**Do not trust a dated aspect-orb table from this file.** `ASPECTS` in
`natal_chart_swe.py` (conj/op 8, sq/tr 7, sext 5, minors 2) does not match Boom's
own aspect engine (`hermes_astro` uses per-planet orbs, e.g. `PLANET_ORBS`
Sun 15 / Moon 12 / Merc 7 / Venus 7 / Mars 8 / Jup 9 / Sat 9) nor the
`BOOM_FULL_ORBS` reference set. If the answer is a transit/natal aspect check,
use the Boom engine; treat these numbers as display-only.


---


