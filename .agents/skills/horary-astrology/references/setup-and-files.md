---
title: "Setup And Files"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "setup-and-files"
tags: [skill-reference, horary-astrology]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/horary-astrology/SKILL.md"
summary: "All scripts use the **shared calculation layer** (`hermes_astro` package — vendored at `E:\Boom Project\hermes-astro-hub\` and installed editable into"
---

# Setup And Files

_Moved verbatim out of SKILL.md so the trigger body stays small._

## Prerequisites

All scripts use the **shared calculation layer** (`hermes_astro` package — vendored at `E:\Boom Project\hermes-astro-hub\` and installed editable into the project venv) which provides:
- **xalen.swe** (XALEN ephemeris) — **primary** ephemeris engine; **swisseph** (genuine Swiss Ephemeris 2.10.03, installed via the `pyswisseph` pip package, imported as `swisseph`) is the automatic **fallback** if xalen is missing. Both expose the same Swiss API and agree to <2″ for the Traditional 7 (Rahu ~9″ is the worst case, where swisseph is the reference).
- flatlib personal orbs (Moon 12°, Sun 15°, Saturn 9°, Jupiter 9°, Mars 8°, Mercury 7°, Venus 7°) — **VOC's documented basis.** `hermes_astro` (v1.1.0+) defaults to the Boom moiety table, so `voc_time.py` calls `set_orb_system('flatlib')` to preserve VOC behaviour. The chart scripts (`horary_chart.py`, `horary_2nd_q.py`) use the default `boom` system and print the active system in their footer.
- Orb-system selection: `hermes_astro.set_orb_system('boom' | 'flatlib')`; `hermes_astro.orb_allowance(a, b)` returns the moiety mean of the two bodies' full orbs.
- flatlib `isVOC()` logic (cross-sign Traditional 7 aspects)
- Placidus houses

```bash
# The hermes_astro package is auto-available in the Hermes venv
from hermes_astro import *
```

No additional install needed. For scripts running outside the venv:
```bash
uv pip install xalen pyswisseph pypdf
```

**Confirm the live engine** before trusting a chart — `hermes_astro.verify_engine()` returns `{'engine', 'ok', 'detail'}` and sanity-checks the engine against a fixed golden position (Sun@J2000 ≈ 280.5°). Both pyswisseph and xalen pass it.

## Integrated Approach — Three Horary Systems

This skill combines **three complementary horary systems** from the ASTROLOGY-BOOKS-DATABASE (`E:\Boom Project\Knowledge\Astrology-Database\#Articles\`):

| System | Source | Strengths |
|--------|--------|-----------|
| **Western Traditional** (Lilly, Frawley) | Classical Western | Planetary dignities, radicality check, aspect-based Yes/No |
| **KP Horary** (Krishnamurthy Paddhati) | `Predicting with KP Horary.pdf` | Number-based, cusp sublord analysis, precise house mapping |
| **Tajik/Prashna** (Neelakanta) | `prashna-tantra.pdf`, `Essence_of_Prashna_Techniques.pdf` | Ithasala/Muthasila, Avasthas, sign types (Chara/Sthira/Dwisvabhava) |

**Flow:** Start with Western for radicality + aspect. If chart is ambiguous, add KP sub-lord analysis. If timing or quality is unclear, apply Tajik sign-type rules.

**⚠️ Multiple-Question Flow:** For the 2nd+ question from the same querent, the **reference point shifts** per the Multiple Query System (Prashna Tantra). See that section below. Do NOT answer a second question using the first chart's houses — you must rotate the chart so the Moon (Q2), Sun (Q3), etc. becomes the new ASC.

---

## Skill Reference Files

This skill includes local reference files beyond the book database:

| File | Content |
|------|---------|
| `references/7th-bhava-prashna-tantra.md` | 7th bhava interpretation from Prashna Tantra: form/attributes/features to declare from the sign in H7. Sign element gives physical appearance, planet in H7 tells partner type, Moon indicates age, sign type reveals fidelity. |
| `references/weather-rain-horary.md` | Rain/weather interpretation rules, house assignments, signifiers, and a worked example (27 Jul 2026). Use for any "will it rain?" follow-up question. |
| `references/moon-voc-calculation.md` | Moon VOC definition, correct cross-sign calculation method, code snippets, and common mistakes. Read before every VOC determination — the in-sign-only trap is the most common error. |
| `references/source-discipline-boom.md` | Mandatory Horary source discipline for BooM: calculation vs Database-backed interpretation vs `research` fallback. Read before any Horary prediction. |
| `references/vedic-prashna-multiple-query-caveat.md` | Research note: Q2-from-Moon is a Vedic Prashna multiple-query rule; the current Placidus-rotation script is hybrid and must be labeled as such. |
| `references/session-examples.md` | Past session examples with pitfalls and lessons learned. |

