# Index-drift drill (Boom Project)

Project indexes under `Knowledge/indexes/` are snapshots. Files get moved into
topic folders, archives get renamed, and nothing rebuilds them automatically. The
consuming scripts usually swallow the resulting errors, so a fully stale index
looks like "no results" rather than "broken index".

## The check

1. Read the index JSON, collect every `files[].path`.
2. Resolve each against its base directory and count how many are missing on disk.
   Use forward-slash or `os.sep`-joined absolute paths — `os.path.join('E:', ...)`
   yields a *drive-relative* path and silently reports everything as missing.
3. Non-zero missing → rebuild with the script that generated the index, then re-run
   the same verification and one real query.

## Known instances

| Index | Builder | Notes |
|---|---|---|
| `Knowledge/indexes/astrology_db_index.json` | `scripts/build_db_index.py` | Walks `*.md` only — the ~185 PDFs under `Knowledge/Astrology-Database/` are intentionally not indexed and must be flagged `[NOT IN DB]`. Rebuilt 2026-10-06: 187 entries → 197, all resolving. |
| `Knowledge/indexes/project_manifest.json` | `scripts/project_index.py` | Rebuilt by the Eng/Libby workflow after Markdown artifacts are created. |

## Why consumers hide it

`scripts/astrology_db.py` and `scripts/query_db.py` wrap file reads in
`try/except → continue`, and `query_db.py` prints
`(no exact keyword matches in file — file is relevant via index topic)` when an
index hit has no grep match. That message means *matched by topic*, not
*confirmed passage* — never cite it as a quotation.

## Script-tooling precedents

When auditing a Boom skill, run its scripts — a documented interface that no longer
exists is the most common defect class:

- `scripts/astrology_db.py` is a **library** (no `__main__`, no argparse). The CLI is
  `scripts/query_db.py "<query>"`. Running the library with flags prints nothing at all.
- Run astro skill scripts with `E:\Boom Project\.venv\Scripts\python.exe` (3.11,
  pyswisseph 2.10.03). `hermes_astro` is editable-installed in the **Hermes** venv
  and is NOT importable from `.venv`.
- `astro-synastry/scripts/synastry.py` takes 6 positional birth args, not JSON flags.
- NotebookLM stage: `notebooklm.exe metadata` returning `Not logged in` is a
  blocker for the query stage only — ideate/bridge/analyze still run.
