---
name: tarot-reading
description: Draw and interpret a tarot spread with the deterministic engine (scripts/tarot_engine.py). Seeded draw, per-card interpretation, timing-aware readings for love, career and decisions.
date: '2026-08-01'
tags:
- tarot
- prediction
- workflow
- skill
source: hermes-astro-hub/skills/tarot-reading/SKILL.md
---

# Tarot Reading Skill

## Purpose
Execute structured tarot readings via deterministic spread engine (`scripts/tarot_engine.py`).

## When to Use
- Querent asks a specific question (love, career, decision, general guidance)
- After astrology timing analysis (if timing-sensitive)
- Any session where a card spread is requested

## Workflow

```
Input (Question + Context)
    ↓
[1] Spread Selection — auto-detect or user-specify
    ↓
[2] Deterministic Draw — seed = hash(question + birth + timestamp)
    ↓
[3] Position + Card Interpretation — per card
    ↓
[4] Synthesis Layer — cross-reference astrology DB if birth data given
    ↓
[5] Formatted Output — structured markdown report
```

## Spread Types

| Spread | Cards | Best For | Auto-Trigger Keywords |
|--------|-------|----------|----------------------|
| `three_card` | 3 | General guidance | (default) |
| `relationship` | 5 | Love, partnership | relationship, love, soulmate, marriage |
| `career` | 5 | Work, finance, business | career, job, money, promotion |
| `yes_no` | 3 | Binary decisions | yes/no, should I, will I, can I |
| `celtic_cross` | 10 | Deep analysis | celtic, deep, full |

## Interpretation Rules

1. **Position first, card second** — the position sets the frame; the card fills it
2. **Reversed = internalized energy** — not always negative; often shows blocked or unconscious expression
3. **Suit patterns matter** — many Cups = emotional theme; many Swords = mental conflict; many Pentacles = material focus; many Wands = action/drive
4. **Major Arcana = archetypal forces** — life themes, destiny moments, significant shifts
5. **Court cards = people or roles** — Page (new energy), Knight (action), Queen (mastery), King (authority)

## Astrology Bridge (Optional)

If birth data is provided:
- Query astrology DB for current transits affecting 7th house (relationships), 10th (career), etc.
- Layer transit interpretation into card synthesis for grounded, time-aware reading
- Use `scripts/astrology_db.py` for targeted retrieval (never load full books)

## Source Discipline

- Card meanings come from the embedded Rider-Waite-Smith reference in `scripts/tarot_engine.py`
- Astrology layering uses `scripts/astrology_db.py` against the converted book database
- Do not invent card meanings not in the reference deck

## Example Invocation

```bash
python scripts/tarot_engine.py \
  --question "Will I find a soulmate this year?" \
  --birth "1996-11-20 20:37" \
  --location "Chiang Rai"
```

## Output Format

Structured markdown with:
- Meta (question, spread, seed, timestamp)
- Per-card breakdown (position + card + orientation + meaning)
- Synthesis section (to be filled by interpretation layer)

## Reproducibility

Same `question + birth + seed` → same cards. Use `--seed` to fix a draw for re-interpretation or cross-check.
