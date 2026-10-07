# FRONTMATTER_SCHEMA — Boom Project

Purpose: make project notes routeable without loading whole files, reducing tokens for Hermes work.

## Minimal schema for new Markdown artifacts

```yaml
---
title: "Short human title"
date: "YYYY-MM-DD"
type: "blueprint | technical-extraction | psychological-extraction | audit | critique | convergence-report | insight | source-package | note"
stage: "Plawan | Nut | CK | Arm | Nan | Bella | Knowledge | Source"
topic: "short-slug"
tags: [astrology, transit, methodology]
source_classes: [database-backed, external-web-material, calculation-backed, synthesis]
status: "draft | verified | clean-with-boundaries | final"
related:
  - "relative/path/to/source-or-previous-stage.md"
summary: "1-2 lines: why this file exists and when to read it"
---
```

## Token-economy rules

1. New research/pipeline artifacts should include frontmatter.
2. Do **not** mass-edit old OCR/database files just to add metadata; use `project_manifest.json` for routing.
3. Before reading raw files, inspect:
   - `Knowledge/indexes/PROJECT_INDEX.md`
   - `Knowledge/indexes/project_manifest.json`
   - topic-specific existing indexes under `Knowledge/indexes/`
4. For BooM research answers, external web sources are substantive material for insight/reference, not citation decoration.
5. Large raw source excerpts go to `Output/source-excerpts/`; final reports cite the path and summarize.

## Recommended source class labels

- `database-backed` — local DB/classic/article/source file
- `external-web-material` — fetched web source used to generate insight/reference
- `calculation-backed` — computed chart/timing/market/stat result
- `synthesis` — Turboz interpretation from evidence
- `blocked` — source attempted but inaccessible, with reason
