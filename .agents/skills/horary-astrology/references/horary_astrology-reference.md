---
title: "horary-astrology — reference material"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "horary_astrology-reference"
tags: [skill-reference, horary-astrology]
source_classes: [synthesis]
status: "verified"
summary: "Deep reference sections moved verbatim out of horary-astrology/SKILL.md so the loaded body stays small."
---

## Radicality Check

Before reading, the chart must pass these tests:

| Rule | If broken → chart not radical |
|------|------------------------------|
| **ASC 3°-27°** | Early (<3°) = question premature; Late (>27°) = matter has passed |
| **Moon not VOC** | Moon Void of Course = no more applying aspects **with any Traditional 7 planet** (Sun, Mercury, Venus, Mars, Jupiter, Saturn) before leaving sign. **Check CROSS-SIGN aspects** — not just planets in the same sign. Moon VOC starts at the **exact time of its last aspect** (do not wait for orb >3°). "Nothing will come of it" — but still check next sign boundary for later development |
| **Saturn NOT in 1st/7th** | Saturn in 1st = querent hindered; Saturn in 7th = matter denied |
| **Lord of hour matches ASC sign** | Traditional rule for electional/horary |

If the chart passes, proceed. If not, still interpret but note the caveats. For follow-up questions (Q2+), see "Multiple Query System" below — you MUST rotate the chart reference point.

## Significator Identification

### Querent (Person Asking)
- Always **Lord of the 1st House (ASC ruler)**
- If female/male and planet matches gender, consider Moon (general significator of the querent)

### Quesited (Matter Asked About)
- **Lord of the house ruling the question** (see house table above)
- If the question involves a specific person, use the house that represents them (e.g., 7th for partner, 10th for boss, 3rd for sibling)

### Algorithm

```python
def get_querent_significator(jd, lat, lon):
    """Returns (planet_code, planet_name) for the querent."""
    asc_arr = swe.houses(jd, lat, lon, b'P')
    asc_lon = asc_arr[1][0]
    asc_sign = int(asc_lon // 30)
    ruler_map = {0: (swe.MARS, "Mars"), 1: (swe.VENUS, "Venus"), 2: (swe.MERCURY, "Mercury"),
                  3: (swe.MOON, "Moon"), 4: (swe.SUN, "Sun"), 5: (swe.MERCURY, "Mercury"),
                  6: (swe.VENUS, "Venus"), 7: (swe.MARS, "Mars"), 8: (swe.JUPITER, "Jupiter"),
                  9: (swe.SATURN, "Saturn"), 10: (swe.SATURN, "Saturn"), 11: (swe.JUPITER, "Jupiter")}
    return ruler_map.get(asc_sign, (swe.MERCURY, "Mercury"))

def get_quesited_significator(house_number, jd, lat, lon):
    """Returns (planet_code, planet_name) for the question matter."""
    cusps, _ = swe.houses(jd, lat, lon, b'P')
    cusp_lon = cusps[house_number - 1]
    cusp_sign = int(cusp_lon // 30)
    ruler_map = {0: (swe.MARS, "Mars"), 1: (swe.VENUS, "Venus"), 2: (swe.MERCURY, "Mercury"),
                  3: (swe.MOON, "Moon"), 4: (swe.SUN, "Sun"), 5: (swe.MERCURY, "Mercury"),
                  6: (swe.VENUS, "Venus"), 7: (swe.MARS, "Mars"), 8: (swe.JUPITER, "Jupiter"),
                  9: (swe.SATURN, "Saturn"), 10: (swe.SATURN, "Saturn"), 11: (swe.JUPITER, "Jupiter")}
    return ruler_map.get(cusp_sign, (swe.MERCURY, "Mercury"))
```

