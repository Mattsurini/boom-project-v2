---
date: '2026-07-27'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/swe-houses-xalen.md
---

# swe.houses() — xalen vs pyswisseph API difference

## The Problem

`swe.houses()` returns different cusps array lengths depending on which Swiss Ephemeris wrapper you import:

| Library | Import | Cusps length | House 1 | House 12 |
|---------|--------|:------------:|:-------:|:--------:|
| pyswisseph | `import swisseph as swe` | 13 | `cusps[1]` | `cusps[12]` |
| xalen | `from xalen import swe` | 12 | `cusps[0]` | `cusps[11]` |

**Both** return `ascmc` as an 8-element list: ascmc[0]=ASC, ascmc[1]=MC, ascmc[2]=RAMC (varies by house system), ascmc[3]=Vertex.

## Normalisation Helper

```python
def houses_normalise(jd, lat, lon, hsys=b'P'):
    """Return (cusps_12, asc, mc) regardless of which swe implementation."""
    cusps_raw, ascmc = swe.houses(jd, lat, lon, hsys)
    cusps_12 = cusps_raw if len(cusps_raw) == 12 else cusps_raw[1:13]
    return cusps_12, ascmc[0], ascmc[1]
```

## House Detection (0° wrap safe)

```python
def house_by_cusps(cusps_12, lon):
    """Return Placidus house number (1-12) for a longitude."""
    for i in range(11):
        c1, c2 = cusps_12[i], cusps_12[i+1]
        if c2 < c1:
            if lon >= c1 or lon < c2:
                return i + 1
        elif c1 <= lon < c2:
            return i + 1
    # House 12 wraps from index 11 back to index 0
    if cusps_12[0] < cusps_12[11]:
        return 12
    return 12 if (lon >= cusps_12[11] or lon < cusps_12[0]) else 12
```

## Verification (BooM's birth chart)

```python
# BooM: 20 Nov 1996 20:37 ICT, Chiang Rai (19.91°N, 99.83°E)
# UTC = 1996-11-20 13:37:00
jd = swe.julday(1996, 11, 20, 13.6167)
cusps, asc, mc = houses_normalise(jd, 19.91, 99.83)
# Expected: asc ≈ 101.7° (♋ 11°42'), mc ≈ 4.3° (♈ 4°16')
```

If your ASC/MC match the reference but house placements differ, the library you're running on has the opposite indexing scheme.
