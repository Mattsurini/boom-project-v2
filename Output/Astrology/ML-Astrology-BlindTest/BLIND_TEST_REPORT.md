---
title: "Astrology Occupation Blind Test — Scientist vs Athlete"
date: "2026-08-26"
type: "insight"
stage: "Knowledge"
topic: "astrology-ml-blindtest"
tags: [boom, astrology, ml, blind-test, statistics]
source_classes: [calculation-backed]
status: "final"
summary: "Blind test result: classical chart-rule scoring predicts occupation at chance level (52.3%, p=0.44)."
related:
  - "Knowledge/Astrology-Research/Datasets/astrodatabank-sci-vs-athlete.jsonl"
---

# Blind Test: Can a Natal Chart Predict Occupation?

## Design
- **Dataset:** 59 records from Astro-Databank (Rodden): 29 scientists (Physics / Mathematics-Statistics categories) + 30 athletes (Boxing / Tennis). First-N alphabetical per category.
- **Blind protocol:** labels hidden during prediction. Charts computed with pyswisseph 2.10 (Placidus, tropical) from birth date/time/place only.
- **Pre-registered rules** (fixed before unblinding):
  - ATHLETE score: Mars in rulership/exaltation (+2 each), Mars angular (+1), Mars conj/trine/sextile Sun or Moon (+1 each), square/opp (+0.5), Mars conj ASC (+1.5)
  - SCIENTIST score: Mercury in rulership/exaltation (+2 each), Mercury angular (+1), Mercury–Saturn aspect (+2), Saturn angular (+1), Saturn rulership (+1), Uranus angular (+1)
  - Predict class with higher score; ties excluded.

## Results

| Set | N | Correct | Ties | Accuracy | Chance | Binomial p (one-sided) |
|---|---|---|---|---|---|---|
| All | 47 | 23 | 3 | **52.3%** | 50% | **0.44** |
| AA-rating only | 38 | 20 | 3 | 55.6% | 50% | 0.31 |

Confusion matrix (all): scientists 15/21 correct; athletes 8/23 correct (model over-predicts "scientist" — Mercury/Saturn rules fired more often).

12 records skipped: no birth time recorded (cannot cast houses).

## Verdict
**No signal above chance.** Classical single-factor dignity/aspect scoring does not distinguish scientist vs athlete charts in this sample. Consistent with published literature (Carlson 1985 Nature; Dean & Kelly meta-analyses; Oshop Project 35 unsupervised clustering failure).

## Caveats
- Small N (47 scored); alphabetical sampling bias.
- Hand-crafted rule scores ≠ all of astrology (no receptions, house rulerships of 6th/10th, profections, whole-sign analysis).
- Result falsifies *this rule set*, not astrology as a whole — but matches the pattern of every rigorous published test.

## Files
- Dataset: `Knowledge/Astrology-Research/Datasets/astrodatabank-sci-vs-athlete.jsonl`
- Raw predictions: `blind_test_results.json` (same folder)
