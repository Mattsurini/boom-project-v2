---
name: myhora-chart
description: Fetch computed charts from myhora.com via POST, no browser.
---

# myhora.com chart via POST

`https://myhora.com/astrology/classical.aspx` is ASP.NET WebForms: the server computes the chart on postback (client JS is UI-only). No browser needed.

## Use the shared module (preferred)

Core logic lives in the hub — do NOT re-implement scraping in individual skills:

```python
from hermes_astro.myhora import get_chart, build_report
chart = get_chart("20.11.2015", "18:18", city="Chiang Rai", tropical=True)
# {meta, natal[24], houses[12], aspects[75]}  (aspects deduped, reciprocal merged)
```

- Module: `E:\Boom Project\hermes-astro-hub\hermes_astro\myhora.py` (editable install; importable from any cwd)
- `get_chart(date, time_hhmm, city=None, lat=None, lon=None, utc="+07:00", name="", tropical=False, house="P", transit=None)`
- `build_report(res, date, time, label, lat, lon, utc)` → markdown with 4 tables: Natal, House cusps, Major aspects (0/60/90/120/180), Minor aspects (30/45/135/150), each sorted by orb
- CLI wrapper: `python E:\\Boom Project\\scripts\\myhora_chart.py DD.MM.YYYY HH:MM "City" [--tropical] [--transit D T] [--json F] [--html F] [--output F]`
- CITIES in module: chiang rai (13,192), chiang saen (13,193), chiang mai (14,210), bangkok (1,15), phuket (42,537) — (province_id, amphur_id, lat, lon, utc). Other places: pass `--lat/--lon/--utc`.
- Run with Hermes venv python (Boom `.venv` python.exe is a broken shim, exit 103).

## Pitfalls (all empirically verified 2026-09)

1. **Zodiac radios are INVERTED vs labels**: `rb_sys1` = tropical, `rb_sys2` = sidereal (Lahiri). Both share `name="sys"` — send ONLY the checked one or the unchecked value overwrites it.
2. **Site is flaky**: intermittent SSL timeouts → retry GET/POST (module does 4 attempts with backoff). `curl` is Cloudflare-blocked on the CDN; use `requests` with a browser User-Agent.
3. **Result structure**: `p_result` div; `ttbh0_tab` → `.pz0` rows (natal), `ttbh1_tab` → `.hz0` (house cusps), `ttbh2_tab` → `.az0` rows whose `title` attr carries `Body1 Aspect (N°) Body2 Orb: ±x.xx°`. Aspect list includes reciprocal pairs — dedupe with frozenset(body1,body2)+aspect+angle. Aspect list also references 0° sign points (เมษ…เมษ = AriesPoint…PiscesPoint) and tropical axis markers (`-trop` suffix).
4. **Thai labels**: derive sign from ecliptic longitude (robust), map bodies by Thai name via `BODY_TH_EN` (longest-key-first prefix match). Tropical marker `ทถ.` is preceded by `\xa0` (non-breaking space) — strip it before matching. Vertex appears as `เวอร์เทค` in aspect titles (spelling variant of the natal label) — both keys are in the map.
5. **Ayanamsa**: myhora's Lahiri is the correct standard value (23.8133° for 1996-11-20). The local swisseph binding returns ~0.88° HIGHER (24.6969°) — a systematic offset in this build, so verify sidereal positions against myhora output, not local swisseph. (Tropical values match swisseph directly.)
6. **Layout fragility**: field names (`__VIEWSTATE`, `dd_province`/`dd_amphur`, `dd_day`/`dd_month`/`dd_year` BE year, `dd_hh`/`dd_mm`, `txt_lat`/`txt_lon`/`txt_utc`) and div classes can break if myhora redesigns; `get_chart` raises if no natal rows parse.
7. **`--transit` is broken server-side (verified 2026-09-11)**: myhora validates the transit date by comparing only **(month, day)** lexicographically against the birth (month, day), **ignoring the year**. For a birth on 20.11, any transit before Nov 21 of the calendar year is rejected with `lab_error` "โปรดตรวจสอบ วันจร/วันที่ทำนาย ต้องเป็็นวันเวลาหลังจากวันเกิด" and 0 natal rows — even for a transit 30 years later. Confirmed: transit 21.11.1996 (day after birth) WORKS; 25.11/20.12/30.11/15.12 all WORK; 21.10/20.11/11.09/01.01/05.09 all FAIL. So `--transit` only works when transit (month,day) > birth (month,day). **Workaround**: cast the transit MOMENT as a plain natal chart (`get_chart(transit_date, transit_time, ...)` — the natal-only path works for any date) and overlay it onto the real natal yourself (map transit longitudes into natal cusps + aspect against natal bodies). See `E:\Boom Project\scripts\myhora_transit_overlay.py`.
8. **Timezone**: the host's `TZ=Asia/Bangkok` is BROKEN (resolves to UTC, not ICT). Use the machine's local clock (already SEAST/ICT) via `date +%d.%m.%Y %H:%M`, or `hermes_astro.ICT` (UTC+7) in Python — never `TZ=Asia/Bangkok date`.

## Verified reference outputs

- 1996-11-20 20:37 ICT Chiang Rai: ASC sidereal 77.90° + 23.8133° = tropical Cancer 11.71° (matches Boom chart profile).
- 2015-11-20 18:18 ICT Chiang Rai: sidereal ASC Taurus 14°26'21" (44.44°), MC Aquarius 2°10'17"; tropical ASC Gemini 8°31'04" (68.52°), MC Aquarius 26°15'00"; 24 bodies, 12 cusps, 75 aspects.
