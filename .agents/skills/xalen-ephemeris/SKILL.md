---
name: xalen-ephemeris
description: Access XALEN ephemeris for high-precision astronomical calculations in Boom Project astrology.
version: 0.1.0
author: Boom Project, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [astrology, ephemeris, astronomy, precision]
    related_skills: [astro-knowledge-db, astro-pipeline, natal-chart, transit-timeline]
---

# XALEN Ephemeris Skill

## When to Use
- You need high-precision planetary positions for Boom Project astrological calculations
- You want to use XALEN's pure-Rust ephemeris with JPL-class accuracy (sub-arcsecond for Sun, Mercury-Saturn)
- You require Vedic astrology calculations with 50+ ayanamsa systems and nakshatra support
- You need Swiss Ephemeris-compatible API via `xalen.swe` drop-in replacement
- You want to calculate planetary positions, houses, aspects, or fixed star conjunctions

## Prerequisites
- XALEN Python wheel built from source — **NOT on PyPI yet** (the `xalen` package on PyPI is an unrelated XALEN SDK; `import xalen` there gives an API client, not ephemeris). Build: `pip install maturin && git clone https://github.com/vedika-io/xalen-ephemeris.git && cd xalen-ephemeris/crates/xalen-python && maturin develop --release`
- Fallback in this environment: the shared `hermes_astro` layer (Hermes venv, pyswisseph 2.10.03) auto-falls back to `xalen.swe` if pyswisseph is missing; Boom Project `.venv` also has pyswisseph 2.10.3.2 + kerykeion
- Basic understanding of astrological concepts (Julian Day, planetary positions, houses, aspects)
- For Vedic calculations: familiarity with ayanamsa systems and nakshatras

## How to Run
- **xalen is only importable in `C:\Users\Turbo\xalen-venv`** — run scripts with `C:\Users\Turbo\xalen-venv\Scripts\python.exe`. In the Hermes venv, `import xalen` resolves to the unrelated 0.2.0 PyPI SDK (no `swe` submodule).
- For Boom astrology work the normal path is the shared `hermes_astro` layer (Hermes venv): pyswisseph primary, `xalen.swe` auto-fallback — you rarely need to touch xalen directly.
- Direct xalen use (dedicated venv): `import xalen` (native API) or `from xalen import swe` (Swiss-compatible drop-in).

## Quick Reference
- `import xalen` — main XALEN package
- `import xalen.swe` — Swiss Ephemeris-compatible submodule
- `xalen.julian_day(year, month, day, hour)` — calculate Julian Day
- `xalen.planet_position(jd, planet_id)` — get planetary position (0=Sun, 1=Moon, etc.)
- `xalen.full_chart(jd, latitude, longitude)` — generate complete chart
- `xalen.swe.calc_ut(jd, planet, flag)` — Swiss-compatible calculation
- **Transit & Horary (new):**
  - `xalen.planetary_return(jd, body, sidereal=False, ayanamsa=0, search_start_jd=None)` — exact Solar/Lunar/Mars/Jupiter/Saturn return (body: 0=Sun,1=Moon,2=Mars,3=Jupiter,4=Saturn)
  - `xalen.rise_transit_set(jd, body, lat, lon, elevation=0, mode="next")` — rise/transit/set; mode="next" (Swiss forward search) or "window" (24h window)
  - `xalen.twilight_times(jd, lat, lon, elevation=0, twilight_type=0)` — dawn/dusk; 0=Civil(-6°), 1=Nautical(-12°), 2=Astronomical(-18°)
  - `xalen.antiscion(lon_deg)` / `xalen.contra_antiscion(lon_deg)` — solstitial/equinoctial mirrors
  - `xalen.detect_antiscia([(name, lon), ...], orb=1.0)` — detect all antiscia/contra-antiscia contacts
  - `xalen.kp_position_py(sidereal_deg)` — KP 249-division breakdown
  - `xalen.varshaphal(birth_jd, natal_asc_sign, year)` — Varshaphal timing (year_lord, muntha)
  - `xalen.varshaphal_with_transits(birth_jd, natal_asc_sign, year, jupiter_sign, saturn_sign, sun_sign)` — Varshaphal + Tri-Pataki check

## Procedure
1. **Determine calculation needs**: planetary positions, houses, aspects, Vedic calculations, etc.
2. **Choose API level**:
   - High-level: `xalen.full_chart()` or `xalen.planet_position()` for Boom Project integration
   - Swiss drop-in: `xalen.swe` for compatibility with existing Swiss Ephemeris code
3. **Calculate Julian Day** for target date/time (remember: hour includes timezone offset!)
4. **Perform calculations** using appropriate XALEN functions
5. **Format results** for Boom Project output (Plawan, Nut, CK, etc. as appropriate)
6. **Apply token-economy indexing** when creating markdown artifacts

## High-level API Examples

### Basic planetary position
```python
import xalen
# julian_day takes UT: local time MINUS timezone offset (ICT = UTC+7 → subtract 7)
jd = xalen.julian_day(1996, 11, 20, 20 + 37/60 - 7)  # BooM natal: 20:37 ICT = 13:37 UT
sun_pos = xalen.planet_position(jd, 0)  # 0 = Sun
print(f"Sun longitude: {sun_pos['longitude']}°")
```

Body IDs: 0=Sun 1=Moon 2=Mercury 3=Venus 4=Mars 5=Jupiter 6=Saturn 7=Uranus 8=Neptune 9=MeanNode(Rahu) 10=TrueNode 11=Pluto 12=Chiron 13=Ketu(Rahu+180). `planet_position` returns dict with longitude/latitude/distance(AU)/lon_speed/lat_speed/dist_speed(per day)/is_retrograde. Sidereal: `planet_position(jd, 0, sidereal=True, ayanamsa=0)` (0=Lahiri).

### Full chart generation (Vedic)
```python
import xalen
jd = xalen.julian_day(1996, 11, 20, 20 + 37/60 - 7)  # BooM natal chart
chart = xalen.full_chart(jd, 19.91, 99.83, ayanamsa=0)  # Chiang Rai, Lahiri
# 9 grahas (+Ketu) with nakshatra/pada/rashi/lord, Whole-Sign ascendant, MC, ayanamsa_deg, 12 cusps
print(f"Ascendant: {chart['ascendant']}°")
print(f"Sun: {chart['planets']['Sun']}")
```

### Vedic-specific calculations
```python
import xalen
jd = xalen.julian_day(1996, 11, 20, 20 + 37/60 - 7)
xalen.panchang(jd, ayanamsa=0)        # tithi/nakshatra/yoga/karana/vara
xalen.nakshatra(sid_lon)              # name/pada/lord/deity/index
xalen.rashi(sid_lon)                  # e.g. "Simha (Leo)"
xalen.ayanamsa(jd, system=0)          # 17 systems, 0=Lahiri
```

### Houses (14 systems, 0=WholeSign .. 13=Krusinski)
```python
import xalen
h = xalen.houses(jd, 19.91, 99.83, system=2)  # 2 = Placidus
# {"cusps":[12], "ascendant":.., "mc":.., "ic":.., "descendant":.., "vertex":..}
xalen.houses_by_name(jd, 19.91, 99.83, "placidus")
```

### Swiss-compatible API (drop-in for pyswisseph)
```python
from xalen import swe
jd = swe.julday(1996, 11, 20, 20 + 37/60 - 7)  # UT
arr, ret = swe.calc_ut(jd, swe.SUN, swe.FLG_SPEED)
sun_longitude = arr[0]  # (lon, lat, dist, lon_speed, lat_speed, dist_speed)
cusps, ascmc = swe.houses_ex(jd, lat, lon, "P")  # hsys is a STRING ("P"=Placidus); no FLG_HOUSE_* ints exist
```

### Chart calculation flow (per repo)
1. Local time → UT: subtract timezone offset (ICT: −7h)
2. JD: `xalen.julian_day(y, m, d, ut_hour)` / Rust `calendar_to_jd(y, m, d, hour - tz, ...)`
3. Planets: `planet_position` / `swe.calc_ut` (apparent geocentric ecliptic)
4. Sidereal: `sidereal=True, ayanamsa=N` or subtract `xalen.ayanamsa(jd, system)`
5. Houses: `xalen.houses(jd, lat, lon, system)` / `swe.houses_ex`
6. Vedic: `full_chart` / `panchang`; Western: `xalen-western` aspects/dignities/Arabic Lots; fixed stars: `xalen.fixed_star_conjunctions(sid_lon, orb_deg, year)`
7. ΔT: `xalen.delta_t(jd)` (SMH 2016 model) for UT1↔TT corrections

## Verified installed (2026-09-12)

Wheel `xalen-0.6.0-cp38-abi3-win_amd64.whl` built from source and installed into **`C:\Users\Turbo\xalen-venv`** (dedicated venv — NOT the Hermes venv). Run scripts with `C:\Users\Turbo\xalen-venv\Scripts\python.exe`. Verified against BooM natal (1996-11-20 20:37 ICT, Chiang Rai 19.91/99.83): ASC 101.71582° (Cancer 11.7°) and Venus 206.92131° (Libra 26.9°) both match the user's known chart exactly; native-vs-swe Sun delta 0.00e+00°.

**Body ID mapping — the two APIs use DIFFERENT IDs:**
- Native `xalen.planet_position(jd, id)`: 0=Sun 1=Moon 2=Mercury 3=Venus 4=Mars 5=Jupiter 6=Saturn 7=Uranus 8=Neptune 9=Rahu(MeanNode) 10=TrueNode 11=Pluto 12=Chiron 13=Ketu.
- `xalen.swe.calc_ut(jd, id, flg)` uses **SWISS** IDs: 0=Sun 1=Moon 2=Mercury 3=Venus 4=Mars 5=Jupiter 6=Saturn 7=Uranus 8=Neptune **9=Pluto 10=MeanNode 11=TrueNode 15=Chiron** (12=MeanApog, 13=OscuApog). Constants: `swe.SUN/MOON/PLUTO/MEAN_NODE/TRUE_NODE/CHIRON/MEAN_APOG/OSCU_APOG`.
- `swe.houses_ex(jd, lat, lon, "P")` — house system is a **string** ("P"=Placidus), NOT a `FLG_HOUSE_*` int (those constants don't exist on `xalen.swe`). Its ascmc/cusps layout differs from classic pyswisseph (documented shape-drop-in, not byte-for-byte). For clean houses prefer the **native** `xalen.houses(jd, lat, lon, system=2)` (system 2=Placidus), which returns `cusps[12]`/`ascendant`/`mc`/`ic`/`descendant`/`vertex` correctly.

## Building the Python wheel on Windows (verified 2026-09-12)

No Windows wheel on PyPI (only macOS) — build from source:
1. Rust: `rustup-init.exe -y --profile minimal --default-toolchain stable` (rustup's own downloader can fail with curl error 23 — download `rustup-init.exe` directly from static.rust-lang.org with `--retry` first). Note: rustup's default host on Windows is the **gnu** target, which needs a C linker.
2. Linker: **VS 2022 Build Tools** — `winget install --id Microsoft.VisualStudio.2022.BuildTools --override "--quiet --wait --norestart --nocache --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"`. Then `rustup target add x86_64-pc-windows-msvc && rustup default stable-x86_64-pc-windows-msvc`. (LLVM-MinGW via winget does NOT work: it lacks libgcc.a/libgcc_eh.a, so the gnu target fails at link.)
3. Put MSVC `link.exe` dir on PATH: `/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/<ver>/bin/Hostx64/x64`.
4. Dedicated venv (do NOT install into the Hermes venv — its `xalen` 0.2.0 is the unrelated PyPI SDK and the name collides): `python -m venv C:\Users\Turbo\xalen-venv`.
5. `cd C:\Users\Turbo\xalen-ephemeris\crates\xalen-python && C:\Users\Turbo\xalen-venv\Scripts\python.exe -m maturin build --release -i C:\Users\Turbo\xalen-venv\Scripts\python.exe` → wheel in `target/wheels/`, then `pip install` it into the target venv.
- Repo clone lives at `C:\Users\Turbo\xalen-ephemeris`; venv at `C:\Users\Turbo\xalen-venv`.
- Release build of the full workspace takes ~10 min.

## Pitfalls
- **Timezone handling**: `julian_day` / `julday` hour is **UT** — subtract the timezone offset from local time (ICT = UTC+7 → subtract 7). Passing local time shifts the chart by 7h.
- **Python environment**: The `xalen` 0.2.0 in the Hermes agent venv is the unrelated PyPI SDK (client/errors only) — `import xalen.swe` fails there. Build the ephemeris wheel with maturin into the target venv, or use pyswisseph (Boom `.venv` has 2.10.3.2).
- **xalen.swe gaps** (drop-in is shape-faithful, not 1:1): Transneptunian IDs 40–47 (Cupido..Poseidon) unsupported → use swisseph for TNS; position-altering flags `SEFLG_HELCTR/TOPOCTR/J2000/EQUATORIAL/BARYCTR/XYZ/RADIANS` raise ValueError; speeds are 0.0 unless `SEFLG_SPEED`; `set_ephe_path`/`close` are no-ops.
- **Import conflicts**: If importing `xalen.swe` fails with attribute errors, check for correct constant names:
  - Use `swe.OSCU_APOG` (not `OSC_APOGEE`) for osculating apogee (Lilith)
  - `swe.CHIRON` exists (=15, Swiss ID); native `planet_position` uses 12 for Chiron instead
  - Vertex from `swe.houses()`: `vertex = ascmc[3]`
- **Wheel installation**: If building from source, use Windows-style paths with `uv pip install` (not MSYS `/c/...` format)
- **Accuracy expectations**: Moon RMS ~2.8″ vs Swiss Ephemeris is negligible for astrological purposes

## Verification
- Verify that calculations return expected planetary positions for known dates
- Check that Vedic calculations produce correct nakshatra and rashi for BooM natal chart
- Confirm Swiss-compatible API returns same results as pyswisseph for identical inputs
- Validate that output is properly formatted for Boom Project pipeline stages
- Ensure token-economy indexing procedures are followed when creating markdown artifacts