---
agent: Nut
date: '2026-08-09'
tags:
- astrology
- psychology
- relationships
- financial-astrology
- methodology
- convergence
- technical
- date:2026-08-09
---

# Nut Technical Extraction — หลักการอ่านดวง Transit

## Summary
Transit reading ที่แข็งแรงต้องเป็น **layered judgment** ไม่ใช่ “ดาว X อยู่ราศี Y = เกิด Z” โดยตรง หลักแกนคือ:
1. ตรวจ natal promise/พื้นดวงก่อน
2. ตรวจว่าดาว transit กระทบเรือน/ดาว/มุมไหนของ natal
3. แยก local chart, transit event, natal overlay ออกจากกัน
4. ใช้ aspect/orb/exact hit เป็น timing trigger
5. ใช้ Moon/VOC/ดาวเร็วเป็นตัวล็อกวัน-ชั่วโมง; ดาวช้าเป็นฉากหลัง/season

## Database-backed Technical Evidence

## Fallback Web Research Correction
Original technical extraction used local DB only. After BooM challenged the pipeline, multi-search fallback was run to supplement the thin Western transit-method source layer.

- `Cafe Astrology — Transits in Astrology: Predictions` supports the technical rule that moving planets form relationships to natal planets/points, can be read through natal house placement, and “stimulate what is already there.” It also recommends reading slower outer-planet transits first for context, then refining with inner planets.
- `Wikipedia — Astrological transit` supports the broad definition of transits as a predictive astrology method, but is lower-grade because the page flags citation limitations.
- `Astro-Seek transit chart` was attempted but blocked by HTTP 403, so it is not used as evidence.

### 1) Bhava/house span matters for Gochara
- `new-techniques-of-prediction.md` lines 1697-1701: source warns that a planet may appear in one Bhava by rāśi chart but actually fall in an adjacent Bhava when Bhava span is scrutinized; “In Gochara reading this is of much significance.”
- Technical rule: do not read transit house from sign-only shortcut when house span is available. For BooM: local house positions must be kept separate from natal overlay.

### 2) Upachaya logic changes malefic transit meaning
- `new-techniques-of-prediction.md` lines 741-746: benefics/malefics in Gochara have specific favorable/unfavorable positions; malefics in 3/6/10/11 Upachaya can produce flourishing rather than only harm.
- Technical rule: malefic transit ≠ bad by default. Mars/Saturn in work-growth houses can mean pressure that builds output.

### 3) House categories create interpretive priority
- `new-techniques-of-prediction.md` lines 801-803: Kendras 1/4/7/10, Panaphara 2/5/8/11, Apoklima 3/6/9/12, Trikona 5/9, Dusthana 3/6/8/12, Upachaya 3/6/10/11.
- Technical rule: Transit to 10/11/6 is especially relevant for career/output/audience; 5/7/8/12 for love/PAC attachment themes.

### 4) Western house meanings are the interpretation map
- `Western Astrology - Planets in Signs and Houses.md` lines 253-255 starts “Planets in Houses”; line 255 defines 1st house as outward character traits.
- Technical rule: transit planet in a house describes the field of life being activated; the planet describes style/force; the aspect shows friction/support.

### 5) Progression/dasha can narrow event timing
- `new-techniques-of-prediction.md` lines 4944-4953: source notes difficulty timing slow planets and uses progressed Moon/Western secondary directions as a via media; annual readings may use solar birthday maps.
- Technical rule: slow transit alone gives window; exact event timing needs trigger layer: Moon, progressed Moon, dasha/bhukti, solar return/annual chart, or exact fast-planet contact.

## Technical Method: Transit Reading Hierarchy
1. **Question scope** — love/work/health/PAC/content. Choose relevant houses.
2. **Natal promise** — natal planet/house condition says what can manifest.
3. **Transit sky** — current planet sign/retrograde/speed/exact aspects.
4. **Natal overlay** — transit planet to natal houses/planets/angles; sort by orb.
5. **Local chart** — where current sky falls in the location chart; label as local, not natal.
6. **Vedic Gochara cross-check** — especially Moon/Lagna, Bhava span, Upachaya/Dusthana logic.
7. **Timing trigger** — exact aspect, Moon phase/VOC, fast planet hit, progressed Moon/dasha activation.
8. **Synthesis boundary** — calculation-backed facts first; prediction only after source-backed meanings.

## Do / Don’t
- DO say: “Saturn transit 10th = workload/standard/authority theme; if supported by natal MC/10th contacts, career restructuring.”
- DON’T say: “Saturn in 10th = job loss” without natal promise + aspect + timing + source.
- DO rank by orb and repetition.
- DON’T read every transit equally.
