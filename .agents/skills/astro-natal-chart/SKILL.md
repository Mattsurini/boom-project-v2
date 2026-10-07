---

name: astro-natal-chart

version: 4.3.7

description: Natal chart calculation and interpretation via Swiss Ephemeris.

metadata:

  openclaw:

    requires:

      bins:

        - python

    emoji: "✨"

    homepage: https://github.com/dynamicsAlex/astro-natal-chart

---


# Astrology — Natal Chart


## Engine: Swiss Ephemeris (pyswisseph) + Pillow (PIL)


`natal_chart_swe.py` uses **pyswisseph**. On this host it loads the copy already


installed in the Boom venv (`E:\Boom Project\.venv\Lib\site-packages\swisseph.cp311-win_amd64.pyd`,


pyswisseph **2.10.03**); `Pillow` renders the wheel.


## Requirements (verified 2026-10-06 on this host)


| Requirement | Status here |

|---|---|

| **Python** | Boom `.venv` = **3.11.16** — `".venv\Scripts\python.exe"` works |

| **pyswisseph** | 2.10.03 installed in that venv (import name `swisseph`) |

| **Bundled `.pyd` / `.pyd.dat`** | **NOT PRESENT** in `scripts/`. The loader's bundled-binary → `import swisseph` fallback is what actually runs. Do not assume the bundled binary exists; on a host without `pyswisseph`, install it (`pip install pyswisseph`). |

| **Python 3.14 + MSVC++ redist** | Claimed by older changelog entries, **not required** here — the cp311 wheel is self-contained |

| **Pillow** | present in the Boom venv (needed only for `draw_wheel.py`) |


Run it with the Boom venv, not bare `python`:


```bash

cd "E:\Boom Project"

".venv\Scripts\python.exe" "C:\Users\Turbo\AppData\Local\hermes\skills\astro-natal-chart\scripts\natal_chart_swe.py" 20.11.1996 20:37 chiang-rai

```


---


## Text Output (Swiss Ephemeris)


### Usage


```bash

python scripts/natal_chart_swe.py <date DD.MM.YYYY> <time HH:MM> <city>

python scripts/natal_chart_swe.py 14.12.1991 18:30 Izhevsk

```


### JSON Output (for renderers)


```bash

python scripts/natal_chart_swe.py <date> <time> <city> --json

python scripts/natal_chart_swe.py 14.12.1991 18:30 Izhevsk --json

```


JSON structure:

```json

{

  "date": "14.12.1991", "time": "18:30", "city": "Izhevsk",

  "city_full": "Izhevsk, Russia",

  "lat": 56.8519, "lon": 53.2114, "tz": "Europe/Samara",

  "tz_offset": 4, "jd": 2448605.104167,

  "planets": {

    "Sun":     {"lon": 262.097, "speed": 1.017, "retro": false},

    "Moon":    {"lon": 354.459, "speed": 12.461, "retro": false},

    ...

  },

  "houses": [116.94, 130.43, ...],

  "asc": 116.94, "mc": 352.89,

  "planet_houses": {"Sun": 6, "Moon": 10, ...},

  "aspects": [

    {"p1": "Mercury", "p2": "Venus", "type": "semisextile", "orb": 0.5},

    ...

  ]

}

```


---


## Standard Text Output Format


```

🌟 NATAL CHART  [Swiss Ephemeris vX.XX]

📅 Date: [date]  ⏰ Time: [time]  📍 Place: [city]

🌍 Coordinates: [lat], [lon]  🕐 Timezone: [tz] (UTC+/-offset)

📊 JD: [julian_day]


⬆️ ASC — [sign] [degrees]′

🜨 MC — [sign] [degrees]′


PLANETS:

☀️ Sun — [sign] [degrees]′ [house] [℞] (speed °/day)

🌙 Moon — [sign] [degrees]′ [house]

...


HOUSES:

I house — [sign] [degrees]′

... (all 12 houses)


MAJOR ASPECTS:

☌ Conjunction: [planet]-[planet] (orb: X.X°)

...


INTERPRETATION:

[detailed interpretation]

```


## Aspect Orbs


| Aspect | Symbol | Orb |

|--------|--------|-----|

| Conjunction | ☌ | ±8° |

| Opposition | ☍ | ±8° |

| Square | □ | ±7° |

| Trine | △ | ±7° |

| Sextile | ✶ | ±5° |

| Semisextile | ⚺ | ±2° |

| Quincunx | ⚹ | ±2° |

| Semisquare | ∠ | ±2° |


## Zodiac Signs — Keywords


- ♈ Aries: initiative, energy, impulsiveness

- ♉ Taurus: stability, sensuality, stubbornness

- ♊ Gemini: sociability, intellect, curiosity

- ♋ Cancer: emotionality, nurturing, intuition

- ♌ Leo: creativity, leadership, pride

- ♍ Virgo: analytical, practical, perfectionist

- ♎ Libra: harmony, diplomacy, partnership

- ♏ Scorpio: depth, transformation, intensity

- ♐ Sagittarius: optimism, philosophy, freedom

- ♑ Capricorn: ambition, discipline, responsibility

- ♒ Aquarius: originality, independence, innovation

- ♓ Pisces: intuition, compassion, dreaminess


## Planets — Meanings


- **Sun** — ego, essence, vitality, father

- **Moon** — emotions, subconscious, mother, instincts

- **Mercury** — thinking, communication, learning

- **Venus** — love, beauty, values, finances

- **Mars** — energy, action, aggression, sexuality

- **Jupiter** — expansion, luck, wisdom, growth

- **Saturn** — limitations, discipline, karma, structure

- **Uranus** — change, rebellion, innovation, suddenness

- **Neptune** — illusion, spirituality, creativity, dissolution

- **Pluto** — transformation, power, death/rebirth


## Houses — Life Areas


1. **I (ASC)** — personality, appearance, self-presentation

2. **II** — money, values, resources

3. **III** — communication, siblings, learning

4. **IV (IC)** — home, family, roots

5. **V** — creativity, children, romance

6. **VI** — health, work, routine

7. **VII (DSC)** — partnership, marriage

8. **VIII** — transformation, shared resources, intimacy

9. **IX** — philosophy, travel, higher education

10. **X (MC)** — career, reputation, goals

11. **XI** — friends, hopes, groups

12. **XII** — solitude, subconscious, karma


## Interpretation Guidelines


When interpreting, consider:

1. **Sun** — core personality

2. **Moon** — emotional nature

3. **Ascendant** — mask, first impression

4. **MC** — career aspirations

5. **Stelliums** (3+ planets in one sign/house)

6. **Retrograde planets** — energy turned inward

7. **Major aspects** — personality dynamics

8. **Dominant elements** (fire, earth, air, water)


## Disclaimer


This is an entertainment/educational tool, not a scientific method. Do not make medical or financial predictions based on astrological readings.


---



## Scripts
`scripts/natal_chart_swe.py` (Swiss Ephemeris chart) · `scripts/draw_wheel.py` (Pillow wheel) · `scripts/interp_data.py`. Detail: `references/scripts-reference.md`.

## Reference files — open only when its topic comes up
The body above suffices for a standard pass; opening all of these costs more than the old single file did.

- `architecture.md` — All astrological calculations flow through a single source of truth
- `changelog.md` — - **QR code now renders by default** — --frame now defaults to bundled
- `chart-rendering.md` — The skill includes `scripts/draw_wheel.py` — a full-featured natal cha
- `scripts-reference.md` — | Script | Purpose | Dependencies |
