---
title: "financial-astrology — reference material"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "financial_astrology-reference"
tags: [skill-reference, financial-astrology]
source_classes: [synthesis]
status: "verified"
summary: "Deep reference sections moved verbatim out of financial-astrology/SKILL.md so the loaded body stays small."
---

## 📋 Using the Script

### Financial Astrology Analysis
```bash
# Current analysis (JST)
python skills/financial-astrology/scripts/financial_astrology.py

# Specific time
python skills/financial-astrology/scripts/financial_astrology.py --date "2026-05-02 12:10:00" --tz Asia/Tokyo

# Specify coordinates
python skills/financial-astrology/scripts/financial_astrology.py --lat 34.93 --lon 136.97

# Analyze a specific asset
python skills/financial-astrology/scripts/financial_astrology.py --asset gold
python skills/financial-astrology/scripts/financial_astrology.py --asset btc

# JSON output
python skills/financial-astrology/scripts/financial_astrology.py --json

# Natal Chart with Dasha (Major - Minor periods)
python skills/financial-astrology/scripts/financial_astrology.py --date "1995-04-25 18:30:00" --tz Asia/Ho_Chi_Minh --lat 21.1861 --lon 106.0763 --natal
```

### Calculating Hora (Planetary Hours)
```python
# Use hora_service.py to calculate accurate hora
from skills.financial_astrology.scripts.hora_service import get_current_hora

# Default: Hekinan, Japan (Asia/Tokyo)
hora = get_current_hora()
print(f"Current hora lord: {hora['current_hora']['lord']}")
print(f"Trading bias: {hora['current_hora']['trading']}")

# Custom coordinates and timezone
hora = get_current_hora(lat=34.9333, lon=136.9667, tz_name="Asia/Tokyo")
```

**Hora calculation rules:**
- Hora divides the 24h into 24 hours ruled by 7 planets
- Chaldean order: Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon
- The first hour of the day (sunrise) belongs to the ruler of that day
- **VEDIC FIX:** The day starts at sunrise, not midnight
- If before sunrise → use the previous day's day lord

## 🔗 MOON + PLANET COMBINATIONS (Most important for Day Trading!)

### Moon ☌ Mars (Chandra-Mangal Yoga) = "Bull Run" 🐂
- **Trend:** Fast rise, high volume, aggressive bullish
- **Strategy:** Buy on dips, momentum trading
- **⚠️ If Mars is weak (Cancer):** Can turn into panic selling

### Moon ☌ Saturn (Vish Yoga) = "Slow Bleed" 🐻
- **Trend:** Range-bound to negative, struggle at resistance
- **Strategy:** Sell on rise, avoid fresh long

### Moon ☌ Rahu (Grahan Yoga) = "The Trap" 🕳️
- **Trend:** High volatility, fake breakout, sudden spikes
- **Strategy:** Option buying (gamma moves), DO NOT hold overnight

### Moon ☌ Ketu = "Panic Button" 💥
- **Trend:** Sudden drop with no news, "bottom falls out"
- **Strategy:** Hedge, shorting opportunities

### Moon ☌ Jupiter = "Expansion" 📈
- **Trend:** Steady growth, banking rally, optimism
- **Strategy:** Position trading, banking/finance stocks

### Moon ☌ Mercury = "Information Flow" 📡
- **Trend:** High volatility, whipsaws (constant ups and downs)
- **Strategy:** Scalping, quick in-out

### Moon ☌ Venus = "Risk Appetite" 💎
- **Trend:** Risk-on, consumer/luxury stocks strong
- **Strategy:** Growth stocks, consumer sector

### Moon ☌ Sun = "Stable Uptrend" ☀️
- **Trend:** Steady rise, high confidence, low volatility
- **Strategy:** Gold, government bonds, PSU

### Moon ☌ Rahu (Nakshatra) = "Disruption" 🌪️
- **Trend:** Sudden volatility, fake moves
- **Strategy:** Tight SL, avoid overnight

### Moon ☌ Ketu (Nakshatra) = "Chaos" 🌀
- **Trend:** Panic fall, confusion, algorithm breaks
- **Strategy:** Cash, defensive positioning

