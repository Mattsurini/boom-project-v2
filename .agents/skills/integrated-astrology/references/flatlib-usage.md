---
date: '2026-07-27'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/flatlib-usage.md
---

# flatlib — Traditional Astrology Library

[flatlib](https://github.com/flatangle/flatlib) is a Python library for Traditional Western Astrology. It wraps Swiss Ephemeris with a simpler object-oriented API and only uses the 7 traditional planets (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn) plus the lunar nodes and fixed stars.

## Installation

```bash
source <venv>/Scripts/activate && uv pip install flatlib
```

Where `<venv>` is the Hermes agent virtual environment (typically `$HOME/AppData/Local/hermes/hermes-agent/venv`).

### ⚠️ Critical: pyswisseph version downgrade

flatlib requires `pyswisseph==2.8.0.post1` or earlier. Installing it **downgrades** any newer version already installed:

```
Installed 2 packages in 23ms
 + flatlib==0.2.3
 - pyswisseph==2.10.3.2
 + pyswisseph==2.8.0.post1
```

**What this breaks:**
pyswisseph 2.8.0.post1 does NOT support Transneptunian points (Cupido–Poseidon, swe.CUPIDO=40 etc.). Uranian astrology calculations will fail after installing flatlib.

**What this keeps:**
All regular planets (Sun–Pluto), houses, aspects, dignities — everything needed for Traditional Astrology.

**To restore full functionality:**
```bash
source <venv>/Scripts/activate && uv pip install pyswisseph==2.10.3.2
```

## Basic usage

```python
from flatlib import const
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart

# Create chart at Chiang Rai, 2026-07-28 13:10 ICT
pos = GeoPos('19n55', '99e50')
date = Datetime('2026/07/28', '13:10', '+07:00')
chart = Chart(date, pos)

# Get planet objects
moon = chart.get(const.MOON)
sun = chart.get(const.SUN)
venus = chart.get(const.VENUS)

print(moon)   # <Moon Capricorn +20:08:04 +12:01:50>
print(sun)    # <Sun Leo +05:12:40 +00:57:20>

# Attributes
moon.sign       # 'Capricorn' (string)
moon.lon        # 290.13 (float, ecliptic longitude)
moon.signlon    # 20.13 (float, degrees within sign)
moon.isDirect()  # True/False
```

## Available planets (Traditional 7)

| Constant | Name | Object ID (string) |
|----------|------|--------------------|
| `const.SUN` | Sun | `'Sun'` |
| `const.MOON` | Moon | `'Moon'` |
| `const.MERCURY` | Mercury | `'Mercury'` |
| `const.VENUS` | Venus | `'Venus'` |
| `const.MARS` | Mars | `'Mars'` |
| `const.JUPITER` | Jupiter | `'Jupiter'` |
| `const.SATURN` | Saturn | `'Saturn'` |

flatlib also supports: `const.NORTH_NODE`, `const.SOUTH_NODE`, `const.CHIRON`, `const.PARS_FORTUNA`, and `const.LIST_FIXED_STARS`.

## Aspect checking

```python
from flatlib.aspects import getAspect

venus = chart.get(const.VENUS)
asp = getAspect(moon, venus)

if asp:
    orb, aspect_type = asp
    print(f'Moon {aspect_type} Venus orb={orb:.2f}')
    # 'Moon Trine Venus orb=0.01'
```

`getAspect` checks the 5 Ptolemaic aspects: Conjunction (0°), Sextile (60°), Square (90°), Trine (120°), Opposition (180°). Default orb is derived from the planet's allowed orb in `const.py` (3° for Moon, 5° for Sun, etc.).

To use a custom orb manually:

```python
delta = abs((moon.lon - venus.lon + 180) % 360 - 180)
for aname, adeg in [('Conjunction',0),('Sextile',60),('Square',90),('Trine',120),('Opposition',180)]:
    orb = abs(delta - adeg)
    if orb <= 3.0:
        print(f'Moon {aname} Venus orb={orb:.2f}')
```

## House systems

flatlib supports many house systems. Set when creating the chart:

```python
from flatlib import const
Chart(date, pos, hsys=const.HOUSES_PLACIDUS)    # default
Chart(date, pos, hsys=const.HOUSES_WHOLE_SIGN)
Chart(date, pos, hsys=const.HOUSES_EQUAL)
Chart(date, pos, hsys=const.HOUSES_REGIOMONTANUS)
```

## VOC with Traditional planets only (user-default method)

> 🔴 **This is the user's DEFAULT VOC method (enforced 27 Jul 2026).**
> See `references/moon-voc.md` for the full definition table + SKILL.md section 0.

flatlib is useful for Traditional VOC calculation because it naturally uses only the 7 planets. To find VOC:

```python
from flatlib import const
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from datetime import datetime, timedelta, timezone

pos = GeoPos('19n55', '99e50')
major_aspects = {'Conjunction': 0, 'Sextile': 60, 'Square': 90, 'Trine': 120, 'Opposition': 180}
obj_ids = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']

# Scan every hour within a sign period
start = Datetime('2026/07/26', '20:00', '+07:00')
end = Datetime('2026/07/29', '10:00', '+07:00')

# (iterate hourly, check moon for any aspect)
```

Note: Because flatlib excludes Uranus, Neptune, Pluto by default, the VOC window it produces may differ from the Swiss-all-planets VOC by several hours. In the July 2026 Moon-in-Capricorn example:

| Definition | VOC start | Notes |
|-----------|-----------|-------|
| Traditional 7 planets (flatlib) | 28 Jul ~19:00 | Only 7 trad planets |
| All planets (Swiss) | 28 Jul ~19:35 | Includes outer planets |

The small difference (35 min) was because Neptune was within square orb with Moon just after Saturn separated.

## See also

- `references/moon-voc.md` — Full VOC calculation methodology and multi-definition comparison
- Skill section 3e — Timezone handling for Swiss Ephemeris
