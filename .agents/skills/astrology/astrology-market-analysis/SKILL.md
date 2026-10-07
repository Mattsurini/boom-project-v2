---
name: astrology-market-analysis
description: Test and use astrology-based market signals.
---

# Astrology Market Analysis

Use this skill when the user asks to test, compare, or use astrology for financial markets: gold/XAU, Nikkei, S&P 500, NASDAQ, DAX, FTSE, crypto, or other tradable assets.

## Core stance

Do **not** present astrology as a standalone trading system. Treat it as:

1. **Timing / sentiment context** — Moon, Nakshatra, Hora, phases.
2. **Risk filter** — hard Moon aspects, Rahu/Ketu, Uranus/Neptune/Pluto, Uranian points.
3. **Volatility / no-trade warning** — high-risk days are often better marked `NO-TRADE` than forced into buy/sell.
4. **Secondary layer** — always cross-check against price action, market session, volume, macro calendar, DXY/yields for gold, and recent trend.

Always include a short disclaimer: exploratory signal only, not financial advice.

## Preferred workflow

### 1. Define the market/session first

Market location and opening time matter.

- **Nikkei / Japan session**: Tokyo, 09:00 JST.
- **S&P 500 / NASDAQ**: New York, 09:30 ET.
- **Gold futures**: New York/COMEX context, often 08:20 ET for pit/session reference; for 24h XAU use the active session requested by the user.
- **DAX**: Frankfurt/Berlin, 09:00 CET/CEST.
- **FTSE**: London, 08:00 GMT/BST.
- **Individual stock IPO chart**: if the user gives only IPO date, use the first trading date at the primary exchange open as an explicit approximation (e.g. Nasdaq/NYSE 09:30 New York). Label it approximate; do not imply a precise incorporation/listing-time chart.

If the user says “global market”, test at least S&P 500, NASDAQ, Gold, DAX, FTSE. Include Nikkei separately if Japan is part of the comparison.

### 2. Use the right model by market

Based on session sanity checks:

- **Nikkei / Japan**: Vedic/Nakshatra model is the strongest first choice.
- **S&P 500 / NASDAQ**: Hybrid model works better: price action + Vedic risk + Western/Uranian risk.
- **Gold / XAU**: astrology-only direction is weak; use astrology mostly for volatility/risk warnings and require DXY/yields/news/price action confirmation.
- **DAX / FTSE**: current simple rules did not validate; do not rely on them without a dedicated backtest.

### 3. Vedic/Nakshatra signals

Useful warning/bias features:

- Moon in **Ashlesha / Mula / Ardra** → avoid / destructive / volatile.
- Moon in **Pushya / Rohini / Ashwini / Hasta / Uttara Phalguni** → more constructive, but still confirm with price.
- **Gandanta** → extreme volatility/reversal risk.
- Moon hard Rahu/Ketu → shock / trap / fakeout / black-swan-style risk.
- Moon hard Uranus/Neptune/Saturn/Mars → volatility, confusion, restriction, aggression.
- Multiple negative Moon aspects → reduce size or no-trade.

### 4. Western + Uranian signals

Use these mostly as volatility/turning-point filters, not direct direction calls.

- Sun–Pluto, Jupiter–Pluto, Mercury–Saturn, Venus–Mars: broad market stress; can persist and over-bias bearish if counted every day.
- Uranus/Pluto/Vulkanus emphasis: sudden moves, shocks, pressure, forced breakout/breakdown.
- Apollon: commerce/expansion; can support risk appetite but is not enough alone.
- Poseidon: narrative, illusion, idealism; treat as misinformation/fake narrative risk in market context.
- Hades/Admetos: decay, blockage, stagnation; use as risk or no-trade filters.

Pitfall: slow aspects persist across many days. Do not let them make every day `BEAR/VOL`. Weight transiting Moon triggers and session-specific activation more heavily.

### 5. Output format

For user-facing results, keep it compact:

```text
Market: Nikkei 225 | Date: YYYY-MM-DD | Session: Tokyo open
Signal: NO-TRADE / BEAR / BULL / SIDEWAYS
Why:
- Vedic: Moon in Mula + Moon square Neptune = high risk
- Western/Uranian: Sun opposite Pluto + Vulkanus activated = volatility
- Price action: prior day downtrend continues
Verdict: avoid longs / only scalp / wait for confirmation
```

For backtests, include:

- Data source (e.g. Yahoo Finance symbol).
- Date range.
- Market/session time used.
- Prediction label vs actual label.
- Score, but label it as **quick sanity check**, not statistical proof.

## Backtesting rules of thumb

- Use open-to-close daily change for a simple directional sanity check.
- Define a flat threshold (e.g. 0.15% of index level, or ~$8 for gold futures in the tested sample).
- Separate `BEAR/VOL` from direct `BEAR` if the model predicts volatility more than direction.
- Count `NO-TRADE` separately where possible; if scoring it, count it as successful when it avoids down/flat long-trade days, but be explicit about that scoring assumption.

## References

- See `references/market-backtest-notes-2026-07.md` for session results and pitfalls from the July 2026 exploratory checks.
- See `references/us-equity-data-fallbacks.md` for Nasdaq API fallback endpoints and cautions when Yahoo/Stooq data fetches are blocked.
