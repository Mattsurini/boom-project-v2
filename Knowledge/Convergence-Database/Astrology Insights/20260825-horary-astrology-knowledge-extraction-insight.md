---
title: "Insight — Horary Astrology Knowledge Extraction"
date: "2026-08-25"
type: insight
stage: Knowledge
topic: astrology-convergence
tags: [boom, knowledge, astrology, horary, prashna]
source_classes: [database-backed, skill-derived, session-verified]
status: final
summary: "Distilled horary method: question-as-chart, radicality gates, three-layer verdict (aspect + condition + Moon narrative), VOC nuance, timing rule, and multi-system discipline."
---

# Insight — Horary Astrology Knowledge Extraction

## Core insight / verdict
Horary treats the **question itself as a chart**: cast at the moment the question is fully understood, at the querent's *current* location. The verdict is never one signal — it is three layers stacked: significator aspect (applying/separating), planetary condition (dignity/avastha), and the Moon's narrative (last aspect = past, next applying aspect = what develops). A single layer alone cannot produce a judgment.

## Key principles

### 1. Frame discipline (most common failure mode)
- Q1 reads from the ASC. Follow-up questions rotate per Prashna Tantra: Q2 = Moon, Q3 = Sun, Q4 = Jupiter, Q5 = stronger of Mercury/Venus.
- Reading Q2 from Q1's houses gives wrong significators and a wrong answer. After rotation, verify the reference planet sits in House 1.
- Location matters: ASC/houses shift with latitude (verified case: Saturn moved 1st ↔ 12th between Chiang Rai 19.91°N and Bangkok 13.75°N on the same chart time).

### 2. Radicality gates before judgment
- ASC within 3°–27° (early = premature; late = matter already passed).
- Moon not void-of-course — computed with personal orbs and cross-sign scan, never in-sign-only with fixed orbs.
- Saturn not in 1st (querent hindered) or 7th (matter denied).
- A failed gate is a caveat, not a stop: interpret with the warning stated explicitly.

### 3. Three-layer verdict
| Layer | Question it answers |
|---|---|
| Aspect between L1 and quesited ruler | Will the matter connect? Applying = active/happening; separating = past/fading |
| Dignity + Avastha | Can each side actually deliver? Strong planet delivers despite friction; weak planet fails even with a trine |
| Moon narrative | What just happened (last aspect), what develops next (next applying aspect), when |

- No direct aspect → check Translation of Light (A aspects B, B aspects C) or Collection of Light.

### 4. VOC is delayed, not impossible
Traditional "Moon VOC = nothing will come of it" was falsified in practice: a sibling went live on schedule despite Moon VOC, because the Moon entered Cancer and conjoined his significator within ~24h. Rule: always check the next sign boundary before concluding "no." Phrase as "unlikely at this time" with a qualifier.

### 5. Timing conversion
Degrees remaining to perfection ÷ faster planet's speed → unit:
Moon ~13°/day (days, watch sign changes) · Mercury 1–2°/day · Sun ~1°/day (weeks) · Venus ~1°/day (weeks–months) · Mars ~0.5°/day (months) · Jupiter ~0.08°/day · Saturn ~0.03°/day (years). For "will X happen at time T": advance the Moon to T by degrees and re-check aspects/VOC there.

### 6. Combustion kills applying aspects (Tajik)
If the Ithasala planet is combust (~within 6° of Sun), the positive effect is negated entirely — even Jupiter's trine is void. Retrograde significator similarly weakens perfection.

### 7. Multi-system discipline
Western (tropical whole-sign, Lilly/Frawley), Vedic Prashna (Lahiri, Ithasala/Muthasila/Musaripha), KP (1–249 number → cusp sublord, three golden rules). Never blend silently; label hybrid rotations (Placidus rotated to Moon-ASC) as hybrid, not classical Vedic.

## Evidence class labels
- database-backed: `ASTROLOGY-BOOKS-DATABASE/#Articles/prashna-tantra.pdf` — multiple query rotation (ASC→Moon→Sun→Jupiter→Mercury/Venus), avasthas, house-by-house rules, success probability table.
- database-backed: `Predicting with KP Horary.pdf` — number-based lagna, cusp sublord golden rules, house mapping table.
- database-backed: `Essence_of_Prashna_Techniques.pdf`, `asthamangal prashnam.pdf` — Vedic Prashna technique layer.
- skill-derived (calculation layer): `horary-astrology` SKILL.md — radicality gates, flatlib personal-orb VOC method, significator algorithm, timing speeds; `references/western-horary-deep-rules.md` — prohibition/frustration/refranation, receptions, VoC benefic-signs exception.
- session-verified lessons: location sensitivity case (Saturn 1st↔12th), VOC-not-impossible case (Jul 2026 sibling/TikTok live), house-ruler script bug fixed 27 Jul 2026.

## Practical workflow (condensed)
1. Confirm location + exact moment of understanding + question number.
2. Cast chart (rotate for Q2+; verify rotation).
3. Radicality gates → log warnings.
4. Significators from actual cusp signs (never house-number-as-index).
5. Aspect: applying/separating + orb; fallback Translation/Collection.
6. Condition: dignity + avastha.
7. Moon narrative: last / next applying aspect + VOC scan (cross-sign, personal orbs).
8. Timing via degrees ÷ speed.
9. Verdict Yes/No/Qualified + caveats + source line.

## Related
- Skill: `horary-astrology` (+ references: western-horary-workflow-16-steps.md, moon-voc-calculation.md, source-discipline-boom.md)
- Companion insights: `20260809-transit-reading-principles-insight.md` (hierarchical reading), essential dignities reference (`integrated-astrology/references/essential-dignities.md`)
