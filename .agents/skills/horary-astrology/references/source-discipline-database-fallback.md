---
date: '2026-07-27'
tags:
- project
source: hermes-astro-hub/skills/horary-astrology/references/source-discipline-database-fallback.md
---

# Horary Source Discipline — Calculation Is Not Prediction

Use this for every Horary answer to BooM.

## Required layers

### Calculation layer
- `horary-astrology` method: radicality, significators, Moon, applying/separating aspects, dignities, timing, Multiple Query System.
- `hermes_astro` (pyswisseph): chart, houses, aspects, VOC.

### Interpretation layer
1. Open `ASTROLOGY-BOOKS-DATABASE` first.
2. Extract relevant source for:
   - horary rule / Prashna rule,
   - house meaning,
   - planet/aspect meaning,
   - question type (money, worship, travel, mother, friend, work, etc.).
3. If DB lacks the specific situation, load/use `research` as fallback.
4. Label what is Database-backed vs fallback.

## Required answer format

```markdown
## Horary Verdict

### [Calculation]
- ASC ...
- Querent ...
- Quesited ...
- Moon VOC ...
- Main aspect ...

### [Database-backed]
- `prashna-tantra.pdf`: ...
- `Western Astrology - Planets in Signs and Houses.pdf`: ...

### [Multi-search fallback]
- Used/not used + why

### [Interpretation]
...

Source: Calculation ... | Interpretation ...
```

## Pitfall from 27 Jul 2026

BooM corrected that Horary answers must not be delivered from calculation alone. A chart can be correct and still not be a complete prediction unless Database/fallback source was checked and labeled.
