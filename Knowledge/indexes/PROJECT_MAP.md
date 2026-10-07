---
title: "Boom Project — Fast File Router"
date: "2026-10-03"
type: "note"
stage: "Knowledge"
topic: "project-navigation"
tags: [project, navigation, token-economy]
status: "verified"
summary: "Single starting point for finding Boom Project files with minimal searches and context."
---

# Boom Project — Fast File Router

Use this page first. Do not browse folders broadly or load whole Knowledge/Output directories.

## One-command lookup

```bash
python scripts/libby/find.py --route <topic words>
```

Returns at most five Markdown matches. Open only the best 1–3 results. For more context, add `--limit 10` and omit `--route` only when necessary. Finder currently indexes Markdown, not Python/JS source files.

## Routes

| Need | Start here | Then |
|---|---|---|
| Find any knowledge or report | `python scripts/libby/find.py --route <topic>` | Use returned paths; inspect targeted sections only |
| Astrology source material | `Knowledge/indexes/PROJECT_INDEX.md` and `project_manifest.json` | `Knowledge/Astrology-Database/<system>/`; search exact technique/topic |
| Transit calculation | `scripts/transit_timeline_v3.py` | Check its `--help`; user preference is v3 for exact-minute output |
| Natal chart | `scripts/natal_chart.py` | `Prediction Astrology/` for BooM natal/transit material |
| Tarot | `scripts/tarot_engine.py` | `Tarot Knowledge/`; use finder for specific card/book material |
| Chinese almanac / BaZi / ZiWei | `Knowledge/Chinese-Astrology/` | Use finder for the specific calendar/date/system |
| PAC or transit content | `Output/PAC/` or `Output/Transit/` | Use finder for existing drafts and timing material |
| Pipeline reports | `Output/Plawan/`, `Nut/`, `CK/`, `Arm/`, `Nan/`, `Bella/` | Follow prior-stage links in frontmatter |
| Project scripts | `scripts/` | Search by filename; avoid searching the whole workspace |
| Hora7 research | `scripts/research/hora7/` | `artifacts/` = captured output; `assets/` = downloaded JS |
| Project rules / identity | `.hermes.md`, `SOUL.md`, `TURBOZ.md` | Consult `BOOM_PERSONAL_OPERATING_SYSTEM.md` when preference details matter |

## Canonical areas

- `Knowledge/` — reusable source knowledge and indexes; source of truth, not generated reports.
- `Output/` — generated drafts and agent deliverables. Use the canonical stage folders above; do not create stage aliases.
- `scripts/` — executable project tools, grouped by purpose; experiments stay in a topic subfolder.
- `Prediction Astrology/` and `Tarot Knowledge/` — domain-specific working collections.
- `.hermes/`, `cache/`, `runtime/`, `logs/`, `node_modules/`, `.venv/` — system state or dependencies; do not move as part of content cleanup.

## Folder inventory (authoritative — kept here, not in `.hermes.md`)

```
Knowledge/
├── Astrology-Database/     ← classical + modern sources
│   ├── Vedic-Classics/  Jaimini/  KP-Prashna/  Nadi/  Nadi jyotish/  Uranian/  Western/
│   ├── Financial/  Natal-Rectification/  Chart-Collections/  Birth-detail-collections/
│   ├── Articles/  #Articles/  Books by Authors/  Classics books/  Good books/
│   └── index.md  readme.md  jaimini_astrology.md  (loose source notes)
├── Astrology-Research/Datasets/
├── Chinese-Astrology/{BaZi,HuangLi,ZiWei,References}/
├── Convergence-Database/{Astrology Insights,ML-AI Insights}/
├── Psychology-Database/Applications/
├── Writing-Style/BooM/
├── _archive/duplicates/    ← verified duplicate archive
└── indexes/                ← PROJECT_MAP.md, PROJECT_INDEX.md, project_manifest.json

Output/
├── Plawan/  Nut/  CK/  Arm/  Nan/  Bella/  Sandee/  Ekae/   ← pipeline stages
├── PAC/  Transit/  Astrology/  Client-Readings/  Marketing/  Sources/
└── NotebookLM/
```

PDFs remain in place inside `Knowledge/` and are not content-read; index their paths instead.

## Low-token retrieval rules

1. Start with this route table or the one-command finder; never start with a recursive raw search.
2. Select one canonical file. Read its title/frontmatter and only the relevant section; expand to at most two supporting files if needed.
3. Prefer `project_manifest.json` for machine routing and `PROJECT_INDEX.md` for a human overview.
4. `project_index.py` indexes Markdown. For code, use a narrow filename search under `scripts/`, not broad project content search.
5. Add metadata to new/reused Markdown artifacts; do not mass-edit legacy OCR or source dumps just to improve indexing.
6. After adding/moving Markdown, run the Eng/Libby indexing workflow in `.hermes.md` so paths stay current.
