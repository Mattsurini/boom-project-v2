---
date: '2026-08-01'
tags:
- project
source: hermes-astro-hub/skills/horary-astrology/references/moon-voc-calculation.md
---

# Moon VOC — Calculation Reference

## Definition (BooM's system)

```
VOC start = exact time of Moon's LAST aspect with Traditional 7 planets
           (Sun, Mercury, Venus, Mars, Jupiter, Saturn)
           do NOT wait for orb >3° — VOC starts at aspect perfection, not when orb exceeds 3°

VOC end   = Moon enters the next sign
```

During VOC: Moon will not perfect any new major aspect until sign change.

---

## Flatlib Personal Orbs — The Correct Method

**CRITICAL:** flatlib does NOT use fixed aspect orbs (conj 8°, sq 7°, etc.). It uses **PERSONAL ORBS per planet:**

```python
PLANET_ORBS = {
    'Sun': 15,    # Widest — vitality, authority
    'Moon': 12,   # Second-widest — emotions, the fastest body
    'Mercury': 7, # Narrow — intellect, communication
    'Venus': 7,   # Narrow — love, values, aesthetics
    'Mars': 8,    # Moderate — action, aggression, drive
    'Jupiter': 9, # Moderate-wide — expansion, luck, growth
    'Saturn': 9,  # Moderate-wide — restriction, structure, karma
}
```

### flatlib's Aspect Logic

In `flatlib.aspects._aspectDict`:
```python
if obj1.orb() < orb and obj2.orb() < orb:
    continue  # SKIP — BOTH planets out of orb
```
where `orb` = `abs(abs(shortest_arc) - ideal_aspect_angle)` — the current angular deviation from exact.

**The aspect is valid if at least ONE planet's personal orb >= the deviation.**

Example — Moon ♑ 6.95° vs Saturn ♈ 14.75°, square (90°):
- Shortest arc = **97.8°** → deviation = |97.8 - 90| = **7.8°**
- Moon orb = 12 → `12 < 7.8` → **False** (within orb)
- Saturn orb = 9 → `9 < 7.8` → **False** (within orb)
- `False AND False` = do NOT skip → **aspect IS valid** ✅

### Practical Impact of Personal Orbs

| Scenario | Fixed orb (wrong) | Flatlib personal (correct) |
|----------|:-----------------:|:--------------------------:|
| Moon 7.8° from square Saturn | ❌ Out (sq=7°) | ✅ In (Moon=12°, Sat=9°) |
| Moon 9.9° from opposition Mercury | ❌ Out (opp=8°) | ✅ In (Moon=12°) |
| Moon 12.0° from trine Venus | ❌ Out (tri=8°) | ❌ Out (Moon=12°, Venus=7°) |

---

## Correct Calculation Method

### Step 1 — Get positions of Traditional 7 planets + Moon

```python
import swisseph as swe  # pyswisseph (Hermes venv); xalen.swe is API-identical in the dedicated xalen-venv
flags = swe.FLG_SWIEPH | swe.FLG_SPEED

TRAD7 = [(swe.SUN,'Sun'), (swe.MERCURY,'Mercury'), (swe.VENUS,'Venus'),
         (swe.MARS,'Mars'), (swe.JUPITER,'Jupiter'), (swe.SATURN,'Saturn')]

m_arr, _ = swe.calc_ut(jd, swe.MOON, flags)
m_lon = m_arr[0]
m_spd = m_arr[3]
```

### Step 2 — Scan ALL planets (cross-sign) using flatlib personal orbs

```python
# flatlib personal orbs — NOT fixed aspect orbs
PLANET_ORBS = {
    'Sun': 15, 'Moon': 12, 'Mercury': 7, 'Venus': 7,
    'Mars': 8, 'Jupiter': 9, 'Saturn': 9
}

MAJOR_ASPECTS = [(0, 'conj'), (60, 'sext'), (90, 'sq'), (120, 'trine'), (180, 'opp')]

import swisseph as swe
import math

TRAD7 = [(swe.SUN,'Sun'), (swe.MERCURY,'Mercury'), (swe.VENUS,'Venus'),
         (swe.MARS,'Mars'), (swe.JUPITER,'Jupiter'), (swe.SATURN,'Saturn')]

m_arr, _ = swe.calc_ut(jd, swe.MOON, flags)
m_lon = m_arr[0]

for code, name in TRAD7:
    arr, _ = swe.calc_ut(jd, code, flags)
    plon = arr[0]

    # flatlib: closestdistance = signed shortest arc
    d = abs(m_lon - plon)
    if d > 180: d = 360 - d
    abs_sep = d  # this is flatlib's absSep

    for a_ang, a_name in MAJOR_ASPECTS:
        deviation = abs(abs_sep - a_ang)  # flatlib's 'orb' in _orbList
        moon_in_orb = PLANET_ORBS['Moon'] >= deviation
        planet_in_orb = PLANET_ORBS[name] >= deviation

        if moon_in_orb or planet_in_orb:
            # at least one planet's personal orb covers it
            # Moon IS applying to this planet — NOT VOC
            print(f"Moon → {a_name} {name}: dev={deviation:.2f}° "
                  f"(Moon orb={PLANET_ORBS['Moon']}, {name} orb={PLANET_ORBS[name]})")
```

Key difference from simplified check:
- **Do NOT filter by `plon >= m_lon` only** — a planet at 14° in Aries has fwd from Moon at 277° Capricorn = (14 - 277) % 360 = 97°
- **Do NOT filter by `plon < m_sign_end`** — the planet can be in ANY sign

### Step 3 — Find exact VOC start time

Moon VOC starts at the exact moment Moon's **last application perfects**. To find it:

1. Find which planet Moon most recently aspected (backward scan)
2. The aspect perfected the last time Moon was at the aspect position
3. After that moment, Moon is VOC

Example: Moon at ♑ 6.95° — last aspect was to Mars (opposition in ♐ 19.78°).
Next applying aspect: square to Saturn ♈ 14.75° at Moon ♑ 14.75° (284.75°).
So Moon will square Saturn first, then be VOC from 284.75° to 300° (Aquarius ingress).

### Step 4 — VOC end time

```python
m_sign = int(m_lon // 30)
m_sign_end = (m_sign + 1) * 30
deg_to_ingress = m_sign_end - m_lon
hours_to_ingress = deg_to_ingress / m_spd * 24
```

---

## Common Mistakes

| Mistake | Why it's wrong |
|---------|---------------|
| Only checking planets in Moon's sign | Moon can aspect planets in other signs (cross-sign) |
| Assuming Moon VOC based on script output alone | `horary_chart.py` only does in-sign check |
| Saying "Moon VOC today" without checking forward applying aspects | Moon may still have an aspect to perfect before going VOC |

## Worked Example — 27 Jul 2026 (flatlib method)

- Moon ♑ 6.95° (276.95°), speed 11.93°/day
- **Saturn** ♈ 14.75° (14.75°) → shortest arc from Moon = 97.8°
  - Square (90°): deviation = 7.8°
  - Moon orb 12 > 7.8 ✅, Saturn orb 9 > 7.8 ✅ → **applying square Saturn**
  - Perfects at ♑ 14.75° (284.75°) ≈ **28 Jul ~02:25 ICT**
- **Mercury** ♋ 16.81° (106.81°) → shortest arc from Moon = 170.14°
  - Opposition (180°): deviation = 9.86°
  - Moon orb 12 > 9.86 ✅, Mercury orb 7 < 9.86 → but **Moon's orb covers it** ✅
  - Perfects at ≈ **28 Jul ~07:15 ICT**
- **Venus** ♍ 18.98° (168.98°) → shortest arc from Moon = 107.97°
  - Trine (120°): deviation = 12.03°
  - Moon orb 12 < 12.03 ❌, Venus orb 7 < 12.03 ❌ → **both out = NOT yet applying**
  - Comes into Venus orb (7°) at Moon ≈ 281.98° ≈ **~20:51 27 Jul**
  - Perfects at ♑ 18.98° (288.98°) ≈ **28 Jul ~10:57 ICT**
- **Last aspect before Aquarius:** △ Venus at ~10:57
- **VOC window:** After last aspect perfects → until Moon enters ♒
  - Moon enters ♒: 300° ≈ **29 Jul ~09:45 ICT**
