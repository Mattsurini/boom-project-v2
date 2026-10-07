---
name: market-astrology-analysis
description: Workflow for testing and using financial/market astrology as a supplementary market timing and risk filter across Gold, Nikkei, US indices, and global markets.
---

# Market Astrology Analysis

Use this skill when the user asks to analyze markets with astrology, compare Vedic vs Western/Uranian market signals, backtest whether astro signals matched price, or build a trade-timing plan.

## Core principle

Do **not** treat astrology as a standalone buy/sell model. Use it as:

1. **Timing layer** — when to look for setups.
2. **Risk filter** — when not to trade or when to reduce size.
3. **Volatility / reversal warning** — where fakeouts, stop hunts, or turning points are more likely.

Price action, macro context, and actual market data remain the primary ground truth.

## Standard workflow

1. **Define the market and session**
   - Gold: use COMEX/New York timing unless user asks otherwise.
   - Nikkei/Japan: use Tokyo open and Asia/Tokyo.
   - US indices: use New York open.
   - European indices: use local market open.

2. **Get actual market context when checking accuracy**
   - Use real OHLC/current price data.
   - Compare against the relevant session: open→close, or the user-provided chart timeframe.
   - Label results honestly as quick sanity checks unless the sample is statistically large.

3. **Run Vedic/Nakshatra layer**
   - Moon sign/element = mood.
   - Nakshatra = day quality.
   - Rahu/Ketu and Gandanta = major risk flags.
   - Multiple negative Moon aspects = volatility/caution.

4. **Run Western/Uranian layer when requested**
   - Tropical Moon and aspects for market mood.
   - Uranian points such as Vulkanus/Pluto/Uranus = force, shock, volatility.
   - Poseidon/Neptune = false narrative, confusion, fakeout risk.
   - Apollon/Jupiter/Venus = commerce/expansion themes.

5. **For Gold, add macro confirmation**
   Always check or ask for: DXY, yields/real yields, COMEX timing, price zones, and news calendar. Gold direction from astrology alone has been unreliable in quick checks; use astro mainly for timing/fakeout warnings.

6. **Produce a trade-oriented report**
   Keep it concise:
   - Bias: Bull / Bear / Sideways / No-trade
   - Risk: Low / Medium / High
   - Best timing windows with timezone conversion
   - Avoid/fakeout windows
   - Key levels / invalidation
   - What would confirm or invalidate the idea

## Findings from session backtests

Quick July 2026 sanity checks suggested:

- **Nikkei/Japan:** Vedic/Nakshatra fit best among tested approaches. Strong danger signals included Ashlesha, Mula/Moola, Ardra, Gandanta, Moon hard Rahu/Ketu, and several negative Moon aspects.
- **Western+Uranian:** better as a volatility/turning-point filter than direction. Persistent slow aspects can over-label many consecutive days as BEAR/VOL.
- **US indices:** a hybrid of price action + Vedic danger filter + Western/Uranian volatility filter worked better than pure astrology in the small sample.
- **Gold:** astrology-only direction was weak; add DXY/yields/price action. Hora can be used for timing only after price confirms.

## Gold timing approach

For Gold, use New York/COMEX planetary hours for practical timing. Example interpretation:

- Jupiter/Sun/Venus hora: look for buy-dip or continuation **only if price action confirms**.
- Mars hora: volatility, spikes, stop hunts.
- Mercury hora: whipsaw / false breakout risk.
- Saturn hora: pressure / avoid fresh longs unless setup is very clean.

Do not tell the user to buy purely because a benefic Hora is active. Say what chart condition must confirm it.

## Pitfalls

- Do not overclaim accuracy from a small sample.
- Do not say a model is proven; say “quick sanity check” or “small-sample result.”
- Do not forecast Gold direction without macro/price context.
- Do not use persistent outer-planet/Uranian aspects as daily directional calls without de-duplicating their multi-day effect.
- Do not confuse “volatility warning” with “sell signal.”

## User-facing style

The user prefers direct, practical Thai output. For trading/timing, avoid long theory unless asked. Give concrete windows, levels, and the reason each window matters.
