---
title: "Zi Wei Dou Shu Workflow"
date: "2026-08-09"
type: "note"
stage: "Knowledge"
topic: "ziwei-doushu"
tags: [astrology, chinese-astrology, ziwei, purple-star, natal]
source_classes: [calculation-backed, external-web-material, synthesis]
status: "clean-with-boundaries"
related:
  - "Knowledge/Chinese-Astrology/README.md"
  - "scripts/ziwei_chart.js"
summary: "Zi Wei workflow and limits for Boom Project: natal chart via iztro, interpretation requires sourced material."
---

# Zi Wei Dou Shu Workflow — 紫微斗数

## Project Role

Zi Wei is the **deep natal palace map**. Use it for identity, relationship, money, career, travel/external world, mental blessing, and long-form personal readings.

## Tool

Project script:

```bash
cd "E:/Boom Project"
node scripts/ziwei_chart.js "1996-11-20" 20 "女" "zh-CN"
```

Engine: `iztro` npm package.

## Critical Limit

`iztro` in this project calculates natal chart only.

| Need | Status |
|---|---|
| Natal chart 本命 | OK |
| Natal interpretation | OK with web/source support |
| Daily Zi Wei 流日 | Not supported in current free project tool |
| Yearly/10-year Zi Wei luck | Not supported in current free project tool |

Do not fake daily Zi Wei. Use BaZi 流日 + HuangLi + Western transit for daily work.

## BooM Reference

```txt
命宫: 天府庙 + 左辅 + 右弼
夫妻: 武曲 + 破军
财帛: 身宫
官禄: 天相 + 禄存
福德: 紫微 + 贪狼
迁移: 廉贞化忌
四化: 天机权, 天同禄, 廉贞忌
```

## Interpretation Rule

1. Calculate chart.
2. Extract palace + main stars + brightness + auxiliaries + malefics.
3. Fetch/source meanings before final interpretation.
4. Separate `calculation-backed` from `web-sourced interpretation`.

## PAC Use

Good for:
- “what kind of person are you?” carousel
- love/marriage deep-dive
- career/money signature
- personal branding angle

Bad for:
- daily horoscope unless the missing timing layer is solved later
