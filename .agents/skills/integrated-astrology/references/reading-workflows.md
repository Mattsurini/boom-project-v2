---
title: "Reading Workflows"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "reading-workflows"
tags: [skill-reference, integrated-astrology]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/integrated-astrology/SKILL.md"
summary: "**Mode guard:** If BooM explicitly says **'Transit'**, 'look at Transit', 'today's energy', or asks for electional timing like 'what time is good to p"
---

# Reading Workflows

_Moved verbatim out of SKILL.md so the trigger body stays small._

## Reading Workflows

### A. Daily energy / Transit questions

**Mode guard:** If BooM explicitly says **"Transit"**, "look at Transit", "today's energy", or asks for electional timing like "what time is good to post the clip", route here — **do not cast a Horary chart**. Horary answers a specific yes/no question from the question moment; Transit/electional timing judges current sky + natal/local chart windows.

1. Determine date/time in ICT.
2. Check `.ics` locations first for Astro-Seek events:
   - `C:\Users\Fourt\Downloads\astroseek_*.ics`
   - `C:\Users\Fourt\AppData\Local\hermes\scripts\transit_data\*.ics`
3. If `.ics` exists: use `SUMMARY` only; never quote `DESCRIPTION`.
4. Fetch the Western/local chart + transit-to-natal aspects with `myhora-chart` (`get_chart(..., transit=...)`); use XALEN only for exact-time root-finding/VOC.
5. Compute Uranian TN contacts with Stellium.
6. Add Vedic/Jyotish cross-check only when BooM explicitly asks or when the question benefits from sidereal timing.
7. Extract 2–5 database references matching the strongest configurations.
7. If database has no relevant passage for a configuration, load/use `multi-search-engine` for fallback research and cite sources before interpreting.
8. Output with tables:
   - Source line
   - Moon schedule
   - 🟢 supportive transits
   - 🔴 caution transits
   - Uranian notes if relevant
   - One-line summary

### B. Monthly/career/love outlook

1. Define month and timezone explicitly.
2. Scan daily (or every 2–3 days for slow Uranian points) for minimum orb dates.
3. Snapshot beginning/mid/end of month for house shifts.
4. For career: emphasize natal/transit 2/6/10/11, MC, Mercury, Saturn, Jupiter, Mars, Uranian Kronos/Apollon/Vulkanus.
5. For love: emphasize 5/7/8/12, Venus, Moon, Neptune, Pluto, Cupido/Poseidon.
6. Add Vedic/Jyotish cross-check by default: sidereal sign, nakshatra, dasha/gochara factors when available; synthesize with Western/Uranian rather than replacing them.
7. Extract database references for the actual configurations used.
7. If database lacks a relevant source for a configuration, load/use `multi-search-engine` for fallback research and cite sources before interpreting.
8. Output:
   - Overall theme
   - Best windows
   - Caution windows
   - Database-backed interpretation
   - Direct advice

### C. Solar Arc career timing

Use when BooM asks “when is there a chance of getting/changing jobs” or career timing via Solar Arc.

1. Read `references/solar-arc-career-timing.md` first.
2. Treat Solar Arc as the **big year/window indicator**, not the sole verdict.
3. Calculate:
   - `Solar Arc = progressed Sun − natal Sun`
   - `directed point = natal point + Solar Arc`
4. Scan directed factors to natal career factors with hard aspects first: `0°, 45°, 90°, 135°, 180°`, orb under `1°`.
5. Career factors: MC/10th, 6th, 2nd, 11th, rulers, Sun, Mercury, Mars, Jupiter, Saturn, Kronos, Apollon, Vulkanus.
6. Confirm month/week timing with transit triggers and/or Progressed Moon.
7. Output ranked windows with direct meanings. Do not give aspect/date numbers without explaining why they matter for work.
8. Source line must separate: `Solar Arc calculation`, `Transit/Progressed Moon trigger`, and `Database-backed interpretation`.

### D. PAC timing/themes

Also read `references/pick-a-card-timing.md` and `fortune-hub/references/pac-style-boom.md`.

Default output for PAC requests:
- Rank 3–5 topic ideas.
- Tie each idea to current Moon/Mercury/Venus/Neptune/Saturn conditions.
- Pick one strongest topic and provide caption/hook.
- BooM's PAC style: 4–5 piles, long paragraphs, playful/sassy, love themes often perform well.

### D. Horary source discipline

Horary is its own question-answer system, but when BooM asks for Horary, apply the same **integrated-astrology workflow discipline** to the Horary reading:

1. Load `horary-astrology` for the actual Horary method.
2. Cast the horary chart for the moment Turboz fully understands the question, using BooM's current location unless she specifies another location.
3. Use the Horary workflow from `horary-astrology`: radicality, significators, Moon, applying/separating aspects, dignity, VOC, timing.
4. Include Vedic/Jyotish support inside Horary when relevant: KP Horary / Tajik / Prashna techniques from `horary-astrology`.
5. Apply this skill's source rules to the interpretation: open ASTROLOGY-BOOKS-DATABASE first; if missing a relevant source, use `multi-search-engine` fallback and cite it.
6. Output should be a Horary reading, not a transit reading. Transit/Uranian background is optional only if BooM asks for extra context.

Preferred output shape:

```markdown
