---
name: astro-knowledge-db
description: Use when querying Boom's classical astrology texts (Vedic/Western) for quotations, citations, or "[NOT IN DB]" checks during research.
---

# Astro Knowledge DB Skill

Query the Boom project's classical texts index (`Knowledge/Astrology-Database/`).

## Critical: two different scripts — pick by what you need

| Script | Has a CLI? | Use it for |
|---|---|---|
| `scripts/query_db.py` | YES — `python scripts/query_db.py "<query>"` | Real searches. Prints matched files + grepped excerpts. |
| `scripts/astrology_db.py` | **NO CLI** — importable functions only | Importing `search()` / `search_summary()` from Python. |

`astrology_db.py` has no `__main__` block and no `argparse`. **Do not** run it as
`astrology_db.py --planet Venus` or `--help` — that is not a real interface and it
produces nothing at all. Use `query_db.py` from the shell.

## Usage

```bash
cd "E:\Boom Project"
".venv\Scripts\python.exe" scripts/query_db.py "Jaimini Chara Dasha"
".venv\Scripts\python.exe" scripts/query_db.py "Venus dignity"
".venv\Scripts\python.exe" scripts/query_db.py "BPHS Upapada Darapada"
```

Output: query line, parsed phrase/terms, matched file titles with sizes, then up
to 10 grepped excerpts per file (~2000 chars/file, 15000 total) with matches
bolded.

From Python:

```python
import sys; sys.path.insert(0, r"E:\Boom Project\scripts")
import astrology_db as a
excerpts = a.search("Chara Dasha", max_results=3)         # [{file,path,line,context}]
files    = a.search_summary("Chara Dasha", max_results=5)  # paths only, low token
```

## What the index actually covers — check before promising sources

Verified 2026-10-06 on this host:

- **Index:** `Knowledge/indexes/astrology_db_index.json`
- **Coverage: 197 Markdown files, all 197 resolve on disk (0 missing).**
- **The 185 PDFs in `Knowledge/Astrology-Database/` are NOT in the index** —
  `build_db_index.py` walks for `*.md` only (`build_db_index.py:119`). PDFs stay
  in place and are never content-read. If a source is PDF-only, flag `[NOT IN DB]`
  instead of implying you searched it.
- Topic mass is currently Jaimini / Chara Dasha / Karaka / Sthira Dasha / Nadi /
  BPHS / Parashara / classics. Retrieval is `topic_index` + substring line grep, so
  a file can match by topic and still print
  `(no exact keyword matches in file — file is relevant via index topic)`.

Treat that parenthetical as *relevant by title/topic*, not a confirmed passage:
open the file directly if you need an actual quote.

## Rebuilding the index

The index drifts from the filesystem (files get moved into topic folders). If
queries return stale paths, miss known files, or start matching nothing, rebuild:

```bash
cd "E:\Boom Project"
".venv\Scripts\python.exe" scripts/build_db_index.py
```

Last rebuilt 2026-10-06. Before that the index held 187 entries of which **182
pointed at files that no longer existed** — the primary searches were silently
dead.

## Pitfalls

- **Use `.venv\Scripts\python.exe`.** Boom `.venv` is Python 3.11 with `swisseph`,
  `pymupdf`, `xalen`; system/Hermes python is a different environment.
- **Query with real content words.** No stemming or fuzzy matching; `help` →
  `No files found in index.`
- **`search()` reads whole files** per match — fine at 23 MB total, wasteful in a
  loop. Use `search_summary()` for a cheap candidate list first.
- **Dedup is process-local.** Excerpt dedupe uses `hash()` of the context string,
  which is salted per process, so it only holds within one run.
- Windows: prefer the `cd "E:\Boom Project"` + relative-script form shown above.

## References

- `scripts/query_db.py` — the CLI (real interface)
- `scripts/astrology_db.py` — importable `search()` / `search_summary()`
- `scripts/build_db_index.py` — index builder (`*.md` only)
- `astro-pipeline` skill — where this is used in the research flow
