---
title: "Chinese Almanac Scraping Report — tarot.loveiseveryday.com"
date: "2026-10-03"
type: "source-package"
stage: "Source"
topic: "chinese-astrology"
tags: [chinese-astrology, huangli, source, scraper]
source_classes: [external-web-material]
status: "verified"
---

# Chinese Almanac Scraping Report — tarot.loveiseveryday.com

## Overview
Site: https://tarot.loveiseveryday.com/chinese-calendar
Stack: Astro SSR, server-rendered per date, minimal client hydration
Timezone for today: Asia/Bangkok

## Features observed
- Daily Chinese almanac with Thai UI
- Facts table: Gregorian date/weekday, lunar month-day, ฤกษ์ของวัน, year/month/day stem-branch + Wu Xing element
- Sections: ควรทำ, ไม่ควรทำ, วันชง + ทิศซัวะ, สีมงคลแบบจีน
- Navigation: prev/next day, date picker, month view
- FAQ with JSON-LD FAQPage schema
- SEO/social meta, OG image, canonical

## Endpoints
- /chinese-calendar → today
- /chinese-calendar/YYYY-MM-DD → specific day
- /chinese-calendar/month/YYYY-MM → month view
- /chinese-calendar/pee-chong-YYYY → year clash

## Scripts extracted
- /_astro/Base.astro*.js → imports /_astro/site.BgoT7lds.js
- /_astro/index.astro*.js → imports /_astro/chinese.BbyYSboQ.js
- site.BgoT7lds.js: GA4, consent, PWA, share dialogs, ref tracking
- chinese.BbyYSboQ.js: date picker redirect, today auto-fetch, year-chong checker
- chong.B7uNF4vp.js: branch/element/color tables + relation logic

## Core client data from chong.B7uNF4vp.js
- Stem map 甲-癸 with element + yin/yang
- Branches 子-亥 with Thai name, animal, element
- Wu Xing colors with hex
- Relation tables: harm i, break a, punish o, self-punish s
- rel(e,n) → self/clash/punish/harm/break

## Example: 2026-10-03
- Gregorian: วันเสาร์ที่ 3 ตุลาคม 2569
- Lunar: เดือน 8 วันที่ 23
- ฤกษ์: วันธรรมดา (เฮยเต้า)
- ปี: มะเมีย ธาตุไฟหยาง
- เดือน: ระกา ธาตุไฟหยิน
- วัน: จอ ธาตุทองหยาง

ควรทำ: แต่งงาน, ตกลงหมั้น, สู่ขอหมั้นหมาย, ไหว้บรรพบุรุษ, ขอพร, เดินทาง, ซ่อมแซม, ขุดดินก่อสร้าง, ย้ายบ้าน, ขึ้นบ้านใหม่
ไม่ควรทำ: ฝังเข็ม, ตัดต้นไม้, ทำคาน, สร้างศาลเจ้า, จัดงานศพ, ฝังศพ
วันชง: ปีมะโรง (มังกร), ทิศซัวะ: เหนือ
สีมงคล: เสริม เหลือง/น้ำตาล, เข้ากัน ขาว/ทอง/เงิน, ควรเลี่ยง แดง/ชมพู/ม่วง

## Implementation notes
Server calculates lunisolar → stem-branch → element → ฤกษ์/do-don’t/clash/direction/colors.
Client only handles navigation, today sync fetch, and interactive year-chong checker using static tables.
