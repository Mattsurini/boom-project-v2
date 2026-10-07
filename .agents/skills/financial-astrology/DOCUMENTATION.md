---
date: '2026-08-01'
tags:
- project
source: hermes-astro-hub/skills/financial-astrology/DOCUMENTATION.md
---

# 📖 Financial Astrology Skill Documentation

> **Created:** 02/05/2026
> **Updated:** 11/05/2026
> **Author:** Trading Bot (AI Assistant) for Minh Swati
> **Purpose:** Reference documentation for session resets, skill rebuilds, or handover

---

## 🆕 Update 11/05/2026: Accurate Hora Service

**Changes:**
- Added `hora_service.py` — module that calculates Planetary Hours accurately using Swiss Ephemeris
- Integrated `hora_service.py` into `financial_astrology.py`, replacing the old `calculate_planetary_hours` function
- **VEDIC FIX:** The day starts from sunrise, not midnight
- **Before sunrise** → use the previous day's day lord
- Chaldean order: Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon

**How to use:**
```python
from skills.financial_astrology.scripts.hora_service import get_current_hora
hora = get_current_hora(lat=34.9333, lon=136.9667, tz_name="Asia/Tokyo")
print(f"Current hora lord: {hora['current_hora']['lord']}")
```

---

## 1. What is this skill for?

Analyzes planetary positions (sidereal/Vedic) and applies them to **short-term trading (Day Trading M15/H1)** for Gold (XAU/USD) and Bitcoin (BTC/USD).

### Main output
- Positions of 8 planets + 3 outer planets (sidereal)
- Moon phase → short-term market sentiment
- Moon Nakshatra + Pada → trader mood
- House placement (Whole Sign) → area of influence
- Moon-Planet combinations (Vedic Yoga) → main trend today
- Moon Aspects → volatility signals for M15/H1
- Combustion detection → false signal warnings
- All major aspects between planets
- Sector analysis: Gold, Bitcoin, stocks
- Day Trading Signal Summary

### NOT used for
- Replacing technical/fundamental analysis
- Guaranteeing profit
- Automatically executing orders

---

## 2. Core Principles

### 2.1 What is Financial Astrology?
Astrology applied to financial markets, based on the hypothesis: **planetary positions influence crowd psychology (fear & greed) → affects price movement.**

> ⚠️ Correlation ≠ causation. This is a **SUPPLEMENTARY** tool, not an accurate forecasting tool.

### 2.2 Golden rule: MOON is the "ACTIVATOR"

> *"Each planet has a tendency, but the Moon decides WHICH tendency gets activated TODAY."*

- Moon = Manas (Mind) in Vedic Astrology
- Market = crowd psychology → Moon moves through the Nakshatras → determines the trader's daily mood
- The planet the Moon interacts with today (via Conjunction, Aspect, or Nakshatra Lord) → sets the trend for the whole session

### 2.3 Astrology system used

| Component | System | Rationale |
|-----------|----------|-------|
| Zodiac | **Sidereal** (Nirayana) | Vedic Astrology, more accurate than Tropical for fixed planets |
| Ayanamsa | **Lahiri** | Vedic standard, most widely used |
| House System | **Whole Sign** | Each house = 1 zodiac sign, simple and accurate for Vedic |
| Planets | 8 bodies + 3 outer | Moon, Sun, Mercury, Venus, Mars, Jupiter, Saturn, Rahu + Uranus, Neptune, Pluto |
| Nodes | **True Node** (Rahu/Ketu) | Rahu = North Node, Ketu = South Node (180° opposite) |

---

## 3. Libraries & Technology

### 3.1 Swiss Ephemeris (pyswisseph)

**Core library** — calculates planetary positions accurately.

- **Package:** `pyswisseph` (Python wrapper)
- **Version:** 2.10.3.2
- **Origin:** Austrian Astrological Institute (Astrodienst)
- **Installation:** `pip3 install pyswisseph`

#### Important functions used:

```python
import swisseph as swe

# 1. Set sidereal mode + Lahiri ayanamsa
swe.set_sid_mode(swe.SIDM_LAHIRI)

# 2. Calculate Julian Day (MUST use UTC)
jd_ut = swe.julday(year, month, day, hour + minute/60.0 + second/3600.0, cal=swe.GREG_CAL)

# 3. Get ayanamsa
ayanamsa = swe.get_ayanamsa_ut(jd_ut)

# 4. Calculate planet position (sidereal)
r, _ = swe.calc_ut(jd_ut, body_id, swe.FLG_SIDEREAL)
# r[0] = longitude, r[1] = latitude, r[2] = distance, r[3] = speed

# 5. Calculate House (tropical first, subtract ayanamsa after)
tropical_cusps, asmc = swe.houses(jd_ut, lat, lon, b'P')
asc_sidereal = (tropical_cusps[0] - ayanamsa) % 360

# 6. Body IDs
swe.MOON, swe.SUN, swe.MERCURY, swe.VENUS, swe.MARS
swe.JUPITER, swe.SATURN, swe.TRUE_NODE  # Rahu
```

### 3.2 Python Standard Library

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo  # timezone handling
import json  # JSON output
import argparse  # CLI arguments
```

### 3.3 No external APIs

- ❌ No astronomy API calls
- ❌ No financial API calls (prices are fetched by another script `get_price.js`)
- ✅ Fully offline, only requires Swiss Ephemeris

---

## 4. Important Calculation Rules

### 4.1 Julian Day — CORRECT WAY

```python
# ✅ CORRECT: Calculate JD from UTC, do NOT add timezone offset
dt_utc = datetime.now(timezone.utc)
jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                dt_utc.hour + dt_utc.minute / 60.0, cal=swe.GREG_CAL)

# ❌ WRONG: NEVER add timezone offset to the JD hour
jd = swe.julday(2026, 5, 1, 16+9)  # WRONG! Large error!
```

### 4.2 Ascendant Sidereal

```python
# Swiss Ephemeris only calculates tropical houses → must subtract ayanamsa
tropical_cusps, asmc = swe.houses(jd_ut, lat, lon, b'P')
asc_sidereal = (tropical_cusps[0] - ayanamsa) % 360
```

### 4.3 House Calculation (Whole Sign)

```python
def get_house(planet_lon, asc_lon):
    asc_sign = int(asc_lon / 30) % 12
    p_sign = int(planet_lon / 30) % 12
    return (p_sign - asc_sign + 12) % 12 + 1
```

### 4.4 Nakshatra Calculation

```python
def get_nakshatra(longitude):
    span = 360.0 / 27.0  # 13°20' per nakshatra
    pada_span = span / 4.0  # 4 padas per nakshatra
    idx = int(longitude / span) % 27
    pos = longitude % span
    pada = int(pos / pada_span) + 1
    return idx, NAKSHATRA_27[idx], pada, NAKSHATRA_LORDS[idx], NAKSHATRA_SYMBOLS[idx]
```

### 4.5 Aspect Calculation

```python
def angle_diff(a, b):
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)  # shortest distance on the circle

# Check aspect
for aname, ainfo in ASPECTS.items():
    angle = ainfo['angle']
    orb = ainfo['orb']
    target = abs(diff - angle)
    if target <= orb:
        # this aspect exists
```

### 4.6 Combustion Detection

```python
sun_lon = bodies_data['Sun']['lon']
for name, limit in COMBUST_ORBS.items():
    diff = angle_diff(sun_lon, bodies_data[name]['lon'])
    if diff <= 0.5:
        # Cazimi — extremely strong energy
    elif diff <= limit:
        # Combust — energy is burnt
```

---

## 5. Skill Directory Structure

```
skills/financial-astrology/
├── SKILL.md                          # Usage instructions (OpenClaw reads this)
├── DOCUMENTATION.md                  # Detailed documentation (this file)
├── scripts/
│   └── financial_astrology.py        # Main script (~400 lines)
```

### How OpenClaw calls the skill

1. OpenClaw reads `SKILL.md` → knows what the skill does
2. When the user requests an astrology analysis → execute the script:
   ```bash
   python3 skills/financial-astrology/scripts/financial_astrology.py
   ```
3. The script outputs results → OpenClaw reads them → integrates into the trading report

---

## 6. CLI Parameters

| Parameter | Default | Description |
|---------|----------|-------|
| `--tz` | Asia/Tokyo | IANA timezone |
| `--date` | Now | YYYY-MM-DD HH:MM:SS |
| `--lat` | 34.9333 | Latitude (Hekinan, Japan) |
| `--lon` | 136.9667 | Longitude |
| `--asset` | all | gold, btc, stocks, all |
| `--json` | False | JSON output instead of text |

### Examples

```bash
# Current time (JST)
python3 scripts/financial_astrology.py

# Specific time
python3 scripts/financial_astrology.py --date "2026-05-02 12:10:00" --tz Asia/Tokyo

# JSON output only
python3 scripts/financial_astrology.py --json

# Analyze Gold only
python3 scripts/financial_astrology.py --asset gold
```

---

## 7. Interpretation Rules

### 7.1 Moon Phase → Market Behavior

| Phase | Psychology | Strategy |
|-------|--------|------------|
| 🌑 New Moon | Low volatility, sideways | Wait for breakout |
| 🌒 Waxing Crescent | Gradually optimistic | Buy dips |
| 🌓 First Quarter | Conflict, decision | Watch reversal |
| 🌔 Waxing Gibbous | High optimism | Trend following |
| 🌕 Full Moon | Emotional peak, HIGH volatility | Avoid overtrading |
| 🌖 Waning Gibbous | Declining optimism | Take profit |
| 🌗 Last Quarter | Reassessment | Hedge |
| 🌘 Waning Crescent | Pessimism | Short, cash |

### 7.2 Moon-Planet Combinations (Most important)

| Combination | Trend | Strategy |
|-------------|-------|----------|
| 🌙☌♂ Chandra-Mangal | Bull Run 🐂 | Buy dips, momentum |
| 🌙☌♄ Vish Yoga | Slow Bleed 🐻 | Sell on rise |
| 🌙☌🐉 Grahan Yoga | The Trap 🕳️ | Option buying, tight SL |
| 🌙☌🔻 Ketu | Panic Button 💥 | Hedge, short |
| 🌙☌♃ Jupiter | Expansion 📈 | Position trading |
| 🌙☌☿ Mercury | Info Flow 📡 | Scalping |
| 🌙☌♀ Venus | Risk Appetite 💎 | Growth stocks |
| 🌙☌☀ Sun | Stable Uptrend ☀️ | Gold, bonds |

### 7.3 Moon Aspects — M15/H1 Signals

| Aspect | Planet | Meaning |
|--------|--------|---------|
| Moon □ Mars | Mars | PANIC SELL / FOMO BUY ⚠️⚠️ |
| Moon ☍ Mars | Mars | Bulls vs Bears, reversal ⚠️ |
| Moon □ Rahu | Rahu | BLACK SWAN ⚠️⚠️⚠️ |
| Moon ☍ Rahu | Rahu | EXTREME DISRUPTION ⚠️⚠️⚠️ |
| Moon △ Jupiter | Jupiter | Strongly bullish ✅ |
| Moon □ Saturn | Saturn | Polarized Fear + Greed ⚠️ |

### 7.4 Combustion → False Signals

| Planet | Orb | Impact |
|-----------|-----|----------|
| Mercury ☿ | ≤14° | Misinformation, false signals |
| Venus ♀ | ≤10° | Wrong risk appetite |
| Mars ♂ | ≤8° | Reduced aggression |
| Jupiter ♃ | ≤10° | Over-optimism |
| Saturn ♄ | ≤14° | Fear amplification |

### 7.5 Nakshatra Trading Quality

| Type | Nakshatra | Lord | Used for |
|------|-----------|------|----------|
| ✅ Good | Ashwini | Ketu | Intraday, quick trades |
| ✅✅ Very good | Pushya | Saturn | Investment, wealth building |
| ✅ Good | Rohini | Moon | Profit-oriented, growth |
| ❌ Avoid | Ardra | Rahu | Emotional volatility |
| ❌ Avoid | Mula | Ketu | Destructive energy |
| ❌ Avoid | Ashlesha | Mercury | Hidden motives, confusion |

---

## 8. Planets & Asset Classes

| Asset | Ruling planet | Sector |
|-------|-------------------|--------|
| 🥇 Gold (XAU/USD) | ☀️ Sun, ♀️ Venus | Safe haven, inflation hedge |
| 🥈 Silver | 🌙 Moon | Industrial + precious metal |
| ₿ Bitcoin | 🐉 Rahu, ⛧ Uranus | Crypto, decentralization |
| 💻 Tech stocks | ⛧ Uranus | Innovation, disruption |
| ⛽ Energy | ♂️ Mars | Oil, gas, defense |
| 🏦 Finance/Banking | ♃ Jupiter, ♄ Saturn | Credit, lending |

---

## 9. Skill Creation Process (Step by Step)

### Step 1: Identify the requirements
- Minh wants astronomy analysis as support for Gold & Bitcoin trading
- Focus: Day Trading M15/H1
- Language: Vietnamese

### Step 2: Research the principles
- Financial Astrology (J.N. Bhasin, Raymond Merrman)
- Vedic Astrology (sidereal, Lahiri ayanamsa, Whole Sign houses)
- Moon phases & market behavior research (Journal of Behavioral Finance)
- Nakshatra trading quality

### Step 3: Choose the tools
- **Swiss Ephemeris** (pyswisseph) — the most accurate astronomy library
- Python 3 — easy to read, easy to maintain
- No external APIs — runs offline, no network dependency

### Step 4: Write the script
1. Install Swiss Ephemeris: `pip3 install pyswisseph`
2. Define data: 27 nakshatras, lords, symbols, zodiac signs, aspects, combustion orbs
3. Write calculation functions: Julian Day, planet positions, houses, nakshatras, aspects, combustion, moon phase
4. Write interpretation functions: moon combinations, moon aspects, nakshatra quality, sector analysis
5. Format output: clean, readable text with emojis

### Step 5: Create SKILL.md
- Describe the skill so OpenClaw can recognize it
- Document how to use the script
- List the interpretation rules

### Step 6: Test & Debug
- Test with different times
- Compare planet positions with other sources
- Fix bugs: Julian Day timezone miscalculation, Ascendant sidereal

---

## 10. Notes for Rebuild / Session Reset

### If the session is reset, you need to:
1. ✅ Keep the folder `skills/financial-astrology/`
2. ✅ Check pyswisseph is still installed: `pip3 show pyswisseph`
3. ✅ Check the script runs: `python3 scripts/financial_astrology.py`
4. ✅ Check SKILL.md is still in the folder

### If pyswisseph is missing:
```bash
pip3 install pyswisseph
```

### If an update is needed:
- Edit `financial_astrology.py` → add planets, add aspects, adjust orbs
- Edit `SKILL.md` → change description, add examples
- Always test: `python3 scripts/financial_astrology.py --json`

---

## 11. Integration with the Trading System

### Operation flow:
```
User requests an analysis
    ↓
OpenClaw calls the script financial_astrology.py
    ↓
Script outputs the astrology results
    ↓
OpenClaw calls get_price.js → gets the current price
    ↓
OpenClaw calls analyze_btc.js / technical analysis
    ↓
OpenClaw combines: fundamental + technical + astrology
    ↓
Outputs BUY/SELL suggestion with entry price, SL, TP
```

### Related scripts:
- `get_price.js` — fetches Gold & Bitcoin prices from TradingView
- `analyze_btc.js` — Bitcoin technical analysis
- `package.json` — dependencies (Node.js: @mathieuc/tradingview)

---

## 12. Warnings & Red Lines

⚠️ **Always remind the user:**
- Financial astrology is a SUPPLEMENTARY tool
- Correlation ≠ causation
- Always use stop loss
- Do not risk more than 1-2% per trade
- Investing involves risk; you are responsible for your own decisions

❌ **Never:**
- Guarantee profit
- Automatically execute orders
- Give personal financial advice
- Replace technical/fundamental analysis

---

## 13. References

### Books
- *Financial Astrology* — J.N. Bhasin
- *The World According to the Stars* — Raymond Merrman
- *Lal Kitab* — Five volumes of Vedic astrology rules

### Research
- Journal of Behavioral Finance — Moon phases & stock returns
- Cambridge Judge Business School — Lunar cycles & investor sentiment

### Tools
- Swiss Ephemeris: https://www.astro.com/swisseph
- pyswisseph: https://github.com/aloistr/pyswisseph
- Ayanamsa Lahiri: Vedic Astrology standard

---

## 15. Dasha (Vimshottari)

### Introduction

**Dasha** is the ruling planet cycle in Vedic Astrology, used to predict life events.

**Vimshottari Dasha** is the most popular system:
- Total cycle: **120 years**
- Based on the **Moon Nakshatra** at birth
- Each planet has a different number of years

### Years per planet

| Planet | Years |
|-----------|--------|
| Ketu | 7 |
| Venus | 20 |
| Sun | 6 |
| Moon | 10 |
| Mars | 7 |
| Rahu | 18 |
| Jupiter | 16 |
| Saturn | 19 |
| Mercury | 17 |
| **Total** | **120** |

### How to calculate

1. Find the Moon Nakshatra at birth
2. The Nakshatra Lord is the planet that starts the Dasha
3. Calculate the remaining fraction in the Nakshatra
4. First Dasha = remaining × years of the Lord
5. Subsequent Dashas follow the order: Ketu → Venus → Sun → Moon → Mars → Rahu → Jupiter → Saturn → Mercury

### Antardasha (Sub-period)

Each Dasha is divided into 9 Antardashas:
- Antardasha = (Dasha years × Sub-lord years) / 120
- The Antardasha order is the same as the Dasha order, starting from the Main Lord

### Using it in the script

```bash
# Natal Chart with Dasha
python3 scripts/financial_astrology.py --date "1995-04-25 18:30:00" --tz Asia/Ho_Chi_Minh --lat 21.1861 --lon 106.0763 --natal

# Transit analysis (no Dasha)
python3 scripts/financial_astrology.py
```

### Notes

- Dasha is only calculated for the **Natal Chart** (add `--natal`)
- Transit analysis does **not use Dasha** (crowd psychology)
- Dasha is used to analyze **an individual's life**

---

## 14. Changelog

| Date | Version | Changes |
|------|-----------|----------|
| 2026-05-02 | v3 | Current version — Full features: Moon phase, nakshatra, aspects, combustion, houses, sector analysis |
| 2026-05-02 | v4 | Added Dasha (Vimshottari) for Natal Chart, --natal flag |

---

**📝 Note for Minh:**
This file contains all the knowledge about the Financial Astrology skill. If the session is reset, just:
1. Keep the folder `skills/financial-astrology/`
2. Make sure `pyswisseph` is still installed
3. The new session will automatically read `SKILL.md` and use it right away

If you need new features (add planets, add indicators, export PDF...), just ask! 📊
