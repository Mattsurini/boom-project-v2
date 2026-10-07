---
title: "Technique Systems"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "technique-systems"
tags: [skill-reference, horary-astrology]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/horary-astrology/SKILL.md"
summary: "A number-based horary system. When the querent provides a number (1-249), use this instead of the standard ASC."
---

# Technique Systems

_Moved verbatim out of SKILL.md so the trigger body stays small._

## KP Horary System (Krishnamurthy Paddhati)

A number-based horary system. When the querent provides a number (1-249), use this instead of the standard ASC.

### KP Rules

1. **Get a number** from the querent (1-249) after they concentrate on the question
2. **Cast Placidus** chart using that number as Lagna, at your location and time of judgment
3. **Test genuineness** — Lagna cusp star lord/sub lord should connect with Moon star lord/sub lord (direct = strong urge, indirect = weak)
4. **Old rule:** If the astrologer is the querent, note down a number that comes to mind after thinking about the question

### Chart Rotation Rules

| Source of question | Action |
|-------------------|--------|
| Person asks about **themselves** | **No rotation** — use 1st house as querent |
| Person asks about **someone else** | **Rotate** — find the house representing that person (e.g., 3rd = sibling, 7th = spouse, 11th = elder sibling) |
| Astrologer asks for **self-interest** | No rotation — check only the house that pertains to the question |

### KP Golden Rules (for Yes/No via cusp sublords)

For every query, find the **main house** and **related houses**. The main house cusp sub lord must satisfy ALL three conditions simultaneously for a YES:

| # | Rule | If Failed → |
|---|------|-------------|
| 3 | Cusp sub lord **NOT retrograde** | ❌ Negative |
| 4 | Sub lord's star lord **NOT retrograde** | ❌ Negative |
| 5 | Sub lord **signifies** related houses | ❌ Negative |
|→| **All 3 satisfied** | ✅ Positive |

### KP House Mapping Table (Main House + Related Houses)

| Matter of Query | Main House | Related Houses |
|-----------------|:----------:|:--------------:|
| Recovery from disease | 11th | 1st, 6th |
| Purchase of household items | 4th | 2nd, 6th, 11th |
| Insurance claims | 11th | 2nd, 8th |
| Scholarship | 8th | 2nd, 4th, 11th |
| Foreign travel | 9th | 3rd, 12th |
| Success in negotiation | 3rd | 9th, 11th |
| Success in PhD/education | 9th | 4th, 11th |
| Winning games/sports | 6th | 5th, 11th |
| Love marriage | 5th | 7th, 11th |
| Unexpected gains | 8th | 2nd, 11th |
| Pilgrimage | 9th | 1st |
| Promotion in service | 10th | 2nd, 6th, 11th |
| Return from foreign trip | 4th | 11th, 2nd, 8th |
| Recovery of lost money | 2nd | 6th, 11th, 12th |
| Job interview | 6th | 11th |
| Business contract | 7th | 11th |
| Litigation | 6th | 11th (also 7th = opponent, 12th = 6th of opponent) |

## Tajik Aspect System (Ithasala / Muthasila / Musaripha)

The Tajik system (from `prashna-tantra.pdf`) uses specific Sanskrit terms for aspect states in horary:

| Term | What it means | Equivalent Western |
|------|---------------|-------------------|
| **Ithasala** / **Itthshala** | Applying aspect — faster planet approaching slower planet within orb | Applying conjunction/sextile/trine |
| **Muthasila** / **Muthaseela** | Mutual aspect — two planets aspecting each other (includes square, opposition) | Any mutual aspect |
| **Musaripha** | Separating aspect — planet that just passed exact aspect with another | Separating aspect |
| **Kamboola Yoga** | Moon conjoining or aspecting a planet with mutual reception | Moon disposition |

### Tajik Aspect Rules

**Ithasala (Applying):**
- Fast planet in lower degree, slow planet in higher degree, within orb → favorable
- Results manifest according to the nature of the aspect (trine = good, square = delay)
- If the planet involved in Ithasala is **combust** or **afflicted by malefics** → the querent will NOT succeed

**Muthasila (Mutual):**
- Direct exchange between houses (e.g., Lord of Lagna in 7th, Lord of 7th in Lagna) → strong connection
- Even squares/oppositions in Muthasila can indicate connection (though stressful)

**Musaripha (Separating):**
- Past event, matter has already peaked
- If the slower-moving planet in Musaripha is afflicted → matter won't return

**Deeptamsha (Orb of Influence):**
- In Tajik, a planet can influence another only within specific degrees (not fixed orbs)
- Rule: the orb depends on the planet involved (Moon: 12°, Sun: 15°, Mercury: 7°, Venus: 8°, Mars: 9°, Jupiter: 9°, Saturn: 9°)

### Tajik Query Table (Planet Mappings by Question Type)

| Question Type | Planets/References |
|---------------|-------------------|
| Employer | Sun (king/ruler), 10th house |
| War / Conflict | Mars (aggressor), 7th (enemy), 12th (querent's strength) |
| Travel | 9th (destination), 3rd (short trip), Lord of ASC position |
| Theft | 2nd (property), 6th (thief), 12th (loss recovery) |
| King & Minister | Sun (king), Jupiter/Mercury (minister), 11th (friendship) |
| Marriage | 7th (spouse), Venus (general), Lord of ASC + Moon |
| Health / Disease | 6th (illness), 8th (death), 10th (treatment), 4th (complications) |
| Missing person | 6th/7th (return signs), Saturn in 3rd (custody), 9th/12th (difficulties) |

## Moon VOC — Definition & Calculation

**VOC definition: see the `integrated-astrology` skill → Section E. VOC Moon** (this is the correct and most up-to-date source)

> Doctor Turboz's VOC calculation uses flatlib's `ChartDynamics.isVOC()`, which checks whether the Moon has applicative or exact aspects with the Traditional 7 planets. If none = VOC
> See full detail + flatlib personal orbs + output format at the `integrated-astrology` skill

Short summary:

```
VOC start = exact time of Moon's LAST aspect with Traditional 7 planets
VOC end   = Moon enters the next sign
do not wait for orb >3°
```

### ❌ Common mistake: checking only in-sign

**Do not check only the planets in the same sign as the Moon** — the Moon can have applying aspects across signs, e.g.:

- Moon ♑ 6.95° is applying a square to Saturn ♈ 14.75° — even though Saturn is in a different sign
- Compute forward from the Moon to the position where the aspect perfects (284.75°)
- Until the Moon reaches that position → Moon is **not yet VOC**

### ✅ Correct calculation method — flatlib personal orbs

**CRITICAL:** flatlib does NOT use fixed aspect orbs (conj 8°, sq 7°, etc.). It uses **PERSONAL ORBS per planet** — the aspect is valid if at least ONE planet's personal orb covers the current angular deviation:

```python
# flatlib personal orbs (from props.object.orb)
PLANET_ORBS = {
    'Sun': 15, 'Moon': 12, 'Mercury': 7, 'Venus': 7,
    'Mars': 8, 'Jupiter': 9, 'Saturn': 9
}
```

**Logic in flatlib's `_aspectDict`:**
```
if obj1.orb() < orb and obj2.orb() < orb:
    continue  # SKIP — both planets out of orb
```
where `orb` = angular deviation from exact aspect. The aspect is valid if EITHER planet's personal orb >= deviation.

Example — Moon ♑ 6.95° vs Saturn ♈ 14.75°, square (90°):
- Angular separation = 97.8° → deviation from 90° = **7.8°**
- Moon orb = 12 → `12 < 7.8` → **False** (Moon is within orb)
- Saturn orb = 9 → `9 < 7.8` → **False** (Saturn is within orb)
- `False AND False` = don't skip ✅ → aspect IS valid

**Step-by-step:**

```
1. Get Traditional 7 planet positions + Moon position
2. For each Traditional 7 planet:
   a. Compute shortest arc distance = closestdistance(moon_lon, planet_lon)
   b. deviation = abs(abs_arc - aspect_angle)
   c. If Moon orb >= deviation OR planet orb >= deviation → aspect valid
3. If there is a valid applying aspect → Moon NOT VOC
4. If none → Moon is VOC from the exact time of the last aspect
```

### Script limitation — resolved (8 Sep 2026)

`horary_chart.py` now calls the shared layer's `moon_voc_status(jd, pos)` — flatlib cross-sign logic with personal orbs. The script's VOC line is now reliable. (Before 8 Sep 2026 it checked in-sign + fixed orbs only — do not trust VOC output from old runs.)

## Interpreting Moon VOC + Saturn in 1st + No Aspect (Triple Warning)

When the chart fires three warnings simultaneously, treat the answer as **qualified negative**:

| Warning | What it means |
|---------|--------------|
| **Moon VOC** | Nothing will come of it — no development |
| **Saturn in 1st** | Querent is hindered, worried, or matter is delayed |
| **No aspect** between significators | Disconnect — no connection between querent and matter |

### How to still find nuance

1. **Moon's next sign change** — Moon will eventually enter a new sign and make new aspects. Does it then contact the quesited significator within 30° (≈5 days)? If yes, matter may develop later even if it misses the current window.
2. **Moon in the quesited's house** — If Moon is physically in the house of the question (e.g., Moon in 3rd house for a sibling question), this connects the querent's emotions to the matter emotionally even if the chart says "no."
3. **Moon as natural significator** — Moon rules Cancer; if the quesited's significator is in Cancer, Moon becomes its dispositor, giving indirect connection.

### Example (from session 12 Jul 2026: sibling + TikTok live)
- Moon VOC ♊ 26.27° in 3rd house (siblings) → Moon in the right house but no applying aspect → **matter won't happen at specified time**
- Saturn ♈ in 1st → BooM worried about brother's live
- ♂ Mars (BooM) vs ☿ Mercury (brother): no aspect
- **Verdict:** ❌ Won't happen at that time. But Moon will ♌☿ Mercury in ♋ in ~30h → maybe later

## Timing for Time-Specific Questions (When will X happen?)

When the question specifies a time window ("at 1-2 AM"), evaluate:

1. **Does the Moon have an applying aspect within that window?** Check by advancing Moon's position to the target time.
2. **Is the Moon VOC at the target time?** If yes → won't happen.
3. **Time to next aspect** — use Moon speed (~13°/day) to compute: `hours_to_aspect = forward_degrees_to_planet / (13/24)`
4. ASC late (>27°) = matter has already passed — question is moot.

## Essential Dignities

Modified for horary:

| Dignity | Score | Meaning |
|---------|:-----:|---------|
| **Rulership** | +5 | In own sign = strong |
| **Exaltation** | +4 | In exaltation = honored |
| **Triplicity** | +3 | In own triplicity |
| **Term** | +2 | In own term |
| **Face** | +1 | In own face |
| **Detriment** | -5 | Opposite sign = weak |
| **Fall** | -4 | Opposite exaltation = debilitated |
| **Peregrine** | 0 | No dignity = weak, neutral |

A strong significator = matter is likely regardless of aspect
A weak significator = matter is unlikely even with a good aspect

## Planetary Avasthas (10 States — from Prashna Tantra)

Planets in a horary chart exist in one of 10 states (Avasthas) that modify the quality of their significations:

| Avastha | Meaning | Effect in Horary |
|---------|---------|------------------|
| **Deeptha** (Illumined) | Planet in own sign/exaltation | ✅ Success in the undertaking |
| **Swastha** (Self-reliant) | Planet in own varga/moolatrikona | ✅ Fame, good reputation |
| **Muditha** (Delighted) | Planet in a friend's sign | ✅ Gain of wealth and happiness |
| **Suveerya** (Powerful) | Planet strong, direct motion | ✅ Access to conveyances and gold |
| **Athiveerya** (Very powerful) | Planet extremely strong | ✅ Political success, valuable contacts |
| **Deena** (Wretched) | Planet in debilitation | ❌ Sorrow, grief |
| **Suptha** (Sleeping) | Planet combust | ❌ Sorrow, fear from enemies |
| **Nipeeditha** (Afflicted) | Planet aspected by malefics | ❌ Loss of money |
| **Mushita** (Loss) | Planet in enemy's sign or fallen | ❌ Failure and loss of money |
| **Pariheena** (Extremely fallen) | Planet debilitated + in enemy sign | ❌ Complete failure, loss |

**Use:** When evaluating a significator, first check its Avastha to determine its overall strength before looking at aspects. A significator in Deeptha or Swastha can deliver results even with a weak aspect. A significator in Deena or Mushita will struggle even with a trine.

## Multiple Query System (Prashna Tantra)

When the querent asks **multiple questions**, the reference point shifts for each successive question (from `prashna-tantra.pdf`):

| Question # | Reference Point |
|:----------:|----------------|
| 1st | **ASC** (standard) |
| 2nd | **Moon** — cast from Moon's position |
| 3rd | **Sun** — cast from Sun's position |
| 4th | **Jupiter** — cast from Jupiter's position |
| 5th | **Mercury or Venus** — whichever is stronger |

**Rule:** If only one question is being asked, always use ASC. The system says "If only one question is answered, the prediction cannot go wrong."

**Research caveat (27 Jul 2026):** `prashna-tantra.pdf` explicitly supports multiple queries: "The first query is to be read from the ascendant, the second from the Moon, the third from the Sun, the fourth from Jupiter and the fifth from the stronger of Mercury or Venus." This is a **Vedic Prashna** rule, not standard Western horary. In a pure Vedic reading, "from the Moon" is best treated as Chandra-lagna / reference-from-Moon, commonly by signs/houses from the Moon. The current `horary_2nd_q.py` method (rotating Placidus cusps so the Moon degree becomes ASC) is a practical hybrid, not a textbook Western method and not guaranteed to be the exact classical Vedic house method. When using it, label the reading as **Vedic Prashna / hybrid calculation**, and avoid presenting it as Western horary.

## Success Probability (Prashna Tantra)

From `prashna-tantra.pdf` — degree-based success estimation:

| Condition | Success Level |
|-----------|:------------:|
| ASC not aspected by its lord or benefic | 25% (1/4) |
| ASC lord aspected by benefics only | 50% (1/2) |
| Even one benefic aspects ASC or its lord | 75% (3/4) |
| Significator aspects Lagna, Lagna Lord, or Moon | 100% (full) |
| ASC lord + significator mutually connected | 100% (full) |

**Key rule from Prashna Tantra:** "The object of the query will not be fulfilled if the significator does not aspect the ascendant or its lord. In a query pertaining to 'success or failure,' no house other than the ascendant can be considered important."

