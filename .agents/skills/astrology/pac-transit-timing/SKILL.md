---
name: pac-transit-timing
description: "Use when BooM asks PAC upload timing. Fast answer first."
version: 1.0.0
author: Turboz
license: MIT
tags: [astrology, transit, electional, pick-a-card, pac, timing, instagram, tiktok]
---

# PAC Transit Timing

Use when BooM asks practical timing for uploading/recording Pick A Card content, e.g. “what time should I upload a Pick A Card clip today”, “what time should I upload PAC”, “check transit before uploading a clip”.

## Core rule — fast answer first

BooM corrected that full database/source workflow is too slow for urgent PAC posting decisions. For practical timing questions, **answer in fast mode first**. Do not open heavy database/PDF/source workflows before giving the actionable time unless BooM explicitly asks for sources, audit, or detailed reasoning.

Fast mode should return:

1. **Best exact time** first.
2. Wider safe window.
3. Avoid windows.
4. 3–5 concise reasons max.
5. Optional topic/hook if useful.

## Calculation checklist

Use current/requested date, BooM timezone Asia/Bangkok, and Chiang Rai unless another location is specified.

Fast calculations:

- Western tropical local chart: Moon sign/aspects, ASC/MC at candidate windows.
- **Moon VOC check is mandatory** for every recommended posting window. Use the shared flatlib/pyswisseph VOC method: Traditional 7 planets, cross-sign aspects, personal orbs. If the chosen window is not VOC, say so explicitly; if it is VOC, reschedule unless BooM deliberately wants drift/low-attachment energy.
- Content factors: Moon, Mercury, Venus, Neptune; avoid hard Moon–Saturn/Mars for accessible love PACs.
- Vedic sidereal filter: Moon nakshatra, Hora.
- Avoid Rahu Kalam, Yamaganda, Gulika unless BooM deliberately wants chaotic/taboo/heavy energy.
- For love PAC, prioritize Venus/Moon/Libra/5th/7th/11th resonance.

## Default output shape

```markdown
Post today: **HH:MM**
Safe window: HH:MM–HH:MM
Avoid: HH:MM–HH:MM because ...

Short reasons:
- Moon ...
- ASC/MC ...
- VOC: clear / if VOC, reschedule
- Hora ...
- Clear of Rahu/Yamaganda/Gulika

Topic that fits the time: “...”
```

## Content-topic mode

Use this when BooM asks "what content should I make today", "what PAC topic should I make", or asks for content themes after a daily transit check. Keep fast mode: do not open heavy database/PDF workflows unless BooM asks for sources.

Output should prioritize action over theory:

1. Give **one strongest topic first**.
2. Then 3–5 alternate PAC/content topics tied to today's Moon, lunation, Venus/Mars/Mercury/Jupiter/Neptune, 5th/7th/8th/11th/12th themes.
3. Include a ready-to-use hook/caption in BooM's PAC creator style.
4. Warn briefly about any tone to avoid (e.g. Venus–Mars = avoid aggressive/shading tone; use tension as "truth/reveal" instead).
5. If Full Moon/Aquarius/11th factors are active, favor reveal/social/online/community/future-themed topics such as:
   - "Full Moon Reveal: What the Universe Is Revealing to You Right Now"
   - "What They Feel But Choose Not to Say"
   - "What Will Change in Your Life After Today"
   - "Who Is Watching You Right Now"
   - "Message from Your Higher Self: What to Let Go of to Grow"

Template:

```markdown
Make today: **{one strongest topic}**
Hook: "..."

Other options:
1. ... — because transit ...
2. ... — because transit ...

Tone: ...
Avoid: ...
```

## When to expand

If BooM asks “request the source”, “check in detail”, “source-backed”, asks for “information about what time to upload clips using astrology”, or challenges the method, then expand from fast timing into a concise method/research explanation. Use `references/astrology-social-posting-research.md` for the class-level framework: electional astrology + planetary hours + Moon/ASC/MC + Rahu/Yamaganda/Gulika + platform audience timing. Use `references/electional-social-posting-framework.md` for a compact session-ready checklist that combines audience availability with electional filters. Use `references/pac-timing-source-provenance.md` when BooM asks “where does the information come from” or specifically challenges Electional rules / Planetary Hours / Vedic filters.

Expanded mode should still be actionable:

1. Explain that posting timing = **Electional Astrology + platform/audience behavior**, not transit-floating alone.
2. Start with the practical synthesis, then give source categories; do not drown BooM in citations.
3. Include the priority order for love PAC: **Venus Hour > Jupiter Hour > Moon Hour > Mercury Hour**.
4. When citing method provenance, explicitly split: **Source-backed tradition** vs **Turboz interpretive application to PAC/IG/TikTok**. Do not imply a source directly studied PAC upload views unless it actually did.
5. Recommend a lightweight posting log so BooM's actual IG/TikTok analytics can override generic social timing claims after 10–20 posts.

## Pitfalls

- Do not spend minutes extracting database passages before answering an urgent posting-time question.
- Do not confuse Transit/PAC timing with Horary. Posting-time selection is transit/electional, not horary.
- Do not give exact-looking times without meaning; each time needs a short reason.
- If no perfect window exists, give the least-bad option and explain what is being avoided.
