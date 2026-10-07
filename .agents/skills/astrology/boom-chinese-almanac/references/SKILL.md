---
name: chinese-almanac-scraper
description: Scrape tarot.loveiseveryday Chinese calendar pages.
---
# Chinese Almanac Scraper Skill

Scrape and analyze https://tarot.loveiseveryday.com/chinese-calendar

Workflow:
1. Fetch HTML via curl/web_extract
2. Parse facts table: Gregorian, lunar month-day, ฤกษ์, year/month/day stem-branch+element
3. Extract sections: ควรทำ, ไม่ควรทำ, วันชง+ทิศซัวะ, สีมงคลแบบจีน
4. Extract scripts: /_astro/*.js, site.BgoT7lds.js, chinese.BbyYSboQ.js, chong.B7uNF4vp.js
5. Notes: Astro SSR, server rendered per date, client hydration minimal

Endpoints:
/chinese-calendar
/chinese-calendar/YYYY-MM-DD
/chinese-calendar/month/YYYY-MM

Infographic workflow (Thai 黄历 cards, done for 20261004 + 20260411):
1. curl the date page (web_extract backend is search-only, use curl with Chrome UA; scratch dir, not /tmp).
2. Parse: Thai date, lunar month/day, year/month/day pillar+element, ฤกษ์ (แดง/黑道), ควรทำ/ไม่ควรทำ lists, วันชง+ทิศซัวะ, สีมงคล (3 groups).
3. Verify day ganzhi independently via JDN: idx=(jdn+49)%60, jdn=toordinal()+1721425; anchors 1949-10-01=甲子, 2000-01-01=戊午, 2024-02-10=甲辰. Month pillar from solar terms (Qingming→辰 month).
4. Fill templates in infographic/templates/chinese-almanac/ (1080x1920 portrait, 1080x1380, 1380x1080 landscape) → infographic/chinese-almanac-YYYYMMDD/ with infographic.html + 2 variants + source.md.
5. Render PNGs with playwright chromium from project .venv (kernel venv greenlet is broken — run via terminal, not execute_code), device_scale_factor=2, 2s font wait, clip to canvas. Output 2160x3840 / 2160x2760 / 2760x2160.
6. Before rendering, measure overflow: sum canvas children heights + gaps + padding vs canvas height; if >0, shrink dos font/gap and card paddings, re-measure, then render. Long ควรทำ lists (16 items) overflow the portrait layouts that fit 4-item lists — expect to tighten.
7. Pitfall: CSS content:"\u2713" renders literal "u2713" text — use content:"\2713 " (CSS escape + trailing space) for the ✓ bullet.
8. Verify each PNG visually (no edge clipping, no tofu, list fits) before reporting done.

Refining the 20260411 source card (build.py reuses it as the canonical template):
- build.py re-parses 20260411's DOM with load-bearing regexes (class names, `cjk big` anchors, `glabel`/`rel`/`chip` structure, the `font-size:..px;margin-top:2px` ritual inline style) and reuses its `<style>` head for future cards. So when improving it, keep the DOM byte-identical and do all craft in CSS (including `::before`/`::after` for decorative motifs) — zero data risk, and the improvement propagates to every future card automatically.
- 20260411 chong panel design (proven): 3px cinnabar top rule + large faint 冲 CJK watermark (centered, ~10% opacity rose, behind content via z-index) turns the sparse clash card into a designed feature. Active day-element chip gets a gold ring (`box-shadow:0 0 0 3px rgba(212,169,78,.5)`). Swatches stay FLAT (they are Wu Xing color data, not decoration — beveling distorts the value).

16-dos layout (verified 20261110, 16 dos + 2 donts):
- Base CSS on the 20260411 template (proven to fit 16 dos in all 3 sizes exactly), NOT 20261004 (fits only 4 dos). 20260411 has no donts card — fold the 2 donts into the chong card (it has vertical slack next to the tall dos card) via a `.donts-in` block (border-top + red ✗ list). This keeps portrait at 1888/1920.
- If 16 dos items are longer than 20260411's, shrink `.dos li` font (23px→19px portrait/square, 16px landscape) so all fit one line (2-line wrap adds ~34px/item and overflows).
- Day-element mismatch: the source template's colors/logic labels + chips are element-specific. If your day element differs, rebuild them: colors_label = source label with source-element→your-element (Thai+English+CJK stem swapped); logic chips must be sourced from a file that HAS them (wood day 20260411 has water/wood/metal chips; metal day 20261004 has earth/metal/fire chips). For an earth day (戊): mother=fire(ไฟ), self=earth(ดิน), restrainer=wood(ไม้); logic_label='ธาตุดิน (戊)', colors_label='ตามธาตุ 戊 ดิน Earth'.
- All Thai must be extracted programmatically (page text by position from 'The Chinese Almanac' marker, or CJK/ASCII-anchored regexes on source files) — NEVER typed (tone marks go wrong). CJK ganzhi + 'วัว' (Ox) are typed (reliable). The hero first token 'กิง' is a fixed label (identical on 乙 and 辛 days), not stem-specific.
- Site uses LUNAR month pillars (not solar terms): Nov 2026 shows 丑 (Ox) not 亥 (Rat). Confirm via the month page. Use the standard stem for the branch (丙-year 丑-month = 辛丑).

Core logic from chong.B7uNF4vp.js:
- branches 子-亥 with Thai name/animal/element
- Wu Xing colors
- Relation tables clash/harm/break/punish
- rel(e,n) returns self/clash/punish/harm/break
