---
date: '2026-07-27'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/astroseek-ics.md
---

# Astro-Seek .ics — Complete Integration Guide

## ⚠️ DATA PRIORITY (CRITICAL — user-enforced)

```
1. 📁 .ICS FILES (local)     → source of truth, check FIRST
2. 🔭 SWISS EPHEMERIS         → verify / fill gaps when .ics missing data
3. 🔮 ephem library           → last resort, only for quick checks
```

**RULE:** Always read `.ics` files from `~/AppData/Local/hermes/scripts/transit_data/` before calculating with Swiss Ephemeris or ephem. The user explicitly prefers this order. Being slow but accurate via .ics is better than fast-but-wrong via ephem.

**LOCAL EVENTS vs LOCAL CHART:**
- **Local events** = the day’s Astro-Seek event list in ICT; use `SUMMARY` + converted `DTSTART` only
- **Local chart** = Swiss transit chart for the current location; use planet placements + houses
- Do not blend the two in one answer unless the user explicitly asks for both

**HOW TO FIND EVENTS:** grep for the target date (format YYYYMMDD) in the VEVENT blocks. Extract `SUMMARY` (raw transit data like "Tr. Jupiter trine Pluto") — that's what you interpret. Extract `DESCRIPTION` only for reference, but **do NOT quote or read from it** — interpret the raw transit data yourself. The DESCRIPTION is generic Astro-Seek boilerplate, not personalized.

**New Moon / Full Moon:** lives in `*monthly*summary*calendar*.ics`. Search for "NEW MOON" or "FULL MOON" in SUMMARY fields. DTSTART gives the exact UTC time — convert to ICT (+7h).

## File Types from Astro-Seek

| File | Contents | Usage |
|------|----------|-------|
| `*transit*calendar*houses*.ics` | Transit planets entering natal houses (~20/month) | House-based interpretation |
| `*transit*calendar*aspects*.ics` | Transit **to natal** planet aspects (~60/month). **Moon events here are Moon→natal planets, not Moon→transiting planets.** | Aspect-based interpretation |
| `*retrograde*calendar*.ics` | All retrograde/direct stations for entire year (20 events) | Verify retrograde status |
| `*monthly*summary*calendar*.ics` | Global aspects, Moon phases, sign ingresses (~46/month) | Market + global context |
| `*personal*transit*calendar*.ics` | Combined personal transit (sometimes houses+aspects merged) | Mixed usage |

### ⚠️ CRITICAL: `.ics` Moon aspects are personal (transit→natal), not transit→transit

The `*transit*calendar*aspects*.ics` file from Astro-Seek is a **Personal Transit Calendar** — it computes transiting planets against *your natal chart*.

- `Tr. Moon square Saturn` = transit Moon square **natal** Saturn
- `Tr. Moon trine Venus` = transit Moon trine **natal** Venus

This has two implications:

1. **For daily interpretation:** These events are valid and useful — they describe how the current sky activates your birth chart.
2. **For VOC calculation:** Traditional VOC requires Moon→**transiting** planet aspects. The `.ics` file alone will NOT give you the traditional VOC window. Transit→natal aspects produce a different (usually shorter) VOC window because natal planets sit at fixed positions that the Moon may keep aspecting longer.

**If the user wants VOC from `.ics` data**, blend sources: `.ics` for personal activation windows + Swiss for traditional VOC. Always state which calculation produced the answer.

## Acquisition

1. Go to https://horoscopes.astro-seek.com/personal-transit-calendar-monthly-astrology-transits
2. Enter birth data (BooM: 20 Nov 1996, 20:37 ICT, Chiang Rai)
3. Select month/year — download both houses + aspects variants
4. Also download: retrograde calendar + monthly summary calendar
5. Place in `~/AppData/Local/hermes/scripts/transit_data/`

## Storage

- **Stable:** `~/AppData/Local/hermes/scripts/transit_data/` (for cron job access)
- **Notification:** Send to chat so user knows files were saved

## Parsing & Deduplication

```python
from icalendar import Calendar
from datetime import datetime, timezone, timedelta
import os, glob

BKK = timezone(timedelta(hours=7))
today = datetime.now(BKK).strftime('%Y%m%d')

ics_files = glob.glob(os.path.expanduser(
    "~/AppData/Local/hermes/scripts/transit_data/*.ics"))

seen_uids = set()
events = []

for path in sorted(ics_files):
    with open(path, 'rb') as f:
        cal = Calendar.from_ical(f.read())
    for ev in cal.walk('VEVENT'):
        uid = str(ev.get('UID', ''))
        if uid in seen_uids:
            continue
        seen_uids.add(uid)

        dtstart = ev.get('DTSTART').dt
        d = dtstart.astimezone(BKK) if isinstance(dtstart, datetime) \
            else datetime.combine(dtstart, datetime.min.time(), tzinfo=BKK)

        if d.strftime('%Y%m%d') == today:
            events.append((
                d,
                str(ev.get('SUMMARY', '')),
                str(ev.get('DESCRIPTION', ''))
            ))

events.sort(key=lambda x: x[0])
```

## Output Filtering

| Event Type | Show Condition |
|-----------|---------------|
| Non-Moon transits (Sun, Venus, Mars, Jupiter, Saturn, etc.) | Always show |
| Moon transits | Show ONLY if conjunction, opposition, square, or trine |
| Moon enters sign | Show (affects market mood) |
| Retrograde/Direct | Always show (day of station) |
| New Moon / Full Moon / Quarter Moon | Always show |
| Sun enters sign / Venus enters sign | Always show |

## Cross-Verification

Compare .ics predictions with live Swiss Ephemeris to validate accuracy:

```
Current sky             .ics says           Status
─────────────────────────────────────────────────
Venus ♍ 3.1°           Venus enters 3H     ✅
Pluto ♒ 4.6°           Venus □ Pluto       ✅ (90° apart)
Mercury ♋ 21.1° ⬅℞    Mercury Rx in cal    ✅
Moon ♊ 23.2°           Moon □ Mars         ✅
```

## Cron Jobs for BooM

| Job | Schedule | Script | What it delivers |
|-----|----------|--------|-----------------|
| `daily-transit` | 07:00 daily | `daily_transit.py` | All today's .ics events with full prediction text |
| `gold-price-2h` | Every 2h | `gold_price.py` | Spot price, futures, USD/THB, Thai gold |
| `gold-trading-advisory` | 08:00 Mon-Fri | `gold_trading_advisory.py` | Merged: .ics + sky + price → BUY/SELL signal |

All use `no_agent: true` — script stdout delivers directly.
