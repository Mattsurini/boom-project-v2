---
date: '2026-07-27'
tags:
- project
source: hermes-astro-hub/skills/horary-astrology/references/source-discipline-boom.md
---

# Horary Source Discipline for BooM

Use this whenever BooM asks a Horary question or challenges whether a Horary prediction was sourced.

## Layer separation

| Layer | Skill/source | Use |
|---|---|---|
| Calculation | `hermes_astro` (pyswisseph) | Horary chart, houses, ASC, Moon, planets, aspects, VOC |
| Horary method | `horary-astrology` | Radicality, significators, Moon, applying/separating, dignity, timing, Multiple Query System |
| Interpretation | `ASTROLOGY-BOOKS-DATABASE` | Meanings and rules from horary/prashna/KP texts, planets/houses/aspects |
| Fallback | `research` | Specific situation not covered by DB; cite as fallback |

## Required Horary order

1. Determine whether the user wants Horary or Transit. If BooM says **Transit**, do not cast Horary.
2. Cast the Horary chart at the time the question is understood and BooM's current location.
3. Run calculation checks: radicality, Moon VOC, Saturn 1st/7th, significators, applying/separating aspects, dignity/timing.
4. Open `ASTROLOGY-BOOKS-DATABASE` before interpreting.
5. Search DB for the relevant rule/topic:
   - `prashna-tantra.pdf` for houses, Prashna rules, success/failure, charity/religion/pilgrimage, gains
   - `Predicting with KP Horary...pdf` for KP sublord questions when needed
   - `Horary Astrology the 6th Reader 3.doc` for Western horary rules when readable
   - `Western Astrology - Planets in Signs and Houses.pdf` for planet-in-house meanings when horary/prashna source is insufficient
6. If DB lacks a specific situation, load/use `research` and label it as fallback.
7. Answer with four visible sections:
   - `[Calculation]`
   - `[Database-backed]`
   - `[Multi-search fallback]` if used, or `not used`
   - `[Interpretation]`

## Pitfall from 27 Jul 2026

Do not answer Horary from calculation alone. A chart output (ASC, Moon, significators, aspects) is only the calculation layer. The prediction must be supported by DB/fallback, otherwise it must be labeled incomplete/non-database-backed.

### Database path/tool-resolution trap

If `search_files` or a POSIX/MSYS path check reports `ASTROLOGY-BOOKS-DATABASE` missing, do **not** conclude the database is unavailable yet. On BooM's Windows host, path resolution can differ between MSYS-style `/c/Users/...` and native Windows `C:\Users\Turbo\...` paths.

Before telling BooM the database cannot be used, retry with a Windows-native Python check:

```bash
"C:/Users/Turbo/AppData/Local/hermes/hermes-agent/venv/Scripts/python" - <<'PY'
from pathlib import Path
root = Path(r'E:\Boom Project\Knowledge\Astrology-Database')
print(root.exists(), root.is_dir())
for f in root.rglob('*'):
    if f.is_file() and any(t in f.name.lower() for t in ['horary', 'prashna', 'kp']):
        print(f)
PY
```

Only label DB as inaccessible after both normal search and native-path verification fail. If the retry finds the DB, continue with DB-backed extraction instead of stopping at calculation-only.

## Money/bills Horary note

For questions like “will I have enough money to pay X bill?” use:
- H2 / Lord 2 = querent's money and ability to pay.
- H12 / Lord 12 = expenditure, bills, money going out.
- H11 = gains/help/fulfillment of hopes.
- Check Moon and Lord 2 contacts for near-term liquidity; label any bill-specific web source as `research` fallback if used.

## Fallback handling

If `research` is loaded/attempted but blocked or returns no usable source, state “attempted but not used” and do not cite it as support. Continue only if Database supports the core rules.

## Minimal Horary source line

```text
Calculation: horary-astrology + hermes_astro (pyswisseph)
Database-backed: <database files used>
Multi-search fallback: <sources, “not used because DB covered it”, or “attempted but not used”>
```
