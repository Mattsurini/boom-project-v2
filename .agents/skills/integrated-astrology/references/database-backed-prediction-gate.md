---
date: '2026-08-01'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/database-backed-prediction-gate.md
---

# Database-Backed Prediction Gate

Session-learned rule for BooM's astrology work.

## Core distinction

Calculation is not interpretation.

| Layer | Counts as done when |
|---|---|
| Calculation | pyswisseph/Stellium computed planets, houses, aspects, Uranian TN points |
| Database-backed interpretation | Relevant passages were opened/extracted from `C:\Users\Fourt\ASTROLOGY-BOOKS-DATABASE` and used in the reading |
| Complete prediction | Both layers are complete and the final answer includes the source line |

## Required behavior

1. Calculate the chart/transits/aspects with pyswisseph/Stellium.
2. Open `C:\Users\Fourt\ASTROLOGY-BOOKS-DATABASE\` using a native Windows path from Python.
3. Extract or summarize relevant passages from the database before interpreting.
4. If the database lacks a relevant passage, broaden database search first, then use `multi-search-engine` fallback research.
5. In the answer, state both layers:
   - `Calculation: pyswisseph/Stellium`
   - `Interpretation: ASTROLOGY-BOOKS-DATABASE-backed`
6. If fallback research was needed, label it:
   - `Database fallback research: <sources actually used>`
7. If the database cannot be accessed, stop before prediction and state the blocker. Only provide a clearly labeled non-database draft if BooM explicitly accepts.

## Reliable database access on this Windows host

Prefer Python native Windows paths over MSYS `/c/...` paths when verifying database existence or reading PDFs:

```python
from pathlib import Path
from pypdf import PdfReader

DB = Path(r"C:\Users\Fourt\ASTROLOGY-BOOKS-DATABASE")
assert DB.exists(), DB

path = DB / "#Articles" / "Western Astrology - Planets in Signs and Houses.pdf"
r = PdfReader(str(path))
text = "\n".join((p.extract_text() or "") for p in r.pages)
```

## If the database has no relevant passage

1. Broaden the search across the database by planet, house, aspect, and theme keywords.
2. If still missing, load/use `multi-search-engine` as fallback research.
3. Search multiple engines/sources where possible.
4. Label the cited material as `Database fallback research`.
5. Do not fill the missing meaning from memory alone.

## If the database is inaccessible

Hard stop. Say the blocker first and ask for the correct path. Only provide a non-database draft if BooM explicitly accepts that limitation.

## User correction encoded

When BooM asks “have you checked against the Database yet” she means: **was the interpretation/prediction checked against the database?** Do not answer only about ephemeris calculation.

## Minimum answer source lines

Database-backed:

```markdown
Calculation: pyswisseph/Stellium | Interpretation: ASTROLOGY-BOOKS-DATABASE-backed
```

Database plus fallback:

```markdown
Calculation: pyswisseph/Stellium | Interpretation: ASTROLOGY-BOOKS-DATABASE + Database fallback research-backed
```

Database inaccessible:

```markdown
Calculation: pyswisseph/Stellium | Interpretation: Not database-backed — database inaccessible
```

Do not present the last one as a complete prediction.
