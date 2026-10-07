---
date: '2026-08-01'
tags:
- project
source: hermes-astro-hub/skills/astrology/astrology-market-analysis/references/market-backtest-notes-2026-07.md
---

# Market Backtest Notes — July 2026

Exploratory sanity checks run during a user session. Data source: Yahoo Finance daily OHLC. Date window: mostly 14–27 Jul 2026. These checks are **not** statistically valid; preserve them as workflow guidance and pitfalls.

## Models tested

### Vedic/Nakshatra financial astrology skill
Used the existing `financial-astrology` skill logic: Sidereal/Lahiri, Moon phase, Moon Nakshatra, Moon aspects, Rahu/Ketu, Hora, and market session location/time.

Results:

| Market | Score | Notes |
|---|---:|---|
| Nikkei 225 | 6/9 = 66.7% | Best fit; Vedic/Nakshatra matched Japan session better than other systems. |
| Gold Futures | 4/10 = 40.0% | Sometimes useful for risk/volatility, weak as direction. |
| S&P 500 | 3/9 = 33.3% | Weak alone. |
| NASDAQ | 3/9 = 33.3% | Weak alone. |
| DAX | 1/9 = 11.1% | Not usable in this sample. |
| FTSE | 0/9 = 0.0% | Not usable in this sample. |

Signals that matched better for Nikkei/Japan:
- Moon in Ashlesha/Mula/Ardra.
- Gandanta.
- Moon hard Rahu/Ketu.
- Moon hard Uranus/Neptune/Saturn/Mars.
- Multiple negative Moon aspects.

### Western/Tropical quick rules on Nikkei
Used Stellium, Tokyo 09:00 JST, Tropical Moon sign/element, Moon aspects, and global Western aspects.

- Nikkei 225: 4/9 = 44.4%.
- Worse than Vedic/Nakshatra for Japan.

### Western + Uranian quick rules on global markets
Used Stellium `.with_uranian()` with Apollon, Vulkanus, Hades, Admetos, Poseidon and Western aspects.

| Market | Score |
|---|---:|
| NASDAQ | 4/9 = 44.4% |
| S&P 500 | 2/9 = 22.2% |
| DAX | 2/9 = 22.2% |
| FTSE | 2/9 = 22.2% |
| Gold | 2/10 = 20.0% |

Pitfall: slow aspects such as Jupiter–Pluto, Pluto–Vulkanus, Mercury–Saturn, Venus–Mars, Sun–Pluto persisted for many days. If counted naively, the model marks almost every day `BEAR/VOL`, causing many false bearish calls.

### Hybrid model
Hybrid = previous-session price action + Vedic risk/bias + Western/Uranian volatility filter.

| Market | Score | Notes |
|---|---:|---|
| S&P 500 | 6/9 = 66.7% | Best global result in this quick test. |
| NASDAQ | 5/9 = 55.6% | Better than Vedic-only or Western/Uranian-only. |
| Nikkei | 5/9 = 55.6% | Worse than Vedic-only; keep Vedic primary for Japan. |
| Gold | 4/10 = 40.0% | Still weak; requires macro filters. |

## Practical conclusions

1. **Nikkei / Japan**
   - Use Vedic/Nakshatra primary.
   - Avoid overcomplicating with Western/Uranian unless the user asks for volatility/turning-point context.

2. **S&P 500 / NASDAQ**
   - Use Hybrid: price action for direction, astrology for risk/no-trade filtering.
   - High astrology risk is better as `NO-TRADE` than automatic short.

3. **Gold / XAU**
   - Do not use astrology-only direction.
   - Add DXY, US yields, news/calendar, session liquidity, and actual trend/levels before giving a trade view.

4. **Europe**
   - Do not reuse the same rules blindly for DAX/FTSE.
   - Requires a separate market-specific model and proper backtest.

## Suggested labels

Use labels that reflect confidence:

- `BULL` — directional long bias, still needs price confirmation.
- `BEAR` — directional short/risk-off bias.
- `SIDEWAYS` — range/no strong edge.
- `BEAR/VOL` — bearish or high-volatility risk; do not conflate with guaranteed downside.
- `NO-TRADE` — risk filter active; best action is avoidance or reduced size.

## User-facing caveat

When reporting results, state: “This is a quick sanity check, not statistical proof.” Avoid saying “exactly on the mark” unless a single event is being described; do not generalize from one event.
