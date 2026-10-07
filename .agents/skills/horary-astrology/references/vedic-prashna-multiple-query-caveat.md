---
date: '2026-08-01'
tags:
- project
source: hermes-astro-hub/skills/horary-astrology/references/vedic-prashna-multiple-query-caveat.md
---

# Vedic Prashna Multiple-Query Caveat

Session lesson from BooM asking whether a Q2 Moon-reference Horary reading is really valid.

## What is supported by source

`ASTROLOGY-BOOKS-DATABASE/#Articles/prashna-tantra.pdf` explicitly supports the multiple-query rule:

> “The first query is to be read from the ascendant, the second from the Moon, the third from the Sun, the fourth from Jupiter and the fifth from the stronger of the planets Mercury or Venus.”

Use this as **Vedic Prashna**, not Western horary.

## What must be labeled carefully

- **Pure Western Horary:** do not rotate Q2 to Moon. Cast/read from the ASC of the question time, then evaluate 1st/7th rulers, receptions, dignities, Moon applications, etc.
- **Vedic Prashna multiple-query mode:** Q2 may be read “from the Moon” per `prashna-tantra.pdf`.
- **Current script `horary_2nd_q.py`:** rotates Placidus cusps so the Moon degree becomes ASC. This is a practical **hybrid calculation**, not a textbook Western method and not guaranteed to be the exact classical Vedic house method.

## Required answer wording

When using Q2 Moon-reference, say:

> “This is the Vedic Prashna multiple-query rule / hybrid calculation, not pure Western Horary”

Do not say simply “Horary” if BooM asks which tradition was used.

## Practical recommendation

If BooM asks to “try researching it” or challenges the method:

1. Quote the `prashna-tantra.pdf` line above.
2. State that external web confirmation may be sparse; the local DB source is the authority used.
3. Offer two clean reruns:
   - pure Western Horary
   - pure/closer Vedic Prashna from Moon / Chandra-lagna logic
