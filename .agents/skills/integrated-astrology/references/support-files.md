---
title: "Support Files"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "support-files"
tags: [skill-reference, integrated-astrology]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/integrated-astrology/SKILL.md"
summary: "- `Western Astrology - Planets in Signs and Houses.pdf`: Mercury in 10th = communication central to career."
---

# Support Files

_Moved verbatim out of SKILL.md so the trigger body stays small._

## Database References
- `Western Astrology - Planets in Signs and Houses.pdf`: Mercury in 10th = communication central to career.
- `new-techniques-of-prediction.pdf / Gochara`: judge transits by Bhava, retrograde is stronger for the moment.
```

Do not paste long English quotes unless BooM asks; summarize the relevant passage in English.

## Timing
...

## Source
Calculation: Horary/pyswisseph + Vedic-Prashna/KP/Tajik as needed | Interpretation: ASTROLOGY-BOOKS-DATABASE-backed / fallback cited
```

### E. VOC Moon

**Calculation layer: SHARED with `horary-astrology`** — both skills use the same engine.

BooM's default VOC definition:
- Start = exact time of the Moon's **last major aspect** before sign ingress.
- Check **cross-sign** applying aspects (not just planets in Moon's sign).
- Uses **flatlib personal orbs** (not fixed aspect orbs):

| Planet | Orb |
|:------:|:---:|
| ☽ Moon | **12°** |
| ☉ Sun | 15° |
| ♄ Saturn | 9° |
| ♃ Jupiter | 9° |
| ♂ Mars | 8° |
| ☿ Mercury | 7° |
| ♀ Venus | 7° |

- Do **not** wait until separation orb exceeds 3° — VOC starts at exact aspect time.
- Show Traditional 7 planets first, then all-planets comparison when available.

**Script:** `horary-astrology/scripts/voc_time.py` (shared, implements flatlib `isVOC()` via pyswisseph)

Output format:

```markdown
## 🌙 Moon VOC
| Item | ICT Time |
|---|---|
| Traditional 7 planets | 28 Jul 13:10 ← used |
| All planets | 28 Jul 13:11 |
| Moon enters next sign | 29 Jul 08:45 |
```

## Support Files

| File | What it contains |
|---|---|
| `scripts/integrated_reading.py` | CLI tool for integrated natal + transit readings |
| `scripts/combined_ephemeris.py` | All 18 bodies + midpoints + 90° dial |
| `scripts/voc_time.py` | **Shared** VOC calculator — same engine as `horary-astrology/scripts/voc_time.py`. flatlib `isVOC()` via pyswisseph. |
| `templates/transit-daily.py` | Daily transit script template |
| `references/solar-arc-career-timing.md` | Solar Arc career/job-change timing workflow for BooM: source-backed Solar Arc basics, career house database anchors, calculation recipe, and ranked-window output format. |
| `references/database-backed-prediction-gate.md` | Session-learned hard gate: calculation vs database-backed interpretation, reliable native Windows path access, and required source-line behavior |
| `references/source-discipline-boom.md` | BooM-specific mandatory separation: calculation layer vs Database-backed interpretation vs `multi-search-engine` fallback. Read when doing predictions/timing. |
| `references/astrology-books-database.md` | Database index and best files |
| `references/gochara-transit.md` | Extracted Gochara principles |
| `references/stellium-uranian.md` | Stellium workflow for Uranian TN points |
| `references/swe-houses-xalen.md` | House API differences |
| `references/moon-voc.md` | VOC calculation method — flatlib personal orbs, cross-sign, shared engine |
| `references/local-vs-swiss-transit.md` | Local events vs local chart vs natal overlay |
| `references/neptune-retrograde.md` | Neptune retrograde notes |
| `references/pick-a-card-timing.md` | PAC electional timing |
| `references/pac-content-themes.md` | PAC themes by astro event |
| `references/returns.md` / `venus-return.md` / `saturn-return.md` | Return workflows |
