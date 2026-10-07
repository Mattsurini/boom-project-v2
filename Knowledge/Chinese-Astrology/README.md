---
title: "Chinese Astrology Hub"
date: "2026-08-09"
type: "note"
stage: "Knowledge"
topic: "chinese-astrology"
tags: [astrology, chinese-astrology, bazi, ziwei, huangli, pac]
source_classes: [calculation-backed, external-web-material, synthesis]
status: "clean-with-boundaries"
related:
  - "Knowledge/Chinese-Astrology/BaZi/README.md"
  - "Knowledge/Chinese-Astrology/ZiWei/README.md"
  - "Knowledge/Chinese-Astrology/HuangLi/README.md"
summary: "Routing hub for adding Chinese Astrology to Boom Project: BaZi as timing core, Zi Wei as natal depth, HuangLi as electional/PAC layer."
---

# Chinese Astrology Hub

## Verdict

เพิ่ม Chinese Astrology ใน Boom Project แบบมีขอบเขต: **BaZi + Zi Wei Dou Shu + HuangLi** เท่านั้นในเฟสแรก

ไม่รวม Feng Shui, Qi Men Dun Jia, Liu Ren, Tai Yi ตอนนี้ เพราะจะบวมและตรวจสอบยาก

## Scope Map

| System | Project role | Best use | Daily use? | Tool/source rule |
|---|---|---|---|---|
| BaZi / Four Pillars 八字 | Timing core | Natal tendency, Da Yun, Liu Nian, Liu Yue, Liu Ri, compatibility | Yes | deterministic calculator first; interpretation must cite source/web |
| Zi Wei Dou Shu 紫微斗数 | Natal palace map | Personality, marriage, wealth, career, life focus | Limited | `iztro` only calculates natal; no fake daily forecast |
| HuangLi / Chinese Almanac 黄历 | Electional/PAC layer | auspicious/avoid activities, clash animal, day quality | Yes | almanac lookup + practical filter for PAC |

## Operating Rule

1. **Calculation and interpretation are separate.** Do not infer stems/branches/stars by memory when a deterministic tool exists.
2. **Chinese systems do not replace Western/Vedic/Thai.** They become a parallel evidence lane.
3. **PAC output must be practical.** Use Chinese Astrology to sharpen timing/angle, not to create theory dumps.
4. **No paid API push.** If free tools have limits, state the boundary and use BaZi/HuangLi fallback.

## Folder Layout

```txt
Knowledge/Chinese-Astrology/
  README.md                 # this hub
  BaZi/README.md            # BaZi workflow and boundaries
  ZiWei/README.md           # Zi Wei workflow and boundaries
  HuangLi/README.md         # Almanac/PAC workflow
  References/source-map.md  # source classes and citation policy

Output/PAC/Chinese-Astrology/
  README.md                 # PAC content lane

scripts/chinese_astrology/
  README.md                 # commands and wrapper notes
```

## BooM Baseline Data

- Birth: 1996-11-20 20:37 ICT, Chiang Rai
- BaZi known reference: 丙子 己亥 辛酉 戊戌 — 辛金 day master
- Da Yun known reference: 丙申 age 26–35
- Zi Wei reference: 命宫天府庙+左右, 夫妻武曲破军, 财帛=身宫, 迁移廉贞化忌

## Next Build Phase

1. Add/verify deterministic BaZi CLI inside project or keep skill-backed workflow documented.
2. Build a small daily Chinese Astrology report template for PAC.
3. Add source excerpts only after fetching real web/source material for interpretations.
