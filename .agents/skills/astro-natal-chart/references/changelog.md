---
title: "Changelog"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "changelog"
tags: [skill-reference, astro-natal-chart]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/astro-natal-chart/SKILL.md"
summary: "- **QR code now renders by default** — --frame now defaults to bundled"
---

# Changelog

_Moved verbatim out of SKILL.md so the trigger body stays small._

## Changelog


### v4.3.7 (2026-06-24)

- **QR code now renders by default** — --frame now defaults to bundled rame_small.png.dat instead of being optional

- Updated .gitignore to exclude runtime-generated .png files

- SKILL.md: updated --frame documentation


### v4.3.6 (2026-06-11)


### v4.3.6 (2026-06-11)

- **Fixed QR code transparency**: RGBA frame images now preserve alpha channel when pasted onto the chart (was converting to RGB, causing black background behind transparent QR codes)

- SKILL.md version bumped to 4.3.6


### v4.3.5 (2026-06-11)

- **Moved divider line above ClawHub link and QR code**: thin separator now appears before the ClawHub URL and QR code in the info panel

- **Added frame_small.png.dat**: bundled QR code image for embedding in chart output

- SKILL.md version bumped to 4.3.5


### v4.3.4 (2026-06-11)

- **Moved divider line above ClawHub link and QR code**: thin separator now appears before the ClawHub URL and QR code in the info panel

- **Added frame_small.png.dat**: bundled QR code image for embedding in chart output

- SKILL.md version bumped to 4.3.4


### v4.3.3 (2026-06-11)

- **Moved divider line above ClawHub link and QR code**: thin separator now appears before the ClawHub URL and QR code in the info panel, improving visual separation from the aspects block

- **Added frame_small.png.dat**: bundled QR code image for embedding in chart output

- SKILL.md version bumped to 4.3.3


### v4.3.2 (2026-06-02)

- **Moved aspects & configurations to Info panel**: detailed aspect list with descriptions (from interp panel) now appears in the middle Info panel, below planet/house tables

- **Added text labels to aspect legend**: wheel legend now shows Unicode symbol + text abbreviation (☌ Conj, □ Sqr, △ Trine, etc.)

- **Restored AI conclusion block**: "CONCLUSION" block at bottom of Interpretation panel (was accidentally removed during refactoring)

- SKILL.md version bumped to 4.3.2


### v4.3.1 (2026-06-02)

- **Fixed aspect symbol rendering**: aspect symbols (☌, ☍, □, △, ✶, ⚹, ⚺, ∠) were rendering as rectangles because `segoeuisl.ttf` does not contain them — now all aspect symbols use `seguisym.ttf` via extended `is_z()` check

- **Legend aspect symbols**: replaced text abbreviations (cj/sx/sq/tr/qn/op) in the wheel legend with proper Unicode aspect symbols from `seguisym`

- SKILL.md version bumped to 4.3.1


### v4.3.0 (2026-06-02)

- **`--conclusion FILE` flag**: draw_wheel.py accepts a path to a text file with an AI-generated conclusion

  - Conclusion appears at the bottom of the Interpretation panel, after the houses section

  - Decorative gold separator lines frame the conclusion block

  - Title: «CONCLUSION»

  - Multi-paragraph text is wrapped to panel width (2400px)

  - Works with any AI-generated summary — not rendered if flag is omitted

- **3-phase workflow for OpenClaw agent**: (1) `natal_chart_swe.py --json` → (2) AI generates conclusion → (3) `draw_wheel.py ... --conclusion file.txt`

- SKILL.md version bumped to 4.3.1


### v4.2.0 (2026-06-02)

- **3-column layout**: right panel split into Info (1/3 = 1200px) and Interpretation (2/3 = 2400px)

  - **Info panel (1/3)**: essential data (date, time, place, coordinates, timezone), ASC/MC, planet table with houses, house cusp table, compact aspect list

  - **Interpretation panel (2/3)**: Sun/Moon/ASC interpretation, dominant element, stelliums, retrograde planets, aspects with descriptions, houses with full planet meanings

- **Text wrapping fixed**: `wrap_text()` now uses per-panel width (1200px for Info, 2400px for Interp) — long descriptions properly wrap instead of being clipped

- **Interpretation panel retitled 'INTERPRETATION'**

- **Vertical dividers** between all three columns

- SKILL.md version bumped to 4.2.0


### v4.0.0 (2026-06-01)

- **Full interpretation**: Sun/Moon/ASC sign interpretation, dominant element, stelliums, retrogrades, all 12 houses with meanings and planets

  - Separate interpretation data module: `scripts/interp_data.py`

  - Includes `HOUSE_TEXTS_EN`, `PLANET_MEANING_EN`, `SIGN_KEYWORDS_EN`, `ASPECT_MEANING_EN`

- **Extended house descriptions**: each house now has a detailed 3-sentence description covering multiple life areas

- **Aspect interpretation block**: all aspects listed with orb values and brief interpretation

- **Filename includes person name**: output format is now `{Name}_full_natal_en.png` (e.g. `Anna_full_natal_en.png`)

- **Fixed planet meaning context bug**: planet meanings now correctly reference the planet itself (not the Sun's sign)

- **Separated interpretation data**: `interp_data.py` contains all text constants, `draw_wheel.py` contains rendering logic

- SKILL.md updated with new CLI flags and output file naming


### v3.8.0 (2026-06-01)

- **Fixed element coloring bug**: `Pillow pieslice()` uses a different coordinate system than `cos/sin` — sectors were drawn at mirrored positions, causing wrong element colors (Fire showed as Earth's green, Air as Water's blue, etc.). Replaced `pieslice()` with `draw.polygon()` using explicit `aof(d) = radians(90-d)` coordinate math, which is consistent with planet/symbol positioning.

- **Sector boundaries aligned to zodiac signs**: sectors now start from the beginning of each sign (e.g. 270° for Capricorn), not from the ASC degree. This ensures clean 30° sign sectors regardless of ASC position.

- **Bundled fonts**: `seguisym.ttf` (2.4 MB, zodiac symbols) and `segoeuisl.ttf` (854 KB, cyrillic/latin) are both included in `scripts/` and published with the pack.

- SKILL.md changelog updated.


### v3.7.0 (2026-06-01)

- **Two equal-size wheels**: natal chart with houses (left) and zodiac planet circle (right) — both 2160×2160px

- **Panoramic layout**: 5760×2880 total (2:1), data panel (1440px) between the two wheels

- **Dual-font rendering**: `seguisym.ttf` for zodiac symbols (large, 44pt), `segoeuisl.ttf` for cyrillic/latin/digits — bundled in `scripts/`

- **Per-character font selection**: `rtext()` automatically picks the right font per character — no more tofu

- **Zodiac planet circle**: same planet orbit radius (RP=648) and planet size (r=18) as main wheel

- **Essential data panel**: date, time, place, coordinates, timezone, ASC/MC between the wheels

- **Roman numerals** for house cusps (I–XII)

- **ASC/DSC/MC lines** on zodiac circle

- **Planet, element, aspect legends** below the left wheel

- Bundled fonts: `seguisym.ttf` (zodiac) + `segoeuisl.ttf` (cyrillic/latin) in `scripts/`


### v3.4.0 (2026-06-01)

- **Fixed zodiac symbol rendering**: all font loading now uses a single TrueType font (Segoe UI) with guaranteed Unicode zodiac + Cyrillic support. Symbols like ♈♉♊ render correctly everywhere — wheel, legend, and interpretation text.

- **Unified font system**: replaced separate `get_symbol_font()`/`get_font()` with single cached `font()` function that scans fallback chain and verifies glyph coverage

- **Element legend added**: color-coded legend showing Fire/Earth/Air/Water with colored rectangles

- **Legends fully below wheel**: planet, element, and aspect legends placed at `cy + R_OUTER + 50`, guaranteed zero overlap with the circular chart


### v3.3.0 (2026-06-01)

- **4K resolution**: canvas is now 3840×2160 (was 2840×1800), all elements scaled proportionally

- **Legend moved below wheel**: planet legend, element legend, and aspect legend are now placed entirely below the circular chart area — zero overlap with the wheel

- **Zodiac symbols in all text**: interpretation text uses ♈♉♊... instead of TA/SG/AR/etc. abbreviations

- **Element color legend**: added visual legend showing Fire/Earth/Air/Water color coding used in sign sectors

- Layout: wheel area 2160×2160, text area 1680×2160, legends below wheel in left panel


### v3.2.0 (2026-06-01)

- **Zodiac symbols instead of text abbreviations**: wheel now shows ♈♉♊♋♌♍♎♏♐♑♒♓ instead of AR/TA/GE/etc.

- **2x resolution**: canvas is now 2840×1800 (was 1420×900), all fonts and elements scaled proportionally

- **Planet legend moved to bottom-left**: no longer overlaps the chart wheel; placed below info box

- **Full interpretation fits**: larger text panel (1040px) with bigger fonts ensures all 12 houses + aspects render without truncation

- Added get_symbol_font() helper: uses Segoe UI Symbol for reliable zodiac glyph rendering

- Version bumped: 3.1.0 → 3.2.0


### v3.1.0 (2026-06-01)

- **Unified calculation architecture**: `draw_wheel.py` removed all duplicate astrological calculation code

  - Now calls `natal_chart_swe.py --json` via subprocess for all planetary/house/aspect data

  - Guarantees text and graphical output always match (single source of truth)

- **Added `--json` flag to natal_chart_swe.py**: exports all calculated data (planets, houses, aspects, metadata) as parseable JSON

- **draw_wheel.py now accepts CLI arguments**: `draw_wheel.py [date] [time] [city] [--name NAME]`

  - Default: Matvey's chart (14.12.1991 18:30 Izhevsk)

  - Custom: any date/time/city combination

- **Generated interpretation**: stelliums, key configurations, house-by-house now auto-detected from JSON data rather than hardcoded

- Updated SKILL.md: architecture diagram, JSON format docs, scripts reference

- Version bumped: 3.0.0 → 3.1.0


### v3.0.0 (2026-06-01)

- **Added graphical chart renderer** (`scripts/draw_wheel.py`) using Pillow (PIL)

  - Composite 3840×2160 PNG (4K): circular wheel (left) + house interpretation (right)

  - 12 sign sectors colored by element (fire/earth/air/water)

  - Planet markers with retrograde(℞) indication

  - House cusp lines with numbered divisions

  - ASC/MC highlighted lines

  - Aspect lines color-coded by type (conj/sqr/trine/sext/opp/quinc)

  - Info box with ASC/MC positions and aspect legend

  - Planet legend panel

  - Full house-by-house textual interpretation on the right panel

- **English interpretation**

  - All labels, headers, and interpretation text rendered in English

- **Added Pillow dependency** (installed via `pip install pillow`)

- **Pillow drawing API documented** in SKILL.md

- **Scripts reference table** added to SKILL.md

- Version bumped: 2.1.0 → 3.0.0

- Description updated to mention graphical visualization


### v2.1.0 (2026-05-28)

- **Fixed `.pyd.dat` loading on Windows** — `importlib.util.spec_from_file_location` does not recognize non-standard extensions; added auto-copy to temporary `.pyd` before loading

- **Added Microsoft Visual C++ Redistributable as explicit requirement** — bundled `.pyd` compiled with MSVC 14.44 requires `vcruntime140.dll` and friends

- **Requires Python 3.14.x** — binary extension compiled for CPython 3.14 ABI

- Added Requirements section to SKILL.md with installation instructions

- Updated metadata: version bumped to 2.1.0, description mentions Windows compatibility

- Tested on Windows 10 (10.0.19045, x64) with Python 3.14.5 and VC++ Redist 14.51.36231.0


### v2.0.0 (2026-05-28)

- **Switched to Swiss Ephemeris** (pyswisseph 2.10.3.2) as the primary calculation engine — replaces simplified analytical formulas

- Replaced hardcoded positions with `swe.calc_ut()` using NASA JPL DE431 ephemerides

- House calculation now uses `swe.houses_ex()` (exact iterative Placidus) instead of analytical approximations

- Added retrograde detection via `FLG_SPEED` flag (velocity sign)

- Bundled `swisseph.cp314-win_amd64.pyd` (2 MB) in `scripts/` — no system-wide pip installation required

- Version detection: `swe.__version__` returns int `20230604` — formatted as `vYY.MM.BLD` string

- Expanded city database to 50+ cities with coordinates and timezone data

- Added proper Julian Day conversion through `swe.julday()`

- Removed legacy scripts: `natal_chart.py`, `placidus_iterative.py`, `placidus_meeus.py` and all debug/fix scripts (11 files)

- SKILL.md rewritten in English with full documentation


### v1.x (earlier)

- Initial release using simplified analytical formulas

- Separate iterative and Meeus-based Placidus implementations

- Planet positions calculated with approximate algorithms (0.5–15° error range)

