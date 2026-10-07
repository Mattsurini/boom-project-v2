---
name: financial-astrology
description: Financial Astrology — planetary positions for market analysis.
---

# 📊 Financial Astrology

Analyzes planetary positions + Nakshatra + Pada + Houses + Aspects + Combustion + **Market psychology** according to Financial Astrology rules.

## 🌙 GOLDEN RULE: MOON IS THE "ACTIVATOR"

> **"Each planet has a tendency, but the Moon decides WHICH tendency gets activated TODAY."**

In Vedic Astrology, Moon represents **Manas (Mind)**. Because financial markets reflect crowd psychology (Fear & Greed), the Moon moving through the Nakshatras determines the trader's mood each day.

**Rule:** "The planet the Moon interacts with today (via Conjunction, Aspect, or Nakshatra Lord) sets the trend for the whole session."

## ⚠️ Calculation Rules

### Julian Day (CORRECT WAY)
```python
# ✅ CORRECT: UTC first, then compute JD
dt_utc = datetime.now(timezone.utc)
jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                dt_utc.hour + dt_utc.minute / 60.0, cal=swe.GREG_CAL)

# ❌ WRONG: NEVER add the timezone offset to the hour
jd = swe.julday(2026, 5, 1, 16+9)  # WRONG!
```

### Input/Output
- **Input/Output**: JST (Asia/Tokyo, UTC+9) by default
- **Calculation**: UTC
- **Ascendant sidereal** = Ascendant tropical − ayanamsa
- **House System**: Whole Sign (Vedic)

## 🌙 MOON PHASES & MARKET BEHAVIOR

| Phase | Market psychology | Strategy |
|-------|------------------|------------|
| 🌑 **New Moon** | Start of a new cycle, low volatility, sideways | Wait for breakout a few days later |
| 🌒 **Waxing Crescent** | Gradually optimistic, Bullish | Buy dips, momentum |
| 🌓 **First Quarter** | Conflict, decision point, volatility | Watch for reversal |
| 🌔 **Waxing Gibbous** | High optimism, Bullish | Trend following |
| 🌕 **Full Moon** | Emotional peak, HIGH volatility, reversal | Avoid overtrading, watch reversal |
| 🌖 **Waning Gibbous** | Declining optimism, caution | Take profit, tighten SL |
| 🌗 **Last Quarter** | Reassessment, volatility | Hedge, reduce position |
| 🌘 **Waning Crescent** | Pessimism, Bearish | Short, cash is king |

**Research:** Journal of Behavioral Finance — Returns drop significantly around the New Moon and rise around the Full Moon. Many hedge funds track lunar cycles as a sentiment indicator.

## 🌙 MOON SIGN & MARKET MOOD

| Element | Signs | Mood | Trading bias |
|-----------|------|------|----------------|
| 🔥 **Fire** | ♈♌♐ | RISK-ON, confident, bullish | BUY dips, momentum plays |
| 🌍 **Earth** | ♉♍♑ | PRACTICAL, safe haven | Gold strong, focus fundamentals |
| 💨 **Air** | ♊♎♒ | RATIONAL, indecisive, sideways | Range trading, false breakouts |
| 💧 **Water** | ♋♏♓ | EMOTIONAL, sensitive | Watch sudden moves, tight SL |

## 🌟 NAKSHATRA & TRADING

### ✅ Nakshatra Good for Trading
| Nakshatra | Lord | Trade type | Characteristics |
|-----------|------|-----------|----------|
| 🐴 **Ashwini** | Ketu | Intraday, quick trades | Fast, action, mental agility |
| 🌸 **Pushya** | Saturn | Investment, positional | Most auspicious, wealth building |
| 🐂 **Rohini** | Moon | Profit-oriented | Growth, abundance, mid/large cap |
| 🛏️ **Uttara Phalguni** | Sun | Strategic planning | Discipline, portfolio diversification |
| ✋ **Hasta** | Moon | Swing trading | Precision, timing, chart analysis |

### ❌ Nakshatra to Avoid
| Nakshatra | Lord | Reason |
|-----------|------|-------|
| 🌊 **Ardra** | Rahu | Emotional volatility |
| 🌿 **Moola** | Ketu | Destructive energy |
| 🐍 **Aslesha** | Mercury | Hidden motives, confusion |

### 🌊 Gandanta Points (Danger zones)
- **Where water meets fire:** Last degree of Water signs (♋♏♓) ↔ First degree of Fire signs (♈♌♐)
- **Effect:** Extreme volatility, unexpected reversal, "drowning point"
- **Strategy:** Avoid trading at gandanta zones, or use a very tight SL

## 🔥 COMBUSTION (Planet burnt by the Sun)

When a planet is too close to the Sun, its energy is "burnt":

| Planet | Orb Combust | Market impact |
|-----------|-------------|-------------------|
| ☿️ **Mercury** | ≤14° | Misinformation, false signals, confusion |
| ♀️ **Venus** | ≤10° | Wrong risk appetite, valuation distortion |
| ♂️ **Mars** | ≤8° | Reduced aggression, but sudden rises |
| ♃ **Jupiter** | ≤10° | Over-optimism → disappointment |
| ♄ **Saturn** | ≤14° | Fear amplification, panic |

### ⚡ Cazimi (In the heart of the Sun)
- **Orb:** ≤0.5° from the Sun
- **Effect:** The planet's energy is concentrated EXTREMELY strongly
- **Market impact:** Very strong but one-directional trend

## 🔗 ASPECTS — Meaning for Trading

| Aspect | Orb | Symbol | Impact |
|--------|-----|--------|----------|
| ☌ **Conjunction** | ≤8° | Unified energy | Strongest, new trend |
| ⚹ **Sextile** | ≤6° | Harmonious | Entry opportunity, good flow |
| □ **Square** | ≤7° | Tension | HIGH volatility, challenge |
| △ **Trine** | ≤8° | Favorable | Strong trend, growth |
| ☍ **Opposition** | ≤8° | Polarity | Turning point, volatility |
| ⚻ **Quincunx** | ≤3° | Adjustment | Instability, need to adapt |
| ∠ **Semi-Square** | ≤2.5° | Mild tension | Watch for escalation |
| ⚼ **Sesquiquadrate** | ≤2.5° | Mild tension | Friction building |

### 🌙 Moon Aspects — Most important for M15/H1
- **Moon □ Mars:** PANIC SELL / FOMO BUY, very volatile ⚠️⚠️
- **Moon ☍ Mars:** Bulls vs Bears, battlefield, prone to reversals
- **Moon □ Mercury:** False signals, contradictory information
- **Moon ☍ Mercury:** Market divergence, confusion
- **Moon □ Rahu:** BLACK SWAN potential ⚠️⚠️⚠️
- **Moon ☍ Rahu:** Major DISRUPTION, extremely strong volatility
- **Moon △ Jupiter:** Strongly bullish, expansion
- **Moon ☌ Jupiter:** Optimism, steady growth
- **Moon □ Saturn:** Fear + greed, polarized
- **Moon ☍ Saturn:** Extreme Fear vs Greed, turning point

## 🪐 PLANETS & ASSET CLASSES

| Asset | Ruling planet | Related sector |
|-------|-------------------|-----------------|
| 🥇 **Gold (XAU/USD)** | ☀️ Sun, ♀️ Venus | Safe haven, inflation hedge |
| 🥈 **Silver** | 🌙 Moon | Industrial + precious metal |
| ₿ **Bitcoin** | 🐉 Rahu, ⛧ Uranus | Crypto, decentralization |
| 💻 **Tech stocks** | ⛧ Uranus | Innovation, disruption |
| ⛽ **Energy** | ♂️ Mars | Oil, gas, defense |
| 🏦 **Finance/Banking** | ♃ Jupiter, ♄ Saturn | Credit, lending, insurance |
| 📱 **IT/Telecom** | ☿️ Mercury | Software, communication |
| 🏗️ **Infrastructure** | ♄ Saturn | Real estate, cement, metals |
| 🎮 **Speculative** | 🐉 Rahu | Penny stocks, meme coins |

## ⏰ HORA (PLANETARY HOURS) — Chaldean Order

### Calculation rules:
- **Chaldean order:** Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon
- **The day starts at sunrise** (VEDIC FIX), not midnight
- **The first hour** (sunrise) belongs to the ruler of that day
- **Before sunrise** → use the previous day's day lord

### Day lords:
| Day | Planet |
|------|----------|
| Sunday | ☀️ Sun |
| Monday | 🌙 Moon |
| Tuesday | ♂️ Mars |
| Wednesday | ☿️ Mercury |
| Thursday | ♃ Jupiter |
| Friday | ♀️ Venus |
| Saturday | ♄ Saturn |

### Meaning of Hora for Trading:

| Hora | Trading Focus | Strategy | Element |
|------|--------------|----------|---------|
| ☀️ **Sun** | Authority, government, gold | Good for gold, government bonds, stable trades | 🔥 Fire |
| 🌙 **Moon** | Emotions, public sentiment, liquids | Watch sentiment shifts, silver, consumer goods | 💧 Water |
| ♂️ **Mars** | Energy, aggression, metals, real estate | Volatile moves, momentum trading, energy stocks | 🔥 Fire |
| ☿️ **Mercury** | Communication, tech, data, short-term | Scalping, IT stocks, quick in-out | 🌍 Earth |
| ♃ **Jupiter** | Expansion, banking, wisdom, growth | Banking stocks, position trading, bullish bias | ✨ Ether |
| ♀️ **Venus** | Luxury, arts, relationships, comfort | Consumer goods, luxury stocks, trend following | 🌍 Earth |
| ♄ **Saturn** | Discipline, restriction, delay, structure | Defensive positioning, infrastructure, cautious | 💨 Air |

## 📊 OUTER PLANETS & LONG-TERM CYCLES

| Planet | Cycle | Market impact |
|-----------|--------|-------------------|
| ♃ **Jupiter** | 11.86 years | Bull market cycles, expansion |
| ♄ **Saturn** | 29.46 years | Bear market, correction, restructuring |
| ⛧ **Uranus** | 84 years | Disruption, innovation, bubbles |
| ♆ **Neptune** | 165 years | Bubbles, illusion, deception |
| ♇ **Pluto** | 248 years | System change, power shifts |
| **Jupiter-Saturn** | ~20 years | Business cycle, regime change |

### ♇ Pluto by sign
| Sign | Period | Impact |
|------|-----------|----------|
| ♑ **Capricorn** | 2008-2024 | Financial crisis, death of old banking |
| ♒ **Aquarius** | 2024-2044 | Crypto, AI, decentralization, tech revolution |

### ⛧ Uranus by sign
| Sign | Period | Impact |
|------|-----------|----------|
| ♈ **Aries** | 2010-2019 | Tech boom, cryptocurrency birth |
| ♉ **Taurus** | 2018-2026 | Finance disruption, currency, resources |

## 📈 SECTOR ROTATION BY PLANET

| Planet | Strong sectors | Weak sectors |
|-----------|------------|-----------|
| ☀️ **Sun** | PSU, Gold, Government bonds | Crypto, speculative |
| 🌙 **Moon** | Silver, consumer, real estate | - |
| ☿️ **Mercury** | IT, media, telecom, brokerage | Heavy industry |
| ♀️ **Venus** | Luxury, consumer, art, beauty | Defense, mining |
| ♂️ **Mars** | Defense, energy, metals, real estate | Utilities, bonds |
| ♃ **Jupiter** | Banking, finance, education, FMCG | - |
| ♄ **Saturn** | Infrastructure, mining, cement | Tech, growth stocks |
| 🐉 **Rahu** | Crypto, penny stocks, tech, speculative | Traditional, conservative |
| 🔻 **Ketu** | Pharma (during crash), spiritual | - |

## 📅 HISTORICAL EXAMPLES

| Event | Planetary configuration |
|---------|-------------------|
| **1987 Black Monday** | Significant lunar cycle event |
| **2000 Dot-com crash** | Jupiter-Saturn conjunction |
| **2008 Financial crisis** | Saturn ☌ Ketu in Leo |
| **2020 COVID crash** | Mars ☌ Jupiter ☌ Saturn in Capricorn |
| **2021 Bull run** | Jupiter in Aquarius, Rahu in Taurus |
| **BTC ATH Oct 2025** | $126,198 — Cycle peak |

## ⚠️ Warnings

- **Correlation ≠ causation** — Planets do not "cause" market moves
- **Financial astrology is a SUPPLEMENTARY tool**, NOT a replacement for technical/fundamental analysis
- **Always use stop loss**, do not risk more than 1-2% per trade
- **Investing involves risk; you are responsible for your own decisions**

## 🔧 Script Parameters

| Parameter | Default | Description |
|---------|----------|-------|
| `--tz` | Asia/Tokyo | IANA timezone |
| `--date` | Now | YYYY-MM-DD HH:MM:SS |
| `--lat` | 34.9333 | Latitude |
| `--lon` | 136.9667 | Longitude |
| `--asset` | all | gold, btc, stocks, all |
| `--json` | False | JSON output |
| `--natal` | False | Calculate Dasha for Natal Chart |

## Reference files — open only when its topic comes up
The body above suffices for a standard pass; opening this costs more than the old single file did.

- `financial_astrology-reference.md` — Deep reference sections moved verbatim out of financial-astrology/SKIL
- Moved sections: 📋 Using the Script, 🔗 MOON + PLANET COMBINATIONS (Most important for Day Trading!)
