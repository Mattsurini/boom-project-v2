---
title: "Pitfalls And Db"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "pitfalls-and-db"
tags: [skill-reference, integrated-astrology]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/integrated-astrology/SKILL.md"
summary: "Use Python with native Windows paths. The MSYS `/c/...` path can be misleading depending on the tool context."
---

# Pitfalls And Db

_Moved verbatim out of SKILL.md so the trigger body stays small._

## Database Workflow

### Reliable access pattern on this Windows host

Use Python with native Windows paths. The MSYS `/c/...` path can be misleading depending on the tool context.

```python
from pathlib import Path
from pypdf import PdfReader

DB = Path(r"C:\Users\Fourt\ASTROLOGY-BOOKS-DATABASE")
assert DB.exists(), DB
```

### Best references

| Use case | Database file |
|---|---|
| Quick planet-in-house interpretation | `#Articles/Western Astrology - Planets in Signs and Houses.pdf` |
| Transit method / Bhava rules / retrograde force | `#Articles/new-techniques-of-prediction.pdf` |
| Library overview | `references/astrology-books-database.md` |
| Extracted Gochara notes | `references/gochara-transit.md` |

### Extraction recipe

```python
from pathlib import Path
from pypdf import PdfReader

path = Path(r"C:\Users\Fourt\ASTROLOGY-BOOKS-DATABASE\#Articles\Western Astrology - Planets in Signs and Houses.pdf")
r = PdfReader(str(path))
text = "\n".join((p.extract_text() or "") for p in r.pages)
for q in ["Mercury in the Tenth House", "Saturn in the Seventh House"]:
    idx = text.lower().find(q.lower())
    if idx >= 0:
        print(q)
        print(" ".join(text[max(0, idx-120):idx+650].split()))
```

### Minimum citation standard

In the answer, include a compact source section:

```markdown
## Common Pitfalls

1. **Skipping the database.** This is the main unacceptable failure. If no database extraction happened, say so before any reading.
2. **Saying “checked” when only calculation was done.** Calculation ≠ interpretation-source verification.
3. **Using `/c/...` path as proof the database is missing.** On this Windows/MSYS setup, use native `C:\Users\Fourt\...` inside Python for reliable access.
4. **Wrong Stellium API.** Use `Native(dt, (lat, lon))` then `ChartBuilder.from_native(native)`.
5. **Wrong timezone.** Convert ICT to UTC before `swe.julday()`.
6. **Wrong house indexing.** Normalize cusps length before assigning houses.
7. **Solar Arc date labels must be timezone-converted.** Swiss/SA calculations often output UTC dates; convert exact hits to BooM's timezone (Asia/Bangkok/ICT) before naming the date. Example correction: `SA Mars □ Natal ASC` for BooM is `2026-10-31 23:59 UTC` = `2026-11-01 06:59 ICT`; do not label it as 31 Oct in the user-facing answer.
8. **Only checking Moon.** BooM expects all transit-to-natal aspects and Uranian TNs.
8. **Mixing local chart and natal overlay.** Label them separately.
9. **Quoting Astro-Seek `DESCRIPTION`.** Use `.ics SUMMARY` only.
10. **Over-specific exact times for slow planets.** For Uranus/Neptune/Pluto/Saturn monthly effects, report peak date/orb/window, not fake exact minute precision unless root-solved.

