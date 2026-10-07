---
date: '2026-07-30'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/moon-voc.md
---

# Moon Void of Course (VOC) — Calculation & Interpretation

> **BOOM'S DEFINITION (updated 30 Jul 2026):**
> VOC start = exact time of Moon's **last EXACT major aspect before sign ingress** (cross-sign aspects count), calculated with **Traditional 7 planets** (Sun–Saturn).
> - Do **NOT** use fixed aspect orbs as the start trigger.
> - Do **NOT** use flatlib's `MAX_EXACT_ORB` / tolerance as extra time after exact; this caused a wrong 05:10 result when the true last exact aspect was 04:26.
> - Do **NOT** wait for 3° separation or any orb separation — VOC starts at the exact aspect minute.
> - Root-solve the last exact aspect time, then set VOC start to that time.
> - Always include/check VOC in BooM's transit, PAC timing, horary, and electional readings.
> - Headline time MUST be the Traditional 7 last-exact-aspect result.

---

## VOC Definition

| Term | Meaning |
|------|---------|
| **VOC** | Moon has no applicative or exact major aspects to any Traditional 7 planet (Sun, Mercury, Venus, Mars, Jupiter, Saturn) |
| **VOC start** | **Exact time** of Moon's **last major aspect** before the next sign ingress |
| **VOC end** | Moon **enters the next sign** |
| **Orb rule** | Uses **flatlib personal orbs** — NOT fixed aspect orbs. An aspect is valid if EITHER planet's personal orb >= current angular deviation from exact. |

### Flatlib personal orbs

| Planet | Personal orb |
|:------:|:-----------:|
| ☀ Sun | 15° |
| ☽ Moon | **12°** |
| ☿ Mercury | 7° |
| ♀ Venus | 7° |
| ♂ Mars | 8° |
| ♃ Jupiter | 9° |
| ♄ Saturn | 9° |

### flatlib's `isVOC()` logic

```python
# From flatlib.tools.chartdynamics
def isVOC(self, ID):
    asps = self.aspectsByCat(ID, const.MAJOR_ASPECTS)
    applications = asps[const.APPLICATIVE]
    exacts = asps[const.EXACT]
    return len(applications) == 0 and len(exacts) == 0
```

Moon is **VOC** only when it has ZERO applicative AND ZERO exact major aspects.

### Key: cross-sign check

**DO NOT check only planets in the same sign as the Moon.** A cross-sign applying aspect blocks VOC just as an in-sign one does.

Example (27 Jul 2026):
- Moon ♑ 6.95°, Saturn ♈ 14.75° — different signs
- Angular separation = 97.8°, deviation from square (90°) = 7.8°
- Moon orb 12° > 7.8° → within orb → **applying square Saturn** → **NOT VOC**

---

## Calculation method (flatlib algorithm via hermes_astro / pyswisseph)

### Algorithm (mirrors flatlib's `_aspectDict` + personal orbs)

1. Get Traditional 7 planet positions at a given time (via pyswisseph)
2. For each planet (paired with Moon as active/faster body):
   a. Compute `sep = closestdistance(Moon_lon, planet_lon)` — signed shortest arc
   b. For each major aspect (0, 60, 90, 120, 180°):
      - Compute `orb = abs(absSep - asp)` — deviation from exact aspect
      - Skip if `Moon.orb < orb AND planet.orb < orb` (both out of orb)
      - Determine movement: `applicative`, `exact`, or `separative`
3. If ANY planet has an applicative or exact aspect within either planet's orb → NOT VOC
4. VOC starts the moment the **last** such aspect is no longer applicative or exact

### Script

Use `horary-astrology/scripts/voc_time.py` (shared calculation engine):

```bash
~/AppData/Local/hermes/hermes-agent/venv/Scripts/python \
  ~/AppData/Local/hermes/skills/research/horary-astrology/scripts/voc_time.py \
  <YYYY-MM-DD> <HH:MM> <lat> <lon>
```

This implements flatlib's exact algorithm using the pyswisseph ephemeris (via `hermes_astro`).

### Worked example

**Input:** `voc_time.py 2026-07-27 10:45 19.91 99.83`

```
Current: Moon VOC? ❌ NO
  Last blocking aspect: opp Mercury (orb=9.861°)

VOC START: 28 Jul 14:15 ICT (Moon @ Cap 20.68°)
MOON SIGNS: 29 Jul 09:15 ICT → Aqu
```

Why the current result says NOT VOC:
- Moon □ Saturn: deviation 7.8° (Moon orb 12, Saturn orb 9 → within both)
- Moon ☍ Mercury: deviation 9.86° (Moon orb 12 → within Moon's orb)
- Moon △ Venus: deviation 12.03° (Moon orb 12, Venus orb 7 → just out; enters orb ~20:51 on 27th)

---

## Interpretation

| Situation | VOC meaning |
|-----------|------------|
| Long VOC (>6h) | Let the energy settle; avoid forcing outcomes |
| Short VOC (<1h) | Minor lull between aspects; usually fine |
| VOC at content posting time | Reschedule if possible; viewers are scattered |
| VOC during a reading | Cards may feel "drift-y" — ground yourself first |

---

## ⚠️ UTC/JD pitfall

`swe.julday()` expects UTC hours. If you pass ICT hours directly, every position shifts by +7h (~3.5° for Moon) — enough to misidentify the VOC window.

Always:
1. Store datetime with `tzinfo=ICT` (UTC+7)
2. Convert to UTC: `dt_utc = dt_local.astimezone(timezone.utc)`
3. Pass UTC components to `swe.julday()`

---

## Related

- `integrated-astrology` SKILL.md Section **E (VOC Moon)** — authoritative definition and output format
- `horary-astrology/scripts/voc_time.py` — calculation script (shared engine)
- `horary-astrology` SKILL.md Section **Moon VOC — Definition & Calculation** — additional flatlib details and common mistakes
