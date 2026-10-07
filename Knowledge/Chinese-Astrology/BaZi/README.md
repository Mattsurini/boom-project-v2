---
title: "BaZi Workflow — Four Pillars"
date: "2026-08-09"
type: "note"
stage: "Knowledge"
topic: "bazi"
tags: [astrology, chinese-astrology, bazi, four-pillars, timing]
source_classes: [calculation-backed, synthesis]
status: "clean-with-boundaries"
related:
  - "Knowledge/Chinese-Astrology/README.md"
  - "Knowledge/Chinese-Astrology/HuangLi/README.md"
summary: "BaZi operating workflow for Boom Project: deterministic chart/range calculation first, interpretation second."
---

# BaZi Workflow — 八字 / Four Pillars

## Use BaZi For

- Natal profile: Day Master, Ten Gods, element balance, useful/unfavorable tendencies
- Timing: 大运, 流年, 流月, 流日, 流时
- Compatibility: branch clashes/combinations, spouse star dynamics, element balance
- PAC daily angle: day stem/branch, clash, useful activity framing

## Do Not Use BaZi For

- Minute-sensitive Western-style aspect timing
- Zi Wei palace/star interpretation
- Certainty claims about fixed fate

## Calculation Rule

Use deterministic tools, not manual LLM calculation.

Preferred tools:

1. `cantian-bazi` Hermes skill for BaZi chart/ranges/HuangLi
2. `openfate-bazi` where OpenFate MCP is available

When location is available, prefer True Solar Time; label whether it was used.

## BooM Reference

```txt
Birth: 1996-11-20 20:37 ICT, Chiang Rai
Known BaZi: 丙子 己亥 辛酉 戊戌
Day Master: 辛金
Da Yun: 丙申, age 26–35
```

Use this as a quick reference only. For public/prediction work, recalculate or cite the deterministic output.

## Interpretation Template

```md
## Deterministic data
- Chart/range source:
- Time standard:
- Pillars / cycle:

## Interpretation
- Element/Ten-God theme:
- Branch interaction:
- Practical advice:

## PAC angle
- Hook:
- Warning:
- Best action:
```

## Boundaries

- Sect/day-boundary must be stated for 子 hour ambiguity.
- For Thai audience, translate concepts plainly: Ten Gods = roles/psychological drives, not scary jargon.
- If source support is thin, mark interpretation as synthesis and fetch external material before final reports.
