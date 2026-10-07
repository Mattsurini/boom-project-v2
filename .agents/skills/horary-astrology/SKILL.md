---
name: horary-astrology
description: Horary astrology — cast and interpret charts for specific questions.
version: 2.0.0
author: Turboz
tags: [horary, interrogatory, astrology, traditional, kp-horary, prashna, tajik, chart, question]
---

# Horary Astrology

Answer any specific question by casting a chart for the moment the question is asked and interpreting it using traditional horary rules (Lilly, Frawley, etc.).

## BooM Presets — Choose Before Reading

BooM prefers Horary readings separated into two explicit presets. Do **not** blend them silently.

| Preset | Use for | Calculation / house style | Interpretation style |
|--------|---------|---------------------------|----------------------|
| **Western Horary** | Yes/No questions, relationship return, jobs, lost items, concrete outcomes | **Tropical Whole Sign (default)**; Placidus opt-in via `--placidus` | Classical Western horary (Lilly/Frawley-style). Do **not** apply Prashna multiple-query Moon/Sun/Jupiter rotation unless explicitly switching presets. |
| **Vedic Prashna** | Multiple-query sequences, sign-based omen-style readings, character/description questions, Tajika/Prashna analysis | Prefer sign/Rāśi-based or Chandra-lagna style; use Prashna Tantra multiple-query reference points (Q1 ASC, Q2 Moon, Q3 Sun, Q4 Jupiter, Q5 Mercury/Venus). If using Placidus rotation scripts, label as **hybrid calculation**. | Prashna/Tajika rules: Ithasala, Muthasila, Avasthas, sign types, planetary indications. |

Response must start with the chosen preset line, e.g. `Preset: Western Horary (tropical, whole sign)` or `Preset: Vedic Prashna (Moon-reference, sign-based/hybrid)`.

## Non-Negotiable Gates

Before every reading, these gates must pass. If any gate fails, say so — do not proceed to prediction as if nothing happened.

### Gate 1 — Calculate correctly

| Rule | Why |
|------|-----|
| Use the **shared calculation layer** (`hermes_astro` → xalen primary, swisseph fallback) | Only supported engines on this host — do NOT hand-roll ephemeris calls |
| Convert ICT → UTC before `swe.julday()` | Wrong timezone shifts ASC by several signs |
| **Confirm querent's current location** (lat/lon) | ASC changes with latitude — Saturn can move from 1st to 12th between Bangkok vs Chiang Rai |
| **Q1 → ASC** (standard). **Q2+ → rotate reference** per Prashna Tantra | Wrong houses = wrong answer |

### Gate 2 — Radicality before reading

| Check | Pass ✅ | Fail ⚠️ |
|-------|:------:|:--------:|
| ASC 3°-27° | Radical | Early (<3°) = premature; Late (>27°) = matter passed |
| Moon not VOC | Can proceed | "Nothing will come of it" — but still check next sign boundary |
| Saturn not in 1st/7th | Clear | Querent hindered / matter delayed |

If radicality fails, still interpret but **state the caveat explicitly** in the answer.

### Gate 3 — Database before prediction

**Mandatory two-layer workflow — do not skip:**

**Calculation layer:**
- Use `hermes_astro` (xalen primary, swisseph fallback) for horary chart, houses, significators, aspects, and VOC.
- Use `horary-astrology` for Horary method: radicality, significators, Moon, applying/separating aspects, dignity, timing, Multiple Query System.

**Interpretation layer:**
1. Open `ASTROLOGY-BOOKS-DATABASE` first.
2. Use Database meanings for horary rules, planets/houses/aspects, and the relevant question type.
3. If a file/path search says the DB is missing, retry with the native Windows path check in `references/source-discipline-boom.md` before declaring the DB inaccessible. Do not stop after one failed `search_files`/MSYS-path attempt.
4. If the Database has no passage for the specific situation, load/use the **`research`** skill as fallback research.
5. In the answer, label clearly what is **Database-backed** vs **multi-search fallback**.

**Hard stop:** Before writing any prediction/forecast, extract relevant interpretations from:

```
E:\Boom Project\Knowledge\Astrology-Database\
```

If the database is missing or unreadable:

> ⛔ This prediction cannot be completed fully because Turboz cannot access `ASTROLOGY-BOOKS-DATABASE` right now.

If the database has no relevant passage for a specific configuration, load `research` for fallback research and cite the actual source used.

### Gate 4 — Source line in answer

Every horary answer must close with a source line:

```
Calculation: xalen (Swiss-API ephemeris) / Horary | Interpretation: ASTROLOGY-BOOKS-DATABASE-backed
```

If not database-backed, say so plainly and do not pretend.

---

## Step-by-Step Workflow

**Mode guard:** Before casting, confirm the task is actually Horary. If BooM says **"Transit"**, "look at Transit", "today's energy", or asks electional timing like "what time is good to upload a clip", route to `integrated-astrology` instead. Do **not** answer Transit questions with Horary just because the wording sounds like a yes/no question.

Follow this order for every horary question.

### Step 0 — Confirm details

- [ ] Ask the querent's **current location** (lat/lon) — do NOT default to Bangkok
- [ ] Determine the **exact time** the question was fully understood
- [ ] Identify which question number this is (Q1 / Q2 / Q3 / Q4 / Q5?)

### Step 1 — Cast the chart

- Use location + time from Step 0
- **Quick chart pull (any engine, one command):** `python E:\\Boom Project\\scripts\\chart_pull.py DD.MM.YYYY HH:MM <city> [--aspects] [--json]` — prints the live engine (`xalen` primary / `swisseph` fallback) with a golden-position sanity check, Placidus cusps + ASC/MC, Traditional 7 with speed + dignity, and (with `--aspects`) the speed-based VOC aspect set. City names follow the `aspect_verify.py` convention (`chiang-rai`, `bangkok`, …) or `--lat/--lon/--tz`.
- **Q1** → standard Placidus houses via `horary_chart.py`
- **Q2** → rotate so Moon = ASC via `horary_2nd_q.py`
- **Q3** → rotate so Sun = ASC
- **Q4** → rotate so Jupiter = ASC
- **Q5** → Mercury or Venus (whichever stronger)
- **Verify:** after rotation, the reference planet should be in House 1

### Step 2 — Check Radicality (Gate 2)

- ASC degree within 3°-27°?
- Moon VOC? If yes, check what happens at the next sign boundary
- Saturn in 1st or 7th?
- Log all warnings before proceeding

### Step 3 — Identify Significators

- **Querent** = ruler of 1st house (ASC sign)
- **Quesited** = ruler of the house matching the question topic
  - Use the Common Question Dictionary for mapping
  - **Always look up the actual cusp sign** of the quesited house, then get its ruler — never use the house number as a sign index
- Note each significator's position, house number, essential dignity, and avastha

### Step 4 — Evaluate Aspect

- Check aspect between Querent and Quesited significators
- Determine **applying** (matter active) vs **separating** (matter past)
- Also check Moon's aspect to either significator
- If no direct aspect, check **Translation of Light** or **Collection of Light**
- (Tajik) If Ithasala is present but the planet is combust → negated

### Step 5 — Check Dignities + Avasthas

- Essential dignity of each significator (Rulership +5, Exaltation +4, Fall -4, Detriment -5)
- Avastha of each significator (Deeptha = strong, Deena = weak, etc.)
- **Strong significator** can deliver even with a weak aspect
- **Weak significator** struggles even with a good aspect

### Step 6 — Apply Timing

- Degrees remaining between applying planets ÷ faster planet's speed
- Planet speed reference:
  - Moon ~13°/day → days
  - Mercury ~1-2°/day → days-weeks
  - Sun ~1°/day → weeks
  - Venus ~1°/day → weeks-months
  - Mars ~0.5°/day → months
  - Jupiter ~0.08°/day → months-years
  - Saturn ~0.03°/day → years
- Moon's next sign change (~46h) often shifts the answer window

### Step 7 — Database + Source

- Open `ASTROLOGY-BOOKS-DATABASE` and extract relevant interpretations
- If a configuration has no matching entry, use `research` fallback and cite it
- Prepare the source line (Gate 4)

### Step 8 — Deliver Verdict

Format:
1. Radicality summary
2. Significators + their positions
3. Aspect + verdict (Yes/No/Qualified)
4. Timing estimate (if applicable)
5. Source line

---

## Verification Checklist

Before delivering any horary answer:

- [ ] **Querent's location confirmed** — not defaulted to Bangkok
- [ ] **Reference point correct** — Q1=ASC, Q2=Moon, Q3=Sun, Q4=Jupiter, Q5=Mercury/Venus
- [ ] **Rotation verified** — reference planet is in House 1 after rotation
- [ ] **Radicality checked** — ASC 3°-27°, Moon VOC?, Saturn position
- [ ] **Significators from actual cusp signs** — not house-number-as-index
- [ ] **Aspect evaluated** — applying/separating, orb, Translation/Collection checked
- [ ] **Dignities + Avasthas** considered
- [ ] **Moon path** checked — VOC duration, next sign, future aspects
- [ ] **Database extracted** — ASTROLOGY-BOOKS-DATABASE opened (or fallback cited)
- [ ] **Source line** included in answer
- [ ] **Multiple questions** — chart rotated correctly for Q2+

## Aspect Evaluation

The answer depends on the **aspect between the two significators**:

### Yes / No

| Aspect | Quality | Meaning |
|--------|---------|---------|
| ☌ **Conjunction** (orb ≤8°) | Strong Yes | The matter comes together |
| ⚹ **Sextile** (orb ≤6°) | Yes | Opportunity, easy flow |
| △ **Trine** (orb ≤8°) | Yes | Very favorable |
| □ **Square** (orb ≤7°) | No/Struggle | Obstacles, delays |
| ☍ **Opposition** (orb ≤8°) | No | Separation, division |
| No aspect | ? | The matter is uncertain |
| **Translation of Light** | Yes | Planet A aspects B, B aspects C = connection made |
| **Collection of Light** | Yes | Planet A+B both aspect a 3rd planet = unified |

### Applying vs Separating

- **Applying aspect** (within orb, getting closer) = matter is active
- **Separating aspect** (just passed exact) = matter is past/diminishing
- Moon applying to significator = timing is sooner

## Response Format

### Radicality
```
✅ Radical — ASC at 12° Leo (within 3-27°)
✅ Moon applying to Jupiter
⛔ Saturn in 7th house — matter may be delayed/denied
```

### Significators
```
You (querent): ☿ Mercury (ASC ruler, 1st house)
The job (quesited): ♄ Saturn (10th house ruler)
```

### Aspect
```
☿ Mercury △ Trine ♄ Saturn (orb 4°, applying)
→ Yes, favorable. The position suits you.
```

### Timing
```
Applying at 4°, Saturn moves ~0.03°/day → ~133 days ≈ 4-5 months
```

## Related Skills

- `hermes_astro` — Shared calculation layer (flatlib algorithm, xalen primary + swisseph fallback ephemeris, personal orbs, VOC)
- `integrated-astrology` — Combined Western + Uranian analysis (VOC reference: Section E)
- `xalen-ephemeris` — Western ephemeris positions
- `astro-natal-chart` — Natal chart calculation

## Scripts
`scripts/horary_chart.py` (cast the chart) · `scripts/horary_2nd_q.py` (2nd-question) · `scripts/voc_time.py` (Moon VOC timing). Usage detail: `references/scripts-and-usage.md`.

## Reference files — open only when its topic comes up
The body above suffices for a standard pass; opening this costs more than the old single file did.

- `horary_astrology-reference.md` — Deep reference sections moved verbatim out of horary-astrology/SKILL.m
- Moved sections: Radicality Check, Significator Identification
