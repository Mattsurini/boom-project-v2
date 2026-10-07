---
name: astrology-books-database
category: astrology
description: Use when querying the BooM Astrology Books Database.
---

# Astrology Books Database Access Protocol

## Overview
This skill governs the mandatory interpretation-source workflow for BooM astrology readings. Calculation (myhora/pyswisseph) and interpretation (Database) must be separated.

## Access Rules
1. **Always open the database first**. Do not attempt to interpret transit/natal configurations from memory.
2. **Use Native Windows Paths**. Use `E:/Boom Project/Knowledge/Astrology-Database/` (or relative path in project). Do not rely on MSYS-style `/e/...` paths in Python `Path()` objects.
3. **Extraction**: Use `pypdf` (or similar) to extract relevant passages for the specific aspect, house, or transit being analyzed.
4. **Fallback**: If the database is missing or lacks a passage for the configuration:
   - Load `multi-search-engine`.
   - Perform the search.
   - Cite the sources as `Database fallback research`.
   - Never present a reading as 'Database-backed' if it is actually just fallback research.

## Common Database Sources
- `Western Astrology - Planets in Signs and Houses.pdf` (General planet/house meanings)
- `new-techniques-of-prediction.pdf` (Gochara transit rules, retrograde force)
- `references/astrology-books-database.md` (Library index)

## Pitfalls
- **Missing Module**: Ensure `pypdf` is installed in the current venv (`pip install pypdf`).
- **Path errors**: Use `pathlib.Path(r'E:/...')` to avoid escaping issues in Windows path strings.
- **Over-citing**: Summarize the findings in English; do not dump long raw text unless BooM asks.
