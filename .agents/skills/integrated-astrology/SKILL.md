---
name: integrated-astrology
description: Western + Uranian astrology readings combined.
version: 2.0.0
author: Turboz
license: MIT
tags: [astrology, western, uranian, transneptunian, integrated, chart, transit, synastry, composite]
metadata:
  hermes:
    tags: [astrology, western, uranian, transneptunian, integrated, transit, prediction]
    related_skills: [uranian-astrology, astro-natal-chart, astro-synastry, fortune-hub, multi-search-engine, vedic-astrology, horary-astrology]
---

# Integrated Astrology — BooM Protocol

## Overview

This skill is the authoritative workflow for BooM's astrology readings that combine:

1. **Western/Tropical astrology** — planets, signs, Placidus houses, aspects, VOC.
2. **Uranian/Hamburg astrology** — Cupido, Hades, Zeus, Kronos, Apollon, Admetos, Vulkanus, Poseidon; 90° dial; midpoint activations.
3. **Vedic/Jyotish cross-check** — sidereal rāśi, nakshatra, dasha/gochara logic where relevant. BooM now wants Vedic included in integrated predictions by default.
4. **ASTROLOGY-BOOKS-DATABASE** — mandatory interpretation source for every prediction.

The core failure this skill prevents: **calculating accurate transits but giving an uncited/unsupported prediction**. BooM treats calculation and interpretation as separate verification layers.

## When to Use

Use this skill for:
- Daily/monthly energy readings: "check today's energy", "what's next month like"
- Transit-to-natal readings, career/love timing, returns, retrogrades, VOC
- PAC timing/themes based on astro weather
- Questions that require Western + Uranian synthesis
- Horary questions use `horary-astrology`; make its workflow follow the same integrated-source discipline: Vedic/Jyotish support, ASTROLOGY-BOOKS-DATABASE gate, and multi-search fallback
- Any time BooM asks whether a prediction was checked against the database

Don't use alone for:
- Pure Tarot/Lenormand card draws → use `tarot-reading` / `lenormand-reading` after timing if needed.
- Thai/Vedic/BaZi-only readings → route through `fortune-hub`.
- Financial market prediction → use `financial-astrology` and empirical backtest rules.

## Non-Negotiable Gates

### Gate 1 — Calculate with the right engine

| Need | Engine | Rule |
|---|---|---|
| Planets/houses/aspects (natal + transit charts) | `myhora-chart` → `hermes_astro.myhora.get_chart()` (myhora.com POST, no local ephemeris) | **PRIMARY CHART ENGINE** — server-computed positions/cusps/aspects; myhora's sidereal Lahiri is correct (local swisseph/xalen run ~0.88° high). See `myhora-chart` skill; run with Hermes venv python (Boom `.venv` shim is broken). |
| Exact times / root-finding / VOC | `hermes_astro` (shared) → pyswisseph primary, `xalen.swe` fallback | **SHARED LAYER** — same engine as `horary-astrology`. flatlib personal orbs, cross-sign VOC, Placidus houses. Fallback chart engine only when myhora is down (flaky site; module retries 4×). |
| Uranian TN points | `stellium` + `.with_uranian()` | Swiss ephemeris (pyswisseph/xalen) does **not** support IDs 40–47 |
| Vedic/Jyotish layer | `vedic-astrology` + sidereal calculations | Optional cross-check in integrated predictions when relevant; do not force it unless BooM asks. |
| Interpretation | `ASTROLOGY-BOOKS-DATABASE` | Mandatory before prediction |
| Fallback research | `multi-search-engine` | Mandatory when database has no relevant passage |
| `.ics` transit events | Astro-Seek `.ics` | Cross-reference only; read `SUMMARY`, never `DESCRIPTION` |

### Gate 2 — Database before prediction

**Mandatory two-layer workflow — do not skip:**

**Calculation layer:**
- Use `myhora-chart` (`get_chart`) for chart/transit positions, houses, and aspects; use `hermes_astro` (pyswisseph primary, xalen fallback) for exact-time root-finding and VOC.

**Interpretation layer:**
1. Open `ASTROLOGY-BOOKS-DATABASE` first.
2. Use Database meanings for planets/houses/aspects.
3. If the Database has no passage for a specific topic (example: "best time to upload Pick a Card love reading"), load/use the **`multi-search-engine`** skill as fallback research.
4. In the answer, label clearly what is **Database-backed** vs **multi-search fallback**.

Before writing **any prediction**, open and extract relevant source material from:

`C:\Users\Fourt\ASTROLOGY-BOOKS-DATABASE\`

**Hard stop:** If the database is missing, moved, or unreadable, do **not** present the reading as complete. Say:

> This prediction cannot be made complete right now, because Turboz cannot access `ASTROLOGY-BOOKS-DATABASE` at the moment

Then either ask for the path or, only if BooM explicitly accepts, provide a clearly labeled **non-database draft**.

**Research fallback with multi-search-engine:** If the database is accessible but does not contain a relevant passage for the exact configuration being interpreted, load/use `multi-search-engine` every time before predicting. Search broadly across multiple engines/sources for the missing meaning, then clearly label the source as `Database fallback research` and cite what was actually used. Do not fill missing meanings from memory without source support.

**Important:** A calculated chart is not a database-backed prediction.

| Statement | Allowed only when |
|---|---|
| "Calculated" | Ephemeris/charts/aspects were calculated |
| "Checked the Database" | You actually opened/extracted database references and used them |
| "Prediction complete" | Both calculation + database-backed interpretation are done |

### Gate 3 — Say the source line in the answer

Every astrology reading should include a compact source line:

`Calculation: myhora-chart/pyswisseph/Stellium | Interpretation: ASTROLOGY-BOOKS-DATABASE-backed`

If not backed, say so plainly and do not pretend.

## Calculation Workflow

### 1. Timezone-safe Julian Day

`swe.calc_ut()` expects UTC. Convert Thai local time (ICT, UTC+7) to UTC first.

```python
from datetime import timezone
import swisseph as swe  # pyswisseph in the Hermes venv (xalen.swe is API-identical in the dedicated xalen-venv)

def jd_utc(dt_local):
    dt_utc = dt_local.astimezone(timezone.utc)
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
    )
```

Never pass ICT hours directly to `swe.julday()`.

### 2. Planets (pyswisseph / xalen.swe — same Swiss API)

```python
import swisseph as swe
swe.set_ephe_path(None)

PLANETS = [
    (swe.SUN, "☉", "Sun"), (swe.MOON, "☽", "Moon"),
    (swe.MERCURY, "☿", "Mercury"), (swe.VENUS, "♀", "Venus"),
    (swe.MARS, "♂", "Mars"), (swe.JUPITER, "♃", "Jupiter"),
    (swe.SATURN, "♄", "Saturn"), (swe.URANUS, "♅", "Uranus"),
    (swe.NEPTUNE, "♆", "Neptune"), (swe.PLUTO, "♇", "Pluto"),
]

def calc_body(pid, dt_local):
    arr = swe.calc_ut(jd_utc(dt_local), pid, swe.FLG_SWIEPH | swe.FLG_SPEED)[0]
    return {"lon": arr[0], "lat": arr[1], "speed": arr[3], "rx": arr[3] < 0}
```

### 3. Placidus houses — normalize engine return shapes

pyswisseph `swe.houses()` may return 13 cusps with index 0 unused; xalen.swe returns 12. Always normalize.

```python
def calc_houses(dt_local, lat, lon, hsys=b'P'):
    cusps_raw, ascmc = swe.houses(jd_utc(dt_local), lat, lon, hsys)
    cusps = list(cusps_raw if len(cusps_raw) == 12 else cusps_raw[1:13])
    return cusps, ascmc[0], ascmc[1]

def house_by_cusps(cusps, lon):
    lon %= 360
    for i in range(12):
        c1, c2 = cusps[i], cusps[(i+1) % 12]
        if c2 < c1:
            if lon >= c1 or lon < c2:
                return i + 1
        elif c1 <= lon < c2:
            return i + 1
    return 12
```

### 4. Transit-to-natal aspects

Always scan **all planets to all natal targets**, then sort by orb. Don't cherry-pick Moon only.

```python
ASPECTS = {
    0: ("☌", 8), 30: ("✱", 3), 60: ("⚹", 6), 90: ("□", 5),
    120: ("△", 6), 150: ("⚻", 3), 180: ("☍", 6),
}

def angle_diff(a, b):
    d = abs((a - b) % 360)
    return 360 - d if d > 180 else d

def aspect_between(a, b):
    d = angle_diff(a, b)
    best = None
    for deg, (sym, max_orb) in ASPECTS.items():
        orb = abs(d - deg)
        if orb <= max_orb and (best is None or orb < best[0]):
            best = (orb, sym, deg)
    return best  # (orb, symbol, exact_degree) or None
```

Priority in the reading:
1. Tight aspects ≤2°.
2. Work questions: emphasize natal/transit houses **2, 6, 10, 11** and Mercury/Saturn/Jupiter/Mars.
3. Love questions: emphasize houses **5, 7, 8, 12**, Venus/Moon/Neptune/Pluto/Cupido.
4. Monthly readings: separate week-by-week windows; do not make one vague paragraph.

### 5. Uranian TN via Stellium

Use this exact API; `ChartBuilder.from_native(lat=..., lon=...)` is wrong.

```python
from stellium import ChartBuilder
from stellium.core.native import Native

def stellium_positions(dt_local, lat, lon, name="Transit"):
    native = Native(dt_local, (lat, lon), name=name)
    chart = ChartBuilder.from_native(native).with_uranian().calculate()
    return {p.name: p.longitude for p in chart.positions}

TN = {"Cupido", "Hades", "Zeus", "Kronos", "Apollon", "Admetos", "Vulkanus", "Poseidon"}
```

Include at least:
- TN → natal planet/angle aspects within 3° for hard aspects, 5° for overview.
- 90° dial contacts within 1.5° when the user asks for depth.
- Midpoint activations within 1.5° for deep/specific timing.

## Horary Verdict
**Short answer:** ...

| Check | Result | Meaning |
|---|---|---|
| Radicality | ASC 12° | Readable |
| Querent | ASC ruler ... | BooM |
| Quesited | 7th ruler ... | Him / the matter asked |
| Main aspect | applying/separating ... | Outcome |
| Vedic/KP/Tajik | ... | cross-check |

## Interpretation Rules

### Retrograde

- Verify speed from ephemeris before saying Rx.
- Retrograde is a modifier, not a verdict.
- Use Gochara principle: retrograde is stronger for the moment, but expression depends on planet/house/aspect.
- For Neptune retrograde nuance, read `references/neptune-retrograde.md`.

### Local vs natal overlay

When BooM says **Local**, keep these separate:

| Label | Meaning | Output |
|---|---|---|
| Local events | Astro-Seek `.ics` event list in ICT | `SUMMARY` + time only |
| Local chart | Transit chart cast for Chiang Rai/current place | Transit planets in local houses |
| Natal overlay | Transit planets through BooM's natal houses | Transit-to-natal houses/aspects |

If unclear, ask one concise clarification. If BooM already used one label, stick to it.

### Work/career focus

For work readings, highlight:
- **10th house / MC**: visibility, career direction, public role.
- **6th house**: workload, routine, health of process.
- **2nd house**: pricing, income, self-worth.
- **11th house**: audience, network, community, gains.
- **Mercury**: writing, speaking, commerce, content.
- **Saturn**: responsibility, structure, pressure, professional standard.
- **Jupiter**: growth, teaching, audience expansion, overpromise risk.
- **Mars**: drive, execution, conflict, burnout.
- **Kronos/Vulkanus/Apollon**: authority, force, knowledge/communication reach.

### Love focus

For love readings, highlight:
- **5th** romance, attention, play, creative love.
- **7th** partner/relationship contract.
- **8th** intimacy, obsession, energetic binding.
- **12th** hidden feelings, secrecy, avoidance.
- **Venus/Moon/Neptune/Pluto** and **Cupido/Poseidon**.

## Scripts
`scripts/integrated_reading.py` · `scripts/voc_time.py`. Detail: `references/support-files.md`.

## Reference files — open only when its topic comes up
The body above suffices for a standard pass; opening this costs more than the old single file did.

- `integrated_astrology-reference.md` — Deep reference sections moved verbatim out of integrated-astrology/SKI
- Moved sections: Output Style for BooM, Verification Checklist
