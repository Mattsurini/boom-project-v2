---
title: "Critical Pitfalls"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "critical-pitfalls"
tags: [skill-reference, horary-astrology]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/horary-astrology/SKILL.md"
summary: "**Do NOT default to Bangkok (13.75°N, 100.5°E).** The ASC and house placements change significantly with latitude — in one test case (Chiang Rai 19.91"
---

# Critical Pitfalls

_Moved verbatim out of SKILL.md so the trigger body stays small._

## Critical Pitfalls

### ⚠️ Always confirm the querent's CURRENT location
**Do NOT default to Bangkok (13.75°N, 100.5°E).** The ASC and house placements change significantly with latitude — in one test case (Chiang Rai 19.91°N vs Bangkok 13.75°N), Saturn moved from 1st house to 12th house on the same chart time, flipping the radicality check. Always:
1. Ask the user where they are right now — it may differ from their birth place
2. Use that lat/lon for casting the horary chart
3. If the user corrects you after the first cast, **recast with the correct coords** — the radicality can change

### ⚠️ Multiple-Question Trap: Don't answer Q2+ from the original chart

**This is the most common error in multi-question horary.** When the querent asks a follow-up question, the reference point shifts per Prashna Tantra. If you look at Q2 using the Q1 chart's houses, you'll get the wrong significators and a wrong answer.

| If you do this | Result |
|---------------|--------|
| ❌ Read Q2's 4th house from Q1's chart | Wrong — you're using the old ASC as reference |
| ✅ Rotate chart so Moon = new ASC, then read new 4th house | Correct — you're answering from the right frame |

**Procedure for Q2 (rain/weather follow-up, or any 2nd question):**
1. Get Moon's current longitude
2. Calculate rotation: `new_ASC = Moon_lon`, so `rotation = Moon_lon - original_ASC_lon` (mod 360)
3. Add rotation to all house cusps from the original Placidus chart
4. The rotated houses are the Q2 chart — interpret normally
5. Read the relevant house (e.g., 4th for weather, 7th for partnership, etc.) from THIS rotated chart, NOT the original

**Verify your work:** after rotation, Moon should be in House 1 (ASC). If it isn't, the rotation is wrong.

**Script:** `scripts/horary_2nd_q.py` automates this rotation for Q2 (Moon reference). Pass the same params as `horary_chart.py`. See also `scripts/horary_chart.py` which is the primary chart cast script.

**Real example (27 Jul 2026):**
- Q1: "Will I go out today?" → ASC ♎ 9.3°, Venus ruler, Moon VOC in ♑ → ❌ not today
- Q2: "Will it rain when I go out?" → rotated Moon ♑ 6.94° to ASC, new 4th house = ♈ Aries (dry), Mars ruler in ♊ (air) → 🌤️ dry, unlikely to rain
- Actual weather verified: 21% rain chance at noon → weather forecast from `wttr.in` is a useful cross-check against the chart for rain questions; the astrology chart shows the *prevailing condition*, while the forecast shows hourly variance.

### ⚠️ 4th house interpretation: Mercury/Venus in 4th ≠ "doing nothing at home"
A benefic (Mercury/Venus) sitting in the 4th house is **not** an automatic "the querent stays home and does nothing." Read the 4th's *ruler* and its aspect to the significators first — the planet physically in the house is the *condition of home*, not the querent's action. Don't collapse "planet in 4th" into "no movement" without checking the ruler and the aspect chain.

### ⚠️ Moon VOC is NOT an automatic "no"
Traditional horary says Moon VOC = "nothing will come of it." **This can be wrong** when the Moon is approaching the quesited's sign within 30° and will conjoin the significator there. In a real case (Jul 2026):
- Moon VOC in ♊ in 3rd house (sibling question) → predicted "brother won't go live"
- Brother **did go live on schedule** despite Moon VOC
- The Moon entered ♋ and conjoined Mercury (brother's significator) within ~24h
- Lesson: Moon VOC = **delayed or weakened, not impossible**. Check what happens at the NEXT sign boundary before concluding "no."

When Moon VOC is the main negative indicator and other radicality checks pass, say "unlikely at this time" rather than "no." Add a qualifier about the next sign boundary.

### ⚠️ Moon VOC — do not check only in-sign (Common Mistake)

**Do not check only the planets in the same sign as the Moon.** The Moon can have applying aspects with planets in other signs, e.g.:

- Moon ♑ 6.95° is applying a square to Saturn ♈ 14.75° — even though Saturn is in ♈ (a different sign)
- Scan forward from the Moon to the position where the aspect perfects
- Until that position is reached → Moon **not yet VOC**
- See the full explanation in the section "Moon VOC — Definition & Calculation"

Note: `horary_chart.py` now computes VOC **cross-sign** via `moon_voc_status` (flatlib personal orbs), so the script's VOC line is reliable. The in-sign-only trap applies when you compute VOC **by hand** — in that case always use the flatlib personal-orb logic above.

### ⚠️ `horary_chart.py` house ruler bug — **Fixed 27 Jul 2026**
Historical: the script once mis-identified a house ruler (Jul 2026, house 2 cusp at ♏ 8.7° returned ♀Venus instead of ♂Mars — a sign-index/cusp-ordering issue). Fixed in the shared layer. Spot-check the script's ruler assignment against the raw cusp data under "HOUSES" only when a reading hinges on it; no routine override needed.

Use ICT (UTC+7) for Thai users. For questions about a specific time window (e.g., "will X happen at 1-2 AM?"), cast the chart for the moment *you understand the question*, not the target event time. Then evaluate Moon position at the target time by advancing degrees (Moon ~13°/day).

**Rule:** Look at the degrees remaining before the applying aspect perfects, and the speed of the faster planet. Full speed reference in Step 6 above.

