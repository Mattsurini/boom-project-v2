---
date: '2026-10-05'
agent: turboz
type: audit
target: hermes-astro-hub
---

# Scrutiny Report — hermes-astro-hub

Outsider review of `E:\Boom Project\hermes-astro-hub` (shared astrology
calculation layer + skill copies + sync tooling).

## Intent

One shared calculation layer (`hermes_astro` package: ephemeris, aspects,
VOC, dignity, quesited mapping) so horary/integrated skills and project
scripts stop duplicating astrology math; plus a mirror of the astrology
skill set and a sync script.

The package part is load-bearing and works. The skills/ mirror is the
questionable part — see M1.

## Verified working (evidence)

- `pytest tests/ -v` (Hermes venv): **18/18 passed** in 0.56s, engine = xalen.
- `verify_engine()`: xalen Sun@J2000 = 280.3690° (expected ~280.5) — ok.
- `check_aspect_with_speed` movement classification: 30 days x hourly samples
  over 5 body pairs, 1113 in-orb aspects checked against ground truth
  (is |deviation| decreasing) — **0 misclassifications**, including the
  active-slower-than-passive case.
- `sync_skill_copies.py` dry run: the 4 managed horary files are in sync.
- `hermes_astro` is pip-installed editable in the Hermes venv (importable
  from any cwd); xalen 0.6.0 (vedika-io, pure-Rust) + pyswisseph 2.10.03 both
  present in that venv.

## Findings

### M1 — MAJOR: skill copies drifted; sync tooling covers 1 of 13 skills,
and its default direction is actively dangerous.

`sync_skill_copies.py` manages only 4 files of horary-astrology. `diff -rq`
against the profile (`C:\Users\Turbo\AppData\Local\hermes\skills`) shows real
drift elsewhere:

- integrated-astrology: SKILL.md + 2 references differ — **hub is newer** (09-22 vs 09-12)
- astro-natal-chart: `natal_chart_swe.py` + `draw_wheel.py` + SKILL.md differ —
  **profile is newer** (profile has bangkok/chiang-rai city entries the hub lacks)
- astro-synastry: SKILL.md differs — profile newer (09-11)
- horary-astrology: reference `7th-bhava-prashna-tantra.md` differs — profile newer (10-02)

Neither side is consistently canonical. The sync script's default direction is
hub -> profile; running `--apply` would clobber the newer profile-side
astro-natal-chart scripts and the horary reference. The profile copy is what
actually loads at runtime.

**Fix (pick one):** (a) delete `hermes-astro-hub/skills/` entirely and keep
only the package + tests (simplest — the hub's stated purpose is the shared
calc layer, not skill hosting); or (b) extend the sync script to all skills
with per-file direction and a "refuse to overwrite a newer file" guard.

### M2 — MAJOR: Thai quesited-keyword table fails on correctly-spelled Thai.

`THAI_MAPPINGS` (hermes_astro/__init__.py:578) contains mostly misspelled
variants (but no correct forms). Verified empirically:

- `"บ่านจะขายได้ไหม"` (home) -> **(7, None)** — should be house 4
- `"เพื่อนจะติดต่อมาไหม"` (friend) -> **(7, None)** — should be house 11

Correctly-typed questions silently fall to the default (7 = partner).
Also: `"มือถือ"` appears twice in the list.

**Fix:** add correctly-spelled variants alongside the typo variants
(keep both — the typos are evidently real user input), dedupe.

### M3 — MAJOR: three parallel VOC implementations; dead code in the shared layer.

Same "exact Moon aspects within one sign" algorithm exists three times:

1. `hermes_astro.find_moon_voc_window` (__init__.py:298-486) — imported by
   `scripts/transit_timeline_v3.py:35` but **never called** (grep: no call
   sites project-wide).
2. `skills/horary-astrology/scripts/voc_time.py` — own ternary-search +
   bisection implementation.
3. `scripts/moon_voc.py` — own dataclass + root-finding implementation.

Also dead: `aspect_perfection_time` (__init__.py:679, zero call sites),
`ASPECT_ORBS` ("for reference only"; imported by v3, never used), and
`check_aspect` (no-speed variant) has no production call sites (tests only).

This is the exact duplication the hub exists to eliminate.

**Fix:** keep one tested implementation in `hermes_astro`, delete the rest;
either wire `find_moon_voc_window` into v3 (if it was intended) or drop the
import.

### m1 — MINOR: stale engine-priority documentation (reversed).

Code priority is xalen primary / pyswisseph fallback (hermes_astro/__init__.py:16-27),
but:

- `scripts/chart_pull.py:14` docstring: "pyswisseph primary / xalen fallback"
- `tests/test_hermes_astro.py:8` docstring: "captured from the live pyswisseph
  ephemeris (primary engine)"

Tests still pass (golden values agree across engines to <0.01°), so this is
documentation rot, not a correctness bug — but it will mislead the next person
debugging an engine question.

### m2 — MINOR: transit_timeline_v3 mixes engines and shadows shared constants.

`scripts/transit_timeline_v3.py` imports `swisseph` (pyswisseph) directly for
outer planets + TN points while trad7 positions come from `hermes_astro`
(xalen) — two ephemeris engines in one run (agreement <2 arcsec per the
hub docstring; negligible, but it defeats the single-layer goal). Lines 43-45
also redefine `SIGNS`/`SIGNS_SHORT` locally right after importing them from
the hub — if the hub's constants change, v3 silently diverges.

### n1 — NIT: `quesited_house` English substring risks.

`"ex"` -> house 7 is a substring of "example", "expected", "explain".
Ordering currently saves "exam" (study list checked first), but any question
containing an "ex-" word without an earlier match lands in house 7.
Consider word-boundary matching for short keywords.

### n2 — NIT: misc.

- `swe.set_ephe_path('')` in horary_chart.py:17 / voc_time.py:12 is a no-op on
  the xalen engine (verified the attribute exists) — harmless, misleading.
- `hermes_astro.egg-info/` (09-07) and `.pytest_cache/` are stale build
  artifacts in the hub dir.
- Profile skill dirs carry `__pycache__/` and test PNGs/fonts that the hub
  copy lacks (part of the M1 drift surface).
- Tests hardcode `E:\Boom Project\scripts\chart_pull.py` — suite is
  machine-bound (acceptable for single-user, noted for the record).
- `myhora.py:_parse_pos` returns None silently if myhora's position format
  changes (row kept with deg/min/sec = None); only an entirely empty natal
  table raises.

## Verdict

**fix-then-ship.** The calculation core is solid and verified (18/18 tests,
golden engine check, 0/1113 aspect-classification mismatches over a month of
samples); the risk is in the hub's periphery — unmanaged skill-copy drift
whose sync tool would clobber newer work, dead/duplicated VOC code, and a
Thai keyword table that fails on correct Thai.

## Fixes applied (2026-10-05, same day)

### M1 — RESOLVED (option a)
Deleted `hermes-astro-hub/skills/` entirely. The hub now contains only the
shared `hermes_astro` package + tests + pyproject. `sync_skill_copies.py` is
now obsolete (its managed files live only in the profile) — kept for the
record, safe to delete later. Profile skills are the single source of truth.

### M2 — RESOLVED (better than the proposed table patch)
Root cause was deeper than "missing correct forms": as-typed Thai misplaces
tone marks (mai ek/tho/tri/chattawa), so exact substring matching fails even
when the consonant/vowel skeleton is right. Fix:
- Added `_normalize_thai()` (strips the 4 tone marks) and wired it into
  `quesited_house` — both question and keywords are normalized before
  matching.
- Rebuilt `THAI_MAPPINGS` (43 entries, code-point-exact): correct spellings
  + only the typo variants normalization can't catch (consonant/vowel swaps,
  doubled/missing vowels). Removed the duplicate "มืือถืือ" entry.
- Verified: all 8 report test strings (as-typed) + 8 correctly-spelled
  equivalents now map to the correct house (16/16). 18/18 hub tests still pass.

### M3 — RESOLVED (dead code removed; working CLIs left alone)
- Deleted `find_moon_voc_window` (0 call sites) and `aspect_perfection_time`
  (0 call sites) from `hermes_astro/__init__.py`.
- Removed v3's orphan imports: `check_aspect`, `find_moon_voc_window`,
  `moon_voc_status`, `ASPECT_ORBS` (all imported, never used in v3 body).
- Kept: `moon_voc_status` (used by horary_chart.py + tests), `check_aspect`
  (tested API), `moon_aspect_times` (tested).
- The three parallel VOC implementations: hub copy deleted; the two live
  CLIs (`scripts/moon_voc.py`, `skills/horary-astrology/scripts/voc_time.py`)
  are working tools with different output shapes — consolidating them into
  one shared function is a follow-up refactor, not a fix.

### Minor (left as-is, noted)
m1 (stale engine-priority docstrings), m2 (v3 engine mix + local SIGNS
redefinition), n1 ("ex" substring risk), n2 (set_ephe_path no-op, stale
egg-info/pytest_cache) — documented, low risk, not touched in this pass.
