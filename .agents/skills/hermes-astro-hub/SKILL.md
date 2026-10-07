---
name: hermes-astro-hub
description: Use when editing the hermes_astro hub or its horary consumers.
---

# hermes_astro Hub

Shared calculation layer for the Hermes astrology skills. Single source of truth
for ephemeris access, positions, houses, aspects, VOC, dignity, and aspect timing.

**Canonical source:** `E:\Boom Project\hermes-astro-hub\hermes_astro\__init__.py`
**Only interpreter that can run it:** `%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\python.exe`
(Boom `.venv` and `xalen-venv` both lack `hermes_astro` — see pitfalls.)

## Engine resolution

Import order: `xalen.swe` → `swisseph` (pyswisseph) → ImportError. Both engines
expose the same Swiss API and agree to <2″ on the Traditional 7 (Rahu ~9″, where
pyswisseph is the reference). `verify_engine()` returns the live engine plus a
J2000 Sun sanity check.

`xalen 0.6.0` in the Hermes venv DOES provide `xalen.swe`. Older notes calling
the Hermes-venv xalen an "unrelated 0.2.0 SDK" are stale — verify with
`from xalen import swe` before repeating that claim.

## Orb systems (v1.1.0+)

Two selectable tables. Effective orb for an aspect is the **mean** of the two
bodies' full orbs — the traditional moiety (half-orb) formula.

| System | Contents | Use |
|---|---|---|
| `boom` (**default**) | Sun 10, Moon 11, Mercury 7, Venus 6, Mars 7, Jupiter 8, Saturn 5, Uranus 5, Neptune 7, Pluto 5 | Transits, charts, anything matching the verified GT |
| `flatlib` | Sun 15, Moon 12, Mercury 7, Venus 7, Mars 8, Jupiter 9, Saturn 9, outers 5 | VOC / horary's documented basis |

```python
ha.set_orb_system('flatlib')          # raises ValueError on unknown name
ha.ORB_SYSTEM                          # 'boom' | 'flatlib'
ha.orb_allowance('Jupiter', 'Saturn')  # (8.0 + 5.0) / 2 == 6.5
ha.ALL_ORBS['Chiron']                  # 3.0 — minor bodies included
```

`set_orb_system()` rewrites `PLANET_ORBS` / `OUTER_ORBS` / `ALL_ORBS` in place,
so consumers reading those names directly keep working. `ORB_SYSTEM` is a module
global — read it as `hermes_astro.ORB_SYSTEM`, not a value captured by
`from hermes_astro import *`, or you will print a stale system.

**Source of truth for the boom table:** `stellium/src/stellium/engines/orbs.py ::
BOOM_FULL_ORBS`. Moon 12→11 and Neptune 5→7 are forced by the GT. Jupiter stays
at 8 — a 7 drops the Jupiter-Saturn trine at 6d26' on 09-25.

## Outer planets

`OUTER_CODES` / `ALL_BODY_CODES` give Uranus / Neptune / Pluto ephemeris ids
(7 / 8 / 9 on both engines). `all_positions(jd, ha.TRAD7 + ha.OUTER3)` fetches
them; passing an unknown body raises `KeyError("unknown body ...")`.

## Verification

```bash
HV="$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/python.exe"
cd "E:/Boom Project/hermes-astro-hub" && "$HV" -m pytest tests/ -q
```

27 tests: 18 original golden-fixture horary tests + 9 in
`tests/test_boom_gt_transits.py`. **The GT test is the important one** — it locks
the three verified transit charts (2026-09-09, 2026-10-14, 2026-10-20) to an exact
aspect set, 40 aspects, 0 missing / 0 extra. Those charts include outer planets.
Changing orbs or the orb rule must keep this test green.

## Pitfalls

- **Interpreter split.** Only the Hermes venv has `swisseph` + `xalen.swe` +
  `hermes_astro` + PIL together. Skill docs saying "run with Boom `.venv`" are
  wrong for anything importing `hermes_astro`. `natal_chart_swe.py` produces
  byte-identical output under either (it has its own engine and does not use the
  Hub).
- **Moiety is not min().** The pre-1.1.0 rule was flatlib's "skip only if BOTH
  bodies' orbs < deviation", which is systematically looser and produced 20 of 80
  GT aspects wrong (all false positives: Saturn 9 vs 5, Jupiter 9 vs 8).
- **VOC uses exact last-aspect timing**, not the orb tables — `voc_time.py`'s
  `set_orb_system('flatlib')` is belt-and-braces, not load-bearing. VOC *does*
  change if you swap systems: 118 vs 93 collected samples over 120 days.
- **Never compare aspect names across layers without normalising case.** The Hub
  returns `conj`/`sq`/`trine`; stellium returns `Conjunction`/`Square`/`Trine`.
  Comparing raw produces a wall of phantom diffs.
- **Read flatlib's actual rule before describing it.** It is "skip only if BOTH
  bodies' orbs < deviation" (pre-1.1.0), not `min()`. Inventing a `min()` filter
  produced a fabricated headline finding.
- **Reproduce the consumer's call, not a reimplementation.** Build every
  comparison from the library's own function. Reimplementing the rule in a
  harness is how three false findings arose (min-filter, a synthetic 10-degree
  separation, aspect-name casing).
- **`xalen` lacks Transneptunian SE ids 40-47** — `calc_ut(jd, 40)` raises
  `ValueError: unsupported SE planet number`. That, not importability, is why
  integrated-astrology falls back to pyswisseph. Verified: xalen handles 7/8/9.
- **A health check must be negative-tested.** `verify_skill_copies.py` was proven
  able to fail by injecting a stale duplicate, an empty managed file, a syntax
  error, and a removed orb-system report (4/4 caught, then restored). A check
  that only ever prints HEALTHY is worthless.
- **Script footers must not claim a basis they don't use.** They now print
  `orbs [{system}]` read from the module, not a hardcoded string.
- **`sync_skill_copies.py` is gone — replaced by `verify_skill_copies.py`.** The old
  script synced a copy of the horary skill that lived at
  `hermes-astro-hub/skills/horary-astrology`. That copy never existed in the current
  layout, so it reported every managed file `[MISSING] ... skipped` while still
  exiting 0 — a silent no-op. The profile copy is now the single canonical one.
  `verify_skill_copies.py` checks completeness, absence of a stale duplicate, Hub
  symbol availability, and that each horary script runs and reports its orb system.
  It is negative-tested: injecting a stale duplicate, an empty managed file, a
  syntax error, or a removed orb-system report each makes it exit 1.

  ```bash
  HV="$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/python.exe"
  cd "E:/Boom Project/hermes-astro-hub" && "$HV" verify_skill_copies.py
  ```

  If you need a backup of the skill, version it — do not fork a second copy.