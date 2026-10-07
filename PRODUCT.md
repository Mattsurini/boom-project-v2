# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

BooM's Instagram followers — a Thai-speaking astrology audience. They open a daily
post and want an accurate, on-brand read of the day (Chinese almanac / HuangLi,
and astrology) that they can act on (what to do, what to avoid, which colors) or
save. The posted PNG is the artifact that is designed for; BooM as the operator
is the producer, not the design target.

## Product Purpose

Turn verified almanac and astrology data into post-ready, accurate, on-brand
social graphics. The deliverable is a rendered PNG in Instagram sizes — not a
website, not a dashboard. Success = the number on the card is right, the Thai
reads correctly, and the image is ready to post with no manual rework.

## Positioning

Accuracy is the product. Every number on the card traces to a real source —
JDN-verified Ganzhi (day/year/month pillar + element), scraped Thai almanac
facts, and Wu Xing color logic — so a generic IG-graphic tool cannot truthfully
copy the guarantee. Thai-first, bilingual labels. This is the social-content
surface of the larger convergence-astrology brand (Vedic + Western + Chinese +
tarot); it is not a standalone consumer app.

## Operating Context

- Data source: `tarot.loveiseveryday.com/chinese-calendar` (scraped, Thai,
  server-rendered per date) plus local Gan-Zhi scripts in the project venv:
  `scripts/chinese_almanac_accurate.py`, `chinese_almanac_web_like.py`,
  `chinese_almanac_zhdate.py`. Cached scrapes live in
  `Output/Sources/Chinese-Astrology/`.
- Pipeline (per date): scrape the date page → `build.py` (parse Thai facts by
  position from the "The Chinese Almanac" marker, write `facts.json`, emit 3
  HTML sizes from templates) → `render.py` (Playwright chromium,
  `device_scale_factor=2`, ~2s font wait, clip to canvas) → PNG.
- Canonical sizes: 1080x1920 (portrait), 1080x1380 (IG portrait), 1380x1080
  (landscape). Rendered at 2x → 2160x3840 / 2160x2760 / 2760x2160.
- Templates: `infographic/templates/chinese-almanac/` (one per size). Per-date
  output dir: `infographic/chinese-almanac-YYYYMMDD/` holding the 3 HTML files,
  3 PNGs, `facts.json`, and a `source.md` fact sheet.
- Rendering runs from the project `.venv` (the kernel venv's greenlet is broken
  — render via terminal, not the execute_code kernel).
- Before rendering, measure overflow: sum canvas children heights + gaps +
  padding vs canvas height; if >0, tighten font/gap/padding and re-measure.
  Long "should do" lists (16 items) overflow layouts that fit 4-item lists.

## Capabilities and Constraints

- Thai text must be extracted programmatically from the source (page text by
  position, or CJK/ASCII-anchored regexes) — NEVER typed by hand, because typed
  Thai gets tone marks wrong. CJK Ganzhi characters and the fixed Thai animal
  name for Ox ("วัว") are typed (reliable).
- Day Ganzhi is verified independently via JDN: `idx=(jdn+49)%60`,
  `jdn=toordinal()+1721425`; anchors 1949-10-01=甲子, 2000-01-01=戊午,
  2024-02-10=甲辰. The site uses LUNAR month pillars (not solar terms).
- Clothing-color advice is Wu Xing-based (wood/fire/earth/metal/water → color
  groups), not personal BaZi luck pillars.
- 16-item "should do" layout: base CSS on the proven 20260411 template (fits 16
  items in all 3 sizes); fold the 2 "avoid" items into the chong card.
- CSS pitfall: `content:"\u2713"` renders literal "u2713" — use
  `content:"\2713 "` (CSS escape + trailing space) for the check bullet.
- Never invent values. If a script or source is missing, state it explicitly
  rather than filling a plausible number.
- Known recurring quality risk: scraped Thai carries broken tone marks, so the
  extracted-not-typed rule and a visual check of every PNG (no tofu, no edge
  clipping, list fits) are mandatory before reporting done.

## Brand Commitments

Part of the convergence-astrology brand (Vedic + Western + Chinese + tarot).
On-brand voice: direct, technical, no fluff. Thai-primary with English
secondary labels. (Grounded in the project operating docs and the existing
artifacts; not separately re-confirmed this session.)

## Evidence on Hand

- `infographic/templates/chinese-almanac/` — 3 proven size templates.
- `infographic/chinese-almanac-20260411/` — proven 16-item layout + `source.md`.
- `infographic/chinese-almanac-20261004/` — metal-day example + `source.md`.
- `infographic/chinese-almanac-20261110/` — latest (16 should-do + 2 avoid).
- `scripts/chinese_almanac_*.py` and `Output/Sources/Chinese-Astrology/` cached
  scrapes.
- Absences future work must not fabricate: there is no live web app, no backend
  API, and no user-facing website — this is a build-to-PNG pipeline. No
  testimonials, customer counts, or performance claims exist.

## Product Principles

1. Accuracy is the product — every number traces to a real source; never invent.
2. Thai-first, extracted-not-typed — tone marks must be right or the artifact fails.
3. Post-ready out of the box — the PNG is the deliverable, in IG sizes, no manual rework.
4. On-brand convergence voice — direct, technical, no fluff; part of the larger brand.

## Accessibility & Inclusion

Thai-speaking audience; Thai and CJK script must render correctly (no tofu, no
broken tone marks) and the layout must fit the canvas at every canonical size.
No other product-specific accessibility requirement was established.
