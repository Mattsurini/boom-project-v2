---
date: '2026-08-01'
tags:
- project
source: hermes-astro-hub/skills/astrology/astrology-market-analysis/references/us-equity-data-fallbacks.md
---

# US equity data fallbacks

Use when doing market + astrology analysis for individual US equities and normal data sources fail or rate-limit.

## Nasdaq API fallback

For listed US equities, Nasdaq's public API can return enough delayed data for a grounded quick read. Use browser-like headers:

```text
User-Agent: Mozilla/5.0
Accept: application/json, text/plain, */*
Origin: https://www.nasdaq.com
Referer: https://www.nasdaq.com/market-activity/stocks/<ticker-lower>
```

Useful endpoints:

```text
https://api.nasdaq.com/api/quote/<TICKER>/info?assetclass=stocks
https://api.nasdaq.com/api/quote/<TICKER>/summary?assetclass=stocks
https://api.nasdaq.com/api/quote/<TICKER>/historical?assetclass=stocks&fromdate=YYYY-MM-DD&todate=YYYY-MM-DD&limit=9999
https://api.nasdaq.com/api/company/<TICKER>/financials?frequency=1
```

Notes:

- Data is delayed/non-real-time unless the payload says otherwise.
- Historical rows are newest-first; reverse before computing rolling averages/returns.
- Parse money fields defensively (`$`, commas, negatives like `-$1,234`).
- For split-heavy names, apparent price levels may be split-adjusted; state the source and avoid overclaiming if the data source's adjustment policy is unclear.
- Compare financial statements in consistent units. Nasdaq financial values may be in thousands while market cap is raw dollars; normalize before calculating P/E, P/S, or margins.

## Output discipline

For user-facing answers, give the decision first, then support with the few metrics that matter:

```text
Verdict: HOLD / WAIT / REDUCE / BUY ONLY ABOVE <level>
Price: <last close>; MA50/MA200; 52w distance
Fundamental read: revenue growth, margin, rough valuation
Astro/IPO read: approximate chart basis, key transit, timing risk
Invalidation: levels or events that would change the view
```
