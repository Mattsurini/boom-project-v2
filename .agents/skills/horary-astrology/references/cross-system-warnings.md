---
title: "Cross System Warnings"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "cross-system-warnings"
tags: [skill-reference, horary-astrology]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/horary-astrology/SKILL.md"
summary: "Western horary, KP Horary, and Tajik Prashna have different assumptions about:"
---

# Cross System Warnings

_Moved verbatim out of SKILL.md so the trigger body stays small._

## Cross-System & Implementation Warnings

### ⚠️ Don't mix systems without intention
Western horary, KP Horary, and Tajik Prashna have different assumptions about:
- **Orbs**: Western uses fixed orbs (8° conj, 6° sextile, etc); Tajik uses Deeptamsha (planetary-specific orbs: Moon 12°, Sun 15°, Mercury 7°, etc)
- **Lagna determination**: Western = time-based; KP = number-based; Tajik = time-based + omens
- **House systems**: Western/KP use Placidus; Tajik typically uses whole sign
- **Vedic aspects**: In Prashna, only benefics aspect beneficially — malefics have special aspect rules

Best practice: **Decide which system you're using per question** and stick to its rules. Use the table in the Integrated Approach section to pick the right tool for the job.

### KP-Specific: Number must be 1-249
If using KP Horary, the querent must provide a number between **1 and 249**. Numbers outside this range are invalid. The number gives the Lagna — e.g., number 1 = Aries, 2 = Taurus... up to 249 (the 249th division of the zodiac).

### Tajik-Specific: Combustion kills Ithasala
In the Tajik system, if the planet involved in Ithasala (applying aspect) is **combust** (within 6° of the Sun), the positive effect of the Ithasala is negated entirely. Even a trine from Jupiter is useless if Jupiter is combust.

### ⚠️ closest_distance sign convention in Newton refinement (fixed 8 Sep 2026)
`hermes_astro.closest_distance(a, b)` returns the arc **b−a** wrapped to ±180° — NOT a−b. When Newton-refining an exact aspect time (solving m(t) = p(t) + sgn·A), the deviation must be `((m − p − sgn*A + 180) % 360) − 180`. Feeding `closest_distance(m, p)` in directly flips the sign for sextile/trine/square/opposition and the iteration diverges; conjunctions are unaffected (sign cancels at A=0), which is why the bug hid until a sextile ~63h out went missing. Fixed in `horary_chart.py` 8 Sep 2026 — earlier Moon-path output is unreliable for non-conjunct aspects.

### ⚠️ Swiss Ephemeris (pyswisseph / xalen) return format
Both the xalen primary and the swisseph fallback expose the same Swiss API. `swe.calc_ut()` returns **`([lon, lat, dist, spd, ...], flags)`** — a tuple where element [0] is the array and [1] is the status flag. Always unpack as `arr, _ = swe.calc_ut(jd, code, flags)`, then use `arr[0]` for longitude and `arr[3]` for speed. Doing `arr = swe.calc_ut(...)` without destructuring will cause `IndexError` when accessing `arr[3]`.

Note: xalen's `swe.houses`/`houses_ex` return `(cusps[12], ascmc[8])` where `ascmc = (asc, mc, armc, vertex, equatorial_asc, co_asc_koch, co_asc_munkasey, polar_asc)` — the same layout pyswisseph's `houses` returns, so the shared layer's `houses()` wrapper works unchanged on either engine.

### ⚠️ julday expects UTC hours, not local time
`swe.julday(year, month, day, hour_decimal)` treats the hour as **UTC**. Passing a local ICT hour (e.g. 10 instead of 03) will shift the ASC by several signs, producing an entirely wrong chart. Always:
1. Store datetime with `tzinfo=ICT` (UTC+7)
2. Convert to UTC: `dt_utc = dt_local.astimezone(timezone.utc)`
3. Pass UTC components to `julday`

## ASTROLOGY-BOOKS-DATABASE References

The local astrology book repository (`E:\Boom Project\Knowledge\Astrology-Database\`) contains 7 horary/prashna files for deeper reference study:

| File | Tradition | Size |
|------|-----------|:----:|
| `Articles/Horary Astrology the 6th Reader 3.doc` | Western Horary | 151K |
| `Articles/prashna-FINDING LOST ARTICLES USING HORARY ASTROLOGY.doc` | Western / Prashna | 76K |
| `#Articles/Predicting with KP Horary-20100324-193133.pdf` | KP Horary (Indian) | 204K |
| `#Articles/asthamangal prashnam.pdf` | Vedic Prashna | — |
| `#Articles/Essence_of_Prashna_Techniques.pdf` | Vedic Prashna | — |
| `#Articles/prashna-tantra.pdf` | Vedic Prashna | — |
| `Books by Authors/Bhrigu/Bhrigu Prashna Nadi - R.G. Rao.pdf` | Bhrigu Nadi Prashna | — |

Quick search: `find /e/Boom Project/Knowledge/Astrology-Database -iname "*keyword*" 2>/dev/null`

Useful for: consulting traditional horary rules from source texts, KP horary techniques (Ruling Planets, sub-lord theory), and cross-referencing Vedic Prashna approaches when a Western horary chart is ambiguous.

