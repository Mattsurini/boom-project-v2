
---
name: daily-transit
description: Use when BooM asks for today's or a specific date's transit/mood check. Computes live positions, retrogrades, stations and exact aspect times via swisseph.
---

# Daily Transit Reading Skill

## Procedure
1. If standard templates fail due to path or environment issues, perform a quick transit check using the project's Python engine directly:
   ```bash
   "/c/Users/Turbo/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" "E:/Boom Project/scripts/today_transit_check.py"
   ```
2. For specific dates, refer to pre-generated reports in `/e/Boom Project/Output/Transit/`.
3. If deep transit analysis is required, use `transit_timeline_v3.py` located in `/e/Boom Project/scripts/` (requires `start` and `end` date arguments in `YYYY-MM-DD` format). Run it with the Hermes venv python, which has `swisseph` — the default `python` does not:
   ```bash
   "/c/Users/Turbo/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" "E:/Boom Project/scripts/transit_timeline_v3.py" <start> <end>
   ```
   A single-day scan should finish in ~2s; if it appears to hang, it is a performance regression, not an infinite loop (see Pitfalls).
4. **Run scripts with `E:/...` paths, not `/e/...`**, when invoking a native Windows python. MSYS path conversion is disabled in this environment, so `/e/Boom Project/scripts/x.py` arrives as the literal `E:\e\Boom Project\scripts\x.py` and fails with "can't open file".
5. For retrograde state and stations, `today_transit_check.py`'s RX flag is not usable (see Known bugs). Compute stations directly: sample `swe.calc_ut(jd, body, swe.FLG_SWIEPH | swe.FLG_SPEED)[0][3]` across a window and keep the **LATEST** sign flip before now (assign to `latest` inside the loop; never `break` on the first hit — that yields the earliest station in the window, months or a year stale). 6-hour steps over ~800 days are safe; bisect each bracket down to ~15 min.

## Units and API quirks (each of these produced a wrong reading — don't repeat them)
- **`swe.julday` in the Hermes venv takes 4 args**: `(year, month, day, hour_float)`. Passing `(y, m, d, h, min, sec)` raises `TypeError: function takes at most 5 arguments`. Put minutes in the hour float: `hour + minute/60`.
- **`calc_ut(...)[0][3]` with `FLG_SPEED` is already degrees per DAY.** Do not multiply by 24 — that produces a Moon moving ~800 deg/day. Sanity anchors: Moon ~13.8 deg/day, Sun ~1 deg/day.
- **Never validate speed against a 10-day measured longitude delta.** Near a station or perihelion the instantaneous rate legitimately differs from the 10-day mean (Venus 2026-10-06: instantaneous -0.12, 10-day mean -0.31 deg/day). The correct check is the orbital-period average `360/(period_years * 365.25)`; only the **sign** matters for retrogradeness.
- **Never hand-type natal degree constants** — three were mistyped by 30° in one session. Pull them from the engine: `calc_chart(NATAL_DATE, CITY_LAT, CITY_LON)` returns a **dict** `{"planets": {name: {"longitude", ...}}, "houses": {...}, "asc", "mc", "jd"}`, not a tuple. Rebuild cusps as `[chart["houses"][i]["cusp"] for i in range(1, 13)]` before passing to `house_of`.
- `today_transit_check.py` counts **self-aspects** (transit planet to its own natal placement): expect `N+6` versus a self-aspect-excluding count (51 vs 45 on 2026-10-06). Not a bug — don't chase it.
- Bisection over `timedelta` must return a *time*, not an orb. The naive `a, b = orb(t0), orb(t1)` golden-section rewrite raises `TypeError: unsupported operand type(s) for -: 'float' and 'datetime.datetime'` once `a`/`b` get rebound to floats — use plain trisection and return `lo + (hi - lo) / 2`.

## Pitfalls
- **Engine Selection**: Avoid external API dependencies (e.g., myhora) which are prone to UI-parsing errors. Use local `pyswisseph` via `scripts/today_transit_check.py` for reliable, reproducible transit calculation.
- **Aspect Logic**: Always use a closest-orb search when matching aspects. Naive loops can produce duplicate/invalid matches if multiple aspect angles are checked independently without finding the single best match.
- **Pathing**: Run scripts from `/e/Boom Project` directly to ensure relative imports (like `natal_chart.py`) resolve correctly in the Python path.
- **v3 performance architecture**: In `transit_timeline_v3.py` the root-finding inner loop (`find_exact_aspect_time`, `find_aspect_window`) must call the single-body fast path `transit_lon(jd, name)`, never `get_chart()` (which computes all 18 bodies per sample). The scan must detect which aspects are in-orb, then refine each unique aspect ONCE over the full range — not re-refine the same aspect at every hourly scan step. Violating either (all-bodies per sample, or per-step re-refinement) turns a ~2s single-day scan into a ~16min hang that looks like a freeze. If you touch this script, re-time a single-day run to confirm it stays in seconds.

## Canonical orb rule
Orbs are **moiety**, not per-aspect constants: effective orb for a pair = `(BOOM_FULL_ORBS[A] + BOOM_FULL_ORBS[B]) / 2`, with `BOOM_FULL_ORBS` in `stellium/src/stellium/engines/orbs.py` (Sun 10, Moon 11, Mercury 7, Venus 6, Mars 7, Jupiter 8, Saturn 5, Uranus 5, Neptune 7, Pluto 5). Jupiter must stay 8, Saturn must stay 5 — changing either breaks the verified reference aspect lists. Import that table or copy it verbatim; never hand-write per-aspect orb numbers (conj 8 / sextile 6 / square 8 … is wrong and silently over-collects).

## Known bugs (fixed 2026-10-06 — re-check these if they reappear)
- **Geo-longitude clobbering**: never name a chart function's site-longitude parameter `lon` while also assigning planet longitudes in the same scope. `swe.houses(jd, lat, lon, ...)` then receives a *planet's* longitude as the site's east longitude and every house placement comes out garbage (Sun in H1, Saturn in H7). Name it `geo_lon`, planet longons `plon`.
- **Sign glyph indexing**: a 3-element glyph list (`['♈','♉','♊']`) raises IndexError for sign index >= 3. A 12-element list is required.
- **Retrograde flags are silently garbage**: `swe.calc_ut(jd, body, swe.FLG_SWIEPH)` does not return daily speed — `[0][3]` is 0.0 unless `swe.FLG_SPEED` is also passed. Any RX/DX claim from that call is invalid.
- **`hermes_astro` return shapes**: `houses()` returns a 3-tuple `(cusps, asc, mc)` and `planet_position()` returns `(lon, speed)`. Unpacking them as 2-tuples raises a confusing TypeError.

## Verification
- Confirm the output shows the requested date and time in ICT.
- Ensure all planets are listed with correct signs and houses.
- Sanity-check houses by hand: natal ASC 101.72 ♋, cusp 4 = 184.28, cusp 5 = 218.05. A transit body at ♎13 (193°) is in **House 4**, not House 1.
- Cross-check the aspect list against `transit_timeline_v3.py <start> <end> --inner --orb 2`; overlapping aspects must agree on orb within ~0.1°.
- Retrograde check needs `FLG_SWIEPH | FLG_SPEED` plus a sign comparison across two dates (a single sample's speed sign is enough near a station, unreliable far from one).

## References
- See `integrated-astrology` skill for broader astrological workflows.
