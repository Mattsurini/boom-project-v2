---
date: '2026-07-27'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/xalen-ephemeris.md
---

# XALEN Ephemeris — Rust Astrology Engine (Python Bindings)

> **Installed 27 Jul 2026.** Now available on PyPI as `pip install xalen` (v0.6.0+). On BooM's system, pre-installed in the hermes-agent venv. Build-from-source instructions below preserved for reference only.

[XALEN Ephemeris](https://github.com/vedika-io/xalen-ephemeris) is a pure-Rust astronomical ephemeris for astrology with JPL-class accuracy (VSOP87A + ELP2000-82), zero `unsafe` core, Apache-2.0 license. It provides:

- Planet positions, houses (23 systems), aspects, fixed stars (506 built-in + 8,870 Hipparcos)
- 12+ astrology traditions (Western, Vedic, Chinese, Uranian, Cosmobiology, Horary, etc.)
- Python bindings via PyO3 with a **Swiss Ephemeris-compatible `swe` submodule**
- **Moon RMS ~2.8″ vs Swiss** — sub-arcsecond for Sun + Mercury–Saturn vs JPL DE440

## Installation (build from source — tested on Windows 10, Jul 2026)

XALEN is **not published to PyPI yet**. Install it from source:

### Prerequisites: Rust toolchain

```bash
# Download Rust installer
curl -sSfL -o /tmp/rustup-init.exe https://win.rustup.rs/x86_64

# Install (non-interactive, minimal profile)
/tmp/rustup-init.exe -y --default-toolchain stable --profile minimal

# Add cargo to PATH for the current session
export PATH="$HOME/.cargo/bin:$PATH"

# Verify
rustc --version   # expected: rustc 1.x.x
cargo --version   # expected: cargo 1.x.x
```

### Build & install the Python wheel

```bash
# 1. Activate Hermes venv + ensure Rust on PATH
source <venv>/Scripts/activate
export PATH="$HOME/.cargo/bin:$PATH"

# 2. Clone (shallow — saves time/space)
git clone https://github.com/vedika-io/xalen-ephemeris.git --depth 1
cd xalen-ephemeris/crates/xalen-python

# 3. Ensure maturin is installed in the venv
uv pip install maturin

# 4. Build the wheel (1–2 min first build)
export PYO3_PYTHON="<venv>/Scripts/python.exe"
maturin build --release --compatibility off
#   → wheel written to: ../../target/wheels/xalen-*.whl

# 5. Install the wheel (use absolute Windows path)
uv pip install "$(pwd)/../../target/wheels/xalen-0.6.0-cp38-abi3-win_amd64.whl"
```

### ⚠️ Windows-specific gotchas

| Issue | Symptom | Fix |
|-------|---------|-----|
| **Maturin Python detection** | `"could not determine version from interpreter name 'python.exe'"` | Set `PYO3_PYTHON=<venv>/Scripts/python.exe` before building |
| **Wheel path with uv** | `"Distribution not found"` because path is `/c/Users/...` format | Use Windows path `C:/Users/...` (forward slashes OK) instead of MSYS `/c/...` |
| **Import fails on abi3 wheel** | `ModuleNotFoundError: No module named 'xalen.xalen'` | cd out of the repo directory before importing; the repo's `xalen/__init__.py` shadows the installed package. Run `cd ~` or any other directory. |
| **flatlib conflict** | Installing flatlib downgrades pyswisseph to 2.8.0.post1 | Reinstall after flatlib work: `uv pip install pyswisseph==2.10.3.2` |

## API: two ways to use it

### A) High-level: `xalen.full_chart()` / `xalen.planet_position()`

```python
import xalen

# Julian Day (UT — hour includes timezone offset!)
jd = xalen.julian_day(2026, 7, 28, 6 + 10/60)  # 13:10 ICT = 06:10 UTC

# Planet position — returns dict with all fields
pos = xalen.planet_position(jd, 0)  # 0=Sun
print(pos['longitude'], pos['latitude'], pos['distance'])

# Full chart for a location
chart = xalen.full_chart(jd, 19.91, 99.83)  # Chiang Rai
print(chart['ascendant'], chart['mc'])
print(chart['planets']['Sun'])
```

Planet IDs: 0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars, 5=Jupiter, 6=Saturn, 7=Uranus, 8=Neptune, 9=Pluto, 10=Mean Node, 11=True Node, 12=Chiron.

### B) Swiss drop-in: `xalen.swe`

```python
from xalen import swe

# Identical API to pyswisseph
jd = swe.julday(2026, 7, 28, 6 + 10/60)
arr, ret = swe.calc_ut(jd, swe.MOON, swe.FLG_SPEED)
print(arr[0])  # ecliptic longitude

# Houses, aspects, ayanamsa — all supported
cusps, ascmc = swe.houses_ex(jd, 19.91, 99.83, b'P')
```

## Accuracy vs Swiss Ephemeris

| Body | XALEN vs Swiss (typical) |
|------|-------------------------|
| Sun | ~0.2″ |
| Moon | ~2.8″ RMS |
| Mercury–Saturn | ≤0.76″ |
| Uranus/Neptune | ~1.8–2.5″ |

For the Moon, this is negligible for astrological purposes — the difference at practical orbs is effectively zero.

## Pitfalls & API quirks (learned 27 Jul 2026)

### `swe.OSCU_APOG` not `swe.OSC_APOGEE`

The Lilith (Black Moon Lilith / osculating apogee) constant in xalen's `swe` module is `swe.OSCU_APOG`. `swe.OSC_APOGEE` does not exist and raises `AttributeError`.

### Chiron constant

No `swe.CHIRON` constant. Use the Swiss Ephemeris integer ID:
```python
swe.calc_ut(jd, 15, swe.FLG_SWIEPH)  # 15 = Chiron
```

### Vertex

Vertex is available from `swe.houses()`:
```python
_, ascmc = swe.houses(jd, lat, lon, b'P')
vertex = ascmc[3]  # [0]=ASC, [1]=MC, [2]=?, [3]=Vertex
```

### Part of Fortune

Standard formula: `(ASC + Moon - Sun) % 360` for day births, `(ASC + Sun - Moon) % 360` for night births. Cross-verify against Astro-Seek output when available.

### Mean vs True Node

Both `swe.MEAN_NODE` and `swe.TRUE_NODE` work. Astro-Seek conventionally displays Mean Node; match against Mean Node unless user asks otherwise.

## When to use XALEN vs Swiss

| Scenario | Preferred |
|----------|-----------|
| Western astrology (10 planets + TNs) | **Swiss** (pyswisseph) — XALEN `swe` module is a pass-through, but Swiss is more battle-tested |
| Traditional Astrology (7 planets) | Either — flatlib or Swiss works fine |
| Vedic / Ayanamsa / Nakshatra | **XALEN** — built-in 50 ayanamsa systems, full nakshatra support |
| Chinese / BaZi / ZWDS | **XALEN** — native support |
| Fixed star conjunctions | **XALEN** — 506 built-in stars, easy query API |
| SVG chart rendering | **XALEN** — built-in chart renderer |
| License compliance | **XALEN** — Apache-2.0 (Swiss Ephemeris has restrictive licensing) |

## See also

- `SKILL.md` section 3c — data source priority (Swiss > .ics > JPL)
- `references/moon-voc.md` — VOC calculation with XALEN `swe` drop-in is identical to Swiss
