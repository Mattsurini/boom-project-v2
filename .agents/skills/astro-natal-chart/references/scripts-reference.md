---
title: "Scripts Reference"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "scripts-reference"
tags: [skill-reference, astro-natal-chart]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/astro-natal-chart/SKILL.md"
summary: "| Script | Purpose | Dependencies |"
---

# Scripts Reference

_Moved verbatim out of SKILL.md so the trigger body stays small._

## Scripts Reference


| Script | Purpose | Dependencies |

|---|---|---|

| `scripts/natal_chart_swe.py` | **Sole calculation engine.** Text natal chart with `--json` export | swisseph (bundled .pyd), math, os |

| `scripts/draw_wheel.py` | **Renderer only.** Calls `natal_chart_swe.py --json`, draws 5760×2880 chart PNG | subprocess, json, math, os, argparse, Pillow |

| `scripts/seguisym.ttf` | **Zodiac symbol font.** Bundled for correct ♈♉♊... rendering. ~2.4 MB. | — |

| `scripts/segoeuisl.ttf` | **Cyrillic/latin font.** Bundled for cyrillic, digits, latin text. ~854 KB. | — |

| `scripts/swisseph.cp314-win_amd64.pyd.dat` | Bundled Swiss Ephemeris binary (2 MB) | MSVC++ Redist |


### draw_wheel.py — Quick Reference


```bash

# Generate chart with interpretation (default Matvey's data)

python scripts/draw_wheel.py


# Generate for any person

python scripts/draw_wheel.py 24.04.1983 06:00 Izhevsk --name "Alexey"

python scripts/draw_wheel.py 25.10.1985 21:35 Mozhga


# Options:

#   --name "Person Name"  — name shown above the wheel

#   --conclusion FILE     — path to text file with AI-generated conclusion

#   --frame FILE          — path to .png.dat image (QR code). Default: bundled frame_small.png.dat


# Output file:

#   {Name}_full_natal_en.png — chart image with person's name


# AI Conclusion workflow (for OpenClaw agents):

#   Step 1: python scripts/natal_chart_swe.py <date> <time> <city> --json

#   Step 2: AI analyzes JSON and writes conclusion to a file

#   Step 3: python scripts/draw_wheel.py <date> <time> <city> --name "Name" --conclusion <file>

```


### natal_chart_swe.py — Quick Reference


```bash

# Text chart

python scripts/natal_chart_swe.py 14.12.1991 18:30 Izhevsk


# JSON export (used by draw_wheel.py)

python scripts/natal_chart_swe.py 14.12.1991 18:30 Izhevsk --json

```


---


