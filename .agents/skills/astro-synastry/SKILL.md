---
name: astro-synastry
version: 1.1.0
description: Synastry (astrology compatibility) calculation and interpretation.
metadata:
  openclaw:
    requires:
      bins:
        - python
      skills:
        - astro-natal-chart
    emoji: "💫"
    homepage: https://github.com/openclaw/openclaw
---

# Astrology — Synastry (Compatibility)

## Dependencies

**This skill requires `astro-natal-chart`** — use it to calculate or load natal charts for both partners before running synastry analysis.

## Input Parameters

For synastry calculation, data for both partners is needed:
1. **Partner 1:** birth date, birth time, birth place
2. **Partner 2:** birth date, birth time, birth place

If natal chart data is already available in memory (USER.md, cached chart files) — use it directly.

## Calculation Algorithm

1. Calculate (or load from files) natal charts for both partners — use the `astro-natal-chart` skill (`scripts/natal_chart_swe.py`), or `hermes_astro.myhora.get_chart()` for a server-computed chart without a local ephemeris (see `myhora-chart` skill)
2. Calculate cross-aspects between Partner 1 and Partner 2 planets — `scripts/synastry.py`
3. Determine house overlays (Partner 1 planets in Partner 2 houses)
4. Generate interpretation by life areas

## Execution

`synastry.py` imports `natal_chart_swe.py` from the **sibling `astro-natal-chart`
skill directory** and computes both charts itself. It takes **positional birth
data, not `--chart1/--chart2` JSON** — there is no argparse in that script.

```bash
cd "E:\Boom Project"
# 6 positional args: date1 time1 city1 date2 time2 city2
# date format is DD.MM.YYYY; city keys are hyphenated lowercase
".venv\Scripts\python.exe" "C:\Users\Turbo\AppData\Local\hermes\skills\astro-synastry\scripts\synastry.py" \
    20.11.1996 20:37 chiang-rai 14.12.1991 18:30 izhevsk

# optional 2 extra args = display names (otherwise the city name is used)
".venv\Scripts\python.exe" "...\synastry.py" 20.11.1996 20:37 chiang-rai 14.12.1991 18:30 izhevsk BooM Partner
```

Verified 2026-10-06: works under Boom `.venv` python 3.11 with pyswisseph 2.10.03.
Wrong arg count prints a usage line; a bad city exits with the natal engine's error.

From Python:

```python
import importlib.util, sys
spec = importlib.util.spec_from_file_location("syn", r"...\astro-synastry\scripts\synastry.py")
syn = importlib.util.module_from_spec(spec); sys.modules["syn"] = syn; spec.loader.exec_module(syn)
c1 = syn.nc.calc_natal_chart("20.11.1996", "20:37", "chiang-rai")
res = syn.calc_synastry(c1, c2, "BooM", "Partner")
print(syn.format_synastry("BooM", "Partner", c1, c2, res["aspects"],
                          res["house_overlaps_1"], res["house_overlaps_2"]))
```

### Scoring caveats (fixed 2026-10-06, measure before quoting a number)

- **Each planet pair is scored once.** The script previously iterated `(Sun,Moon)`
  *and* `(Moon,Sun)`, so every cross-aspect counted twice and same-planet pairs
  (`Sun-Sun`, `Moon-Moon`, `Venus-Venus`) were dropped entirely — even though they
  carry the highest weights in `KEY_PAIRS`. Both are fixed; identical charts now
  print one `☌ Sun-Sun (conjunction, orb 0.0°)` per body.
- **The overall score is not a calibrated compatibility number.** Across 60 random
  chart pairs it spans **44–91 with a median of 79** — aspect *density* drives it
  more than harmony, so a busy chart outscores a quiet harmonious one. Report it as
  a relative indicator at most, never as "X% compatible".
- **Sphere scores saturate.** The `5 + raw * 1.5` mapping clips at 10 readily; on the
  BooM/Izhevsk sample four of five spheres printed 10/10. Read the aspect list, not
  the bars.
- **Minor aspects are in the same total.** Semisextiles/semisquares/quincunxes use a
  ±1.5° orb and ±1 score; the "no-minor" recomputation shifts the overall score by
  ~4 points (85 → 89), so the total is sensitive to whether minors are counted.

## Output Format

```
💕 SYNASTRY — Compatibility Report
👤 [Name 1]: [birth date], [birth place]
👤 [Name 2]: [birth date], [birth place]

═══════════════════════════════════════
📊 OVERALL COMPATIBILITY SCORE: [X]/100
═══════════════════════════════════════

🔥 PASSION & PHYSICAL ATTRACTION
   Score: [X]/10
   [Mars-Venus, Mars-Mars, Venus-Venus, Pluto aspects]

💞 EMOTIONAL COMPATIBILITY
   Score: [X]/10
   [Moon-Moon, Moon-Sun, Venus-Moon aspects]

🗣️ COMMUNICATION & INTELLECT
   Score: [X]/10
   [Mercury-Mercury, Mercury-Sun, Mercury-Moon aspects]

🎯 SHARED GOALS & VALUES
   Score: [X]/10
   [Jupiter-Jupiter, Sun-Sun, MC-MC aspects]

🏠 FAMILY & DOMESTIC LIFE
   Score: [X]/10
   [4th house, Moon, Venus aspects]

⚡ CONFLICT POINTS
   [description of tense aspects: squares, oppositions]

✨ STRENGTHS OF THE PAIR
   [description of harmonious aspects: trines, sextiles, conjunctions]

🔑 KEY SYNASTRY ASPECTS:
   [table of all cross-aspects]

📋 RECOMMENDATIONS:
   [practical advice for low-score areas]
```

## Synastry Aspect Orbs

Actual values in `SYNSTRY_ORBS` (verified 2026-10-06) — the table below was wrong
before; `semisquare` and `quincunx` are ±1.5° in both, everything else is unchanged:

| Aspect | Symbol | Orb |
|--------|--------|-----|
| Conjunction | ☌ | ±7° |
| Opposition | ☍ | ±7° |
| Square | □ | ±6° |
| Trine | △ | ±6° |
| Sextile | ✶ | ±4° |
| Semisextile | ⚺ | ±1.5° |
| Quincunx | ⚹ | ±1.5° |
| Semisquare | ∠ | ±1.5° |

## Key Synastry Aspects

Weights are `KEY_PAIRS` in the script; unlisted pairs get weight **1.0**.
Orientation matters only cosmetically now (each pair is scored once, in the
canonical direction).

### Weight 4.0 (highest)
- **Sun — Moon** / **Moon — Sun** — deep connection, "recognition"
- **Venus — Mars** / **Mars — Venus** — sexual chemistry, attraction

### Weight 3.0
- **Sun — Sun** — core personality compatibility
- **Moon — Moon** — emotional compatibility

### Weight 2.5
- **Saturn — Sun/Moon** (and the reverse) — stability/seriousness

### Weight 2.0
- **Venus — Venus** — love language
- **Mars — Mars** — energy and conflicts
- **Pluto — Sun/Moon** (and the reverse) — transformative connection

### Weight 1.5
- **Mercury — Mercury** — communication
- **Jupiter — Jupiter** — support and growth
- **Uranus — Venus**, **Neptune — Venus** — unexpectedness / idealization in love

**ASC and MC get no cross-aspect.** `calc_synastry_aspects` iterates only
`chart["planets"]`, which holds the ten bodies only — `asc`/`mc` are separate chart
keys and never compared. So **ASC—ASC and MC—MC described below do not appear in
output**, and `MC`/`IC` in the sphere lists (`values`, `family`) never match
anything: those spheres are effectively driven by Sun/Moon/Venus/Jupiter/Saturn.
Do not promise an ASC/MC overlay from this script.

## House Overlays

When Partner 1 planets fall into Partner 2 houses:
- **I house** — Partner 1 amplifies Partner 2's personality
- **II house** — influence on finances and values
- **V house** — romance, children, creativity
- **VII house** — partnership, marriage (very important!)
- **VIII house** — transformation, intimacy, shared resources
- **X house** — influence on career and status

## Scoring

The score is **not** an additive list of named rules. Verified implementation:

```python
ASPECT_SCORES = {conjunction 3, trine 5, sextile 3, opposition -1, square -3,
                 semisextile 1, semisquare -1, quincunx -1}
score   = ASPECT_SCORES[type] * KEY_PAIRS_weight   # weight defaults to 1.0
raw     = sum(score) / sum(|ASPECT_SCORES[type]| * weight) * 100
overall = clamp(round(50 + raw * 0.5), 10, 95)     # 50 = neutral midpoint
```

Then per sphere: `raw = mean(aspect scores touching that sphere's planet list)`,
`score = clamp(round(5 + raw * 1.5), 1, 10)`.

So the earlier "+3-5 points per trine" style list does not exist, and the score is
normalised **against the pair's own aspect count** — a pair with few aspects is
rescaled, not penalised. Read the caveats above before quoting any number.

## Interpretation Guidelines

- Synastry is a self-discovery tool, not a verdict
- Tense aspects don't mean "incompatibility" — they indicate growth zones
- Absence of aspects between planets is also informative — a "neutral" zone
- Never make categorical conclusions like "you are not right for each other"
- Always frame challenging aspects as opportunities for growth
- Consider the whole chart — a few hard aspects can be outweighed by many harmonious ones

## Disclaimer

This is an entertainment/educational tool, not a scientific method. Do not make life decisions solely based on astrological readings.

---

## Changelog

### v1.1.0 (2026-05-28)
- **Translated to English** — full SKILL.md rewrite from Russian to English
- **Added dependency** — declared `astro-natal-chart` as a required skill
- **Updated metadata** — version bumped to 1.1.0, description notes English language and dependency
- **Added disclaimer** — educational/entertainment use note
- **Expanded interpretation guidelines** — best practices for responsible readings
- **Added changelog section**

### v1.0.0 (earlier)
- Initial release in Russian
- Synastry calculation and interpretation workflow
- Aspect scoring system
- House overlay analysis
