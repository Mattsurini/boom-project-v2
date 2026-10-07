# ADR 0001: aspect_verify.py uses Astro-Seek's orb rule, not the Boom engine

- Status: accepted
- Date: 2026-09-10

## Context

`scripts/aspect_verify.py` verifies a reference aspect list (pasted from
Astro-Seek) against freshly computed planet positions and confirms the set is
complete (two-way). The reference lists the user pastes come from Astro-Seek's
major-aspect default, so the tool's completeness scan must reproduce *that*
source's orb rule — otherwise a correct reference list would produce false
extras/misses.

The project already has an orb engine (`stellium/src/stellium/engines/orbs.py`,
`MoietyOrbEngine(system="boom")`). Using it would be circular: the verifier
would depend on the very engine under test, and its Boom orbs (Sun 10 / Moon 11 /
Mer 7 / Ven 6 / Mar 7 / Jup 8 / Sat 5 / Ura 5 / Nep 7 / Plu 5, effective
(A+B)/2) do not match Astro-Seek's, so a valid Astro-Seek list would FAIL.

## Decision

The tool computes positions directly (xalen → swisseph, same as
`transit_timeline_check.py`) and scans aspects with **Astro-Seek's default
orb rule**, encoded as `seek_orb()`:

- Conjunction 0°, Square 90°, Trine 120°, Opposition 180°: **7°**, **10°** if a
  luminary (Sun/Moon) is involved.
- Sextile 60°: **4°**, **5°30′** if a luminary is involved.
- Minor 30/45/72/135/144/150°: **2°30′** fixed (only when `--minor` or the
  reference contains a minor aspect).

This rule was verified to reproduce the 2015-11-19 18:18 ICT Chiang Rai
reference exactly: 12/12, 0 missing, 0 extra — and independently confirmed on
2015-11-20 18:18 ICT Chiang Rai: 14/14, 0 missing, 0 extra (a second,
independent date). Orb deltas vs the source are ≤ ~0.016° (the source rounds
to 1′ plus a small ephemeris-position difference), so `--tol 0.02` is the
practical default for Astro-Seek references.

## Consequences

- A correct Astro-Seek reference yields a clean two-way PASS (collection) and
  orb deltas ≤ ~0.016° (the source rounds to 1′; use `--tol 0.02` for green).
- The tool is standalone: it does not import the Boom engine and does not log
  to `verification_evidence.db`.
- If a future reference source is not Astro-Seek, the scan rule must be
  re-derived (or a `--system` flag added); the current rule is Astro-Seek-specific.
