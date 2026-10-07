---
title: "Chart Rendering"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "chart-rendering"
tags: [skill-reference, astro-natal-chart]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/astro-natal-chart/SKILL.md"
summary: "The skill includes `scripts/draw_wheel.py` — a full-featured natal chart wheel renderer that produces a composite PNG image."
---

# Chart Rendering

_Moved verbatim out of SKILL.md so the trigger body stays small._

## Graphical Chart Rendering (Pillow)


The skill includes `scripts/draw_wheel.py` — a full-featured natal chart wheel renderer that produces a composite PNG image.


**Important:** `draw_wheel.py` does NOT perform its own astrological calculations. It calls `natal_chart_swe.py --json` and renders the returned data. This eliminates data discrepancies between text and graphical output.


### Usage


```bash

# Default (Matvey's data)

python scripts/draw_wheel.py


# Arbitrary birth data

python scripts/draw_wheel.py 24.04.1983 06:00 Izhevsk


# With person name

python scripts/draw_wheel.py 24.04.1983 06:00 Izhevsk --name "Alexey"

```


### Output


| File | Description |

|---|---|

| `{Name}_full_natal_en.png` | Chart image (5760×2880) |


### Image Layout (5760×2880 px)


```n+------------------+---------------------------+------------------+

|                  |                           |                  |

|   NATAL WHEEL    |     ESSENTIAL DATA        |  ZODIAC CIRCLE   |

|   (2160×2160)    |     (1440×2880)           |  (2160×2160)     |

|                  |                           |                  |

|  - Sign sectors  |  - Date, time, place      |  - Sign sectors  |

|  - House cusps   |  - Coordinates, timezone  |  - Planet marks  |

|  - Planet marks  |  - ASC / MC positions     |  - ASC/DSC/MC    |

|  - Aspect lines  |                           |  - Same size as  |

|  - ASC/MC lines  |                           |    natal wheel   |

|                  |                           |                  |

|  --- Legends --- |                           |                  |

|  Planet|Element  |                           |                  |

|  |Aspect       |                           |                  |

+------------------+---------------------------+------------------+

```


### Image Layout (5760×2880 px)


```

+------------------+---------------------------------------------+

|                  |                                             |

|   NATAL WHEEL    |          INTERPRETATION PANEL               |

|   (2160×2160)    |            (3600×2880)                      |

|                  |                                             |

|  - "NATAL CHART" |  - Date, time, place, coordinates, tz       |

|    title + name  |  - ASC / MC positions                       |

|  - Sign sectors  |  - Sun/Moon/ASC sign interpretation         |

|  - House cusps   |  - Dominant element, stelliums, retrogrades |

|  - Planet marks  |  - All 12 houses with cusp positions,       |

|  - Aspect lines  |    house meanings, and planets in each      |

|  - ASC/MC lines  |                                             |

|                  |                                             |

|  --- Legends --- |                                             |

|  Planet|Element  |                                             |

|  |Aspect       |                                             |

|  | ClawHub link |                                             |

+------------------+---------------------------------------------+

```

```


### Font Handling


Two bundled fonts in `scripts/`:


| Font | Purpose | Glyphs |

|---|---|---|

| `seguisym.ttf` (2.4 MB) | Zodiac symbols | ♈♉♊♋♌♍♎♏♐♑♒♓ (U+2648–U+2653) + latin |

| `segoeuisl.ttf` (854 KB) | All other text | Cyrillic, latin, digits, punctuation |


The `rtext()` function selects fonts **per character**: zodiac symbols → `seguisym.ttf`, everything else → `segoeuisl.ttf`. This ensures correct rendering of mixed content like "♈ Aries AR".


**Why not a single font?** No standard Windows font contains both zodiac symbols AND cyrillic. `seguisym.ttf` has zodiac but no cyrillic. `segoeui.ttf` has cyrillic but no zodiac. Per-character selection is the solution.


### Pillow Dependencies


`draw_wheel.py` uses these Python modules:


| Module | Purpose | Install |

|---|---|---|

| `PIL` (Pillow) | Image creation, drawing (circle, ellipse, line, pieslice, text) | `pip install pillow` |

| `math` | Trigonometric calculations (cos, sin, radians) | Stdlib |

| `json` | Parse natal_chart_swe.py JSON output | Stdlib |

| `subprocess` | Call natal_chart_swe.py --json | Stdlib |

| `os`, `sys` | File path operations | Stdlib |

| `argparse` | CLI argument parsing (`--name`, `--conclusion`, `--frame`) | Stdlib |


Note: `draw_wheel.py` does NOT import `swisseph` directly. It receives all planetary data from `natal_chart_swe.py --json`.


---


