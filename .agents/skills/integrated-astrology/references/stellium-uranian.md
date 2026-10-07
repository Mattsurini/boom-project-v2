---
date: '2026-07-27'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/stellium-uranian.md
---

# Stellium — Uranian / Transneptunian Workflow

**Installed:** 27 Jul 2026 · **Version:** 0.22.0
**Backend:** pyswisseph 2.10.3.2 (auto-installed)
**Python:** 3.14 (system) | Also works via `hermes` venv

## What It Does

Stellium is a fluent Python library for astrology that provides:

- Full **Western** (planets, houses, aspects) + **Uranian** (Hamburg school) + **TNOs** + Vedic + Chinese
- **Dial charts** (90°, 45°, 360°) for Uranian analysis
- Transit timelines, returns, progressions
- Chart visualization (SVG) with themes

## Uranian Support — Verification Result (27 Jul 2026)

**8/8 Uranian points work out of the box** with just `.with_uranian()`:

| Point | ID | Works? |
|-------|:--:|:------:|
| Cupido | 40 | ✅ |
| Hades | 41 | ✅ |
| Zeus | 42 | ✅ |
| Kronos | 43 | ✅ |
| Apollon | 44 | ✅ |
| Admetos | 45 | ✅ |
| Vulkanus | 46 | ✅ |
| Poseidon | 47 | ✅ |

No extra ephemeris files needed. The standard Swiss Ephemeris distribution (bundled with Stellium) contains these points.

## Usage Pattern

```python
from stellium import ChartBuilder

chart = (
    ChartBuilder.from_native(
        year=YYYY, month=MM, day=DD,
        hour=HH, minute=MM,
        lat=DD.DDD, lon=DD.DDD,
        timezone_str="Asia/Bangkok",
        name="Chart Name"
    )
    .with_uranian()     # ← Cupido–Poseidon
    .with_tnos()        # ← Eris, Sedna, etc. (requires ephemeris download)
    .calculate()
)

# Access all positions
for pos in chart.positions:
    print(pos.name, pos.longitude)

# Draw 90° dial
chart.draw_dial("output.svg").save()
```

## TNOs (Trans-Neptunian Objects)

TNOs require ephemeris download before they work:
```bash
stellium ephemeris download-asteroid 136199   # Eris
stellium ephemeris download-asteroid 90377    # Sedna
```
As of 27 Jul 2026, TNOs are **not yet downloaded**. They throw `MissingEphemerisWarning` if called with `.with_tnos()`.

## API Notes

- `chart.positions` → tuple of `CelestialPosition` objects (each has `.name`, `.longitude`, `.latitude`, `.distance`, `.speed_longitude`, etc.)
- `chart.get_object("Cupido")` → single position lookup
- `chart.draw_dial(path)` → creates Uranian dial SVG
- `chart.draw(path)` → creates standard natal wheel SVG
- Uranian names are capitalized: "Cupido", "Hades", "Zeus", "Kronos", "Apollon", "Admetos", "Vulkanus", "Poseidon"
- NOTE: It's "Vulkanus" not "Vulcanus" in Stellium

## When to Use Stellium vs pyswisseph

| Task | Engine |
|------|--------|
| Planet positions (Sun–Pluto) | pyswisseph (`import swisseph as swe`) — faster |
| Houses, aspects, transit timing | pyswisseph |
| **Uranian points** (Cupido–Poseidon) | **Stellium** only |
| 90° dial / midpoints | Stellium |
| Chart visualization | Stellium |
| Transit timeline | pyswisseph (faster for basic) |

## Pitfalls

- Stellium depends on `timezonefinder` which requires `numpy` — ensure numpy is compatible with the Python version
- `.with_tnos()` → requires ephemeris download; throws missing-file warnings if run without it
- The `from_notable(name)` method only works for figures in Stellium's built-in notable persons list. For arbitrary charts, always use `from_native()`.
- Stellium is installed at the system level (Python 3.14), not in the Hermes venv (Python 3.11). Calls from terminal() use the system Python.
