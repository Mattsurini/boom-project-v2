---
date: '2026-07-27'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/astrology-books-database.md
---

# ASTROLOGY-BOOKS-DATABASE — Reference Library

> Path: `C:\Users\Fourt\ASTROLOGY-BOOKS-DATABASE\`
> Source: https://github.com/ayushman1024/ASTROLOGY-BOOKS-DATABASE
> Size: ~2 GB | 1,465 files | Cloned 27 Jul 2026

**Usage rule:** Consult this repository BEFORE writing any prediction or transit interpretation. Search by keyword (planet name, house number, aspect type, transit configuration) to find authoritative interpretations from established astrology texts.

## Directory Structure

| Directory | Contents |
|-----------|----------|
| `#Articles/` | Astrology articles and papers |
| `Birth-detail-collections/` | Database of birth charts of famous people and events |
| `Books by Authors/` | Books organized by author name (BV Raman, KN Rao, Bhrigu, Jaimini) |
| `Classics books/` | Classical astrology texts (BPHS, Jataka Parijata, Saravali, etc.) |
| `Good books/` | Recommended reading (Vedic predictive techniques) |
| `Nadi jyotish/` | Nadi astrology texts (Tamil tradition) |

## Coverage

- **Traditions:** Vedic (Jyotish), Nadi, Cuspal Interlink Theory, Mundane Astrology, Esoteric Astrology, Western
- **Format:** Mostly PDF
- **Languages:** Primarily English, some Hindi/Tamil

## Quick Search Commands

```bash
# Search by keyword in PDF filenames
find /c/Users/Fourt/ASTROLOGY-BOOKS-DATABASE -iname "*saturn*" 2>/dev/null

# Search contents (PDFs only — limited by text layer)
# Best approach: use pypdf for targeted extraction
python3 -c "
from pypdf import PdfReader
import sys
path = r'C:\Users\Fourt\ASTROLOGY-BOOKS-DATABASE\#Articles\Western Astrology - Planets in Signs and Houses.pdf'
r = PdfReader(path)
kw = sys.argv[1] if len(sys.argv) > 1 else 'Venus'
for i in range(len(r.pages)):
    t = r.pages[i].extract_text()
    if kw.lower() in t.lower():
        print(f'--- Page {i+1} ---')
        print(t[:1500])
"
```

## Most Useful Books for Daily Transit Readings

### ⭐ #1: Western Astrology — Planets in Signs and Houses (32 pages)
**Path:** `#Articles/Western Astrology - Planets in Signs and Houses.pdf`
**Best for:** Quick daily transit interpretation. Every planet in every sign + every planet in every house (pages 1-32).
**Extraction:** `pypdf` works perfectly — full text layer.

### BV Raman — A Manual of Hindu Astrology (155 pages)
**Path:** `Books by Authors/BV Raman/A Manual of Hindu Astrology by BV Raman.pdf`
**Best for:** Classical Vedic interpretation, Gochara (transit) principles, planetary yogas.
**Note:** PDF may be scanned — check with pypdf first.

### KN Rao — Learn Successful Predictive Techniques (159 pages)
**Path:** `Books by Authors/KN rao/Learn Successful Predictive Techniques of Hindu Astrology.pdf`
**Best for:** Saturn-Jupiter double transit theory, practical predictive methods.
**Note:** PDF has readable text.

### Predictive Jyotish by M.N. Kedaar
**Path:** `Good books/Predictive Jyotish by m-n-kedaar.pdf`
**Best for:** Timing of events through transit + dasha combinations.

## Horary & Prashna Resources (discovered 27 Jul 2026)

| File | Tradition | Notebook Reference |
|------|-----------|-------------------|
| `#Articles/Predicting with KP Horary-20100324-193133.pdf` | KP Horary (9p, text) | KP golden rules, cusp sublord, house-mapping table |
| `#Articles/prashna-tantra.pdf` | Vedic Prashna (Neelakanta, 38p) | Ithasala/Muthasila, Avasthas, house-by-house questions |
| `#Articles/Essence_of_Prashna_Techniques.pdf` | Vedic Prashna (10p) | Daivagya Vallabha vs Tajik comparison, Deeptamsha orbs |
| `#Articles/Horary Astrology the 6th Reader 3.doc` | Western Horary (151K) | 6th house / reading techniques |
| `#Articles/prashna-FINDING LOST ARTICLES USING HORARY ASTROLOGY.doc` | Lost objects (76K) | Finding lost items via prashna |
| `#Articles/asthamangal prashnam.pdf` | Kerala Prashna (9p) | Ashtamangala Deva Prasna — temple divination |
| `Books by Authors/Bhrigu/Bhrigu Prashna Nadi - R.G. Rao.pdf` | Bhrigu Nadi (165p) | Nadi-style prashna, scanned |

**Search shortcut:** `find /c/Users/Fourt/ASTROLOGY-BOOKS-DATABASE -iname "*horary*" -o -iname "*prashna*" 2>/dev/null`

These are integrated into the `horary-astrology` skill (v2.0.0+) as three systems: Western traditional, KP Horary, and Tajik/Prashna.

## Priority Topics (by BooM's interests)

- **Relationship/Synastry:** Venus, 7th house, composite charts
- **Transit interpretation:** Outer planet transits (Saturn, Uranus, Neptune, Pluto)
- **Pick A Card / Content timing:** Moon sign, VOC, Mercury retrograde
- **Lenormand:** Traditional meanings
- **Fortune prediction:** Thai-style reading structure

## Key Interpretations Extracted (from Western Astrology book)

### Venus in 1st House
> "Venus in the First House gives personal charm, tends to make the appearance pleasing, gives physical beauty."

### Mars in 10th House
> "Mars in the Tenth House — you could be in any profession as long as you are able to have non-stop activity. Any supervisor will tend to be on the aggressive side."

### Uranus in 10th House
> "Uranus in the Tenth House — forget working your way up the corporate ladder. If it's new, unusual, on the cutting edge, and even shocking — that's the profession for you."

### Sun in 12th House
> "Sun in the Twelfth House — people with this placement are frequently in the process of getting their act together, hiding your light under a bushel."

### Jupiter in 12th House
> "Jupiter in the Twelfth House — can hide their joviality, their cheerfulness. However, while it can limit luck as far as getting things for you, it can also protect you from physical harm, especially from enemies."

### Neptune Action
> "Neptune dissolves boundaries wherever it goes."

### Saturn in 9th House
> "Saturn in the Ninth House — learns best by actually doing, rather than from books. Long journeys tend to be for business, not pleasure."
