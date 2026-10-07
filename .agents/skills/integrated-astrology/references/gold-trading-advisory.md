---
date: '2026-07-12'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/gold-trading-advisory.md
---

# Gold Trading Advisory — Combined Analysis Use Case

This reference documents the workflow for generating astrological gold trading signals by combining:
1. **.ics transit files** from Astro-Seek (personal transits)
2. **Financial-astrology** skill (Vedic/sidereal planetary analysis)
3. **Gold spot price** from api.gold-api.com
4. **USD/THB rate** from Yahoo Finance
5. **Live planetary positions** from Swiss Ephemeris (pyswisseph)

## Source Files

| File | Path | Purpose |
|------|------|---------|
| `gold_trading_advisory.py` | `~/AppData/Local/hermes/scripts/gold_trading_advisory.py` | Main advisory script |
| `gold_price.py` | `~/AppData/Local/hermes/scripts/gold_price.py` | Gold price-only (used by gold-price-2h cron) |
| `daily_transit.py` | `~/AppData/Local/hermes/scripts/daily_transit.py` | Daily .ics transit summary (used by daily-transit cron) |
| `.ics files` | `~/AppData/Local/hermes/scripts/transit_data/` | Stored Astro-Seek .ics (houses, aspects, retrograde, monthly summary) |

## .ics File Sources

Astro-Seek generates 4 types of personal .ics calendars:
- **Personal Transit Calendar (Houses):** Tr. planet enters natal house
- **Personal Transit Calendar (Aspects):** Tr. planet aspects natal planet
- **Retrograde Calendar:** Planetary station dates for 2026
- **Monthly Summary:** Moon phases, sign ingresses, general aspects

These are downloaded by the user from https://horoscopes.astro-seek.com/ and sent as files.

## Scoring Logic

The advisory uses a simple +/- scoring system:

| Factor | Score |
|--------|:-----:|
| Moon in Earth/Water sign (safe haven) | +1 |
| Mercury retrograde (false signals) | -1 |
| Venus square Pluto (emotional spending) | -1 |
| Venus square Uranus (volatility) | -0.5 |
| Jupiter trine Saturn (stable growth) | +1 |
| Jupiter opposition Pluto (tension) | -0.5 |
| Sun conjunct Mercury (cazimi, confusion) | -0.5 |
| Saturn retrograde (economic slowdown) | -1 |

### Signal Thresholds

| Score | Signal | Meaning |
|:-----:|:------:|---------|
| +2+ | 🟢 BUY | Strong astrological support for gold |
| +1 | 🟡 ACCUMULATE | Cautious accumulation |
| 0 | ⚪ HOLD | Neutral, wait |
| -1 | 🟠 CAUTION | Negative factors present |
| -2 | 🔴 SELL/WAIT | Market not supporting gold |

## Cron Jobs

All three cron jobs use `no_agent: true` — the script stdout is delivered directly without LLM processing.

| Job | Schedule | Output |
|-----|----------|--------|
| `gold-price-2h` | Every 2h | Spot price + Thai gold price estimate |
| `daily-transit` | Daily 07:00 ICT | Today's .ics transits with full descriptions |
| `gold-trading-advisory` | Mon-Fri 08:00 ICT | Score + recommendation + .ics notes |

## Related Cron Scripts

All scripts live under `~/AppData/Local/hermes/scripts/`:

```python
# gold_price.py — Simplified, no dependencies beyond urllib + subprocess
# Reads: api.gold-api.com (XAU/USD), stocks_client.py (GC=F, USDTHB=X)
# Output: Spot price, futures, Thai gold estimate

# daily_transit.py — Parses .ics files via icalendar
# Reads: All .ics files in cache + transit_data/
# Output: Today's events, deduplicated by UID

# gold_trading_advisory.py — Combined analysis
# Reads: Swiss Ephemeris + .ics + gold price + financial factors
# Output: Scored recommendation
```
