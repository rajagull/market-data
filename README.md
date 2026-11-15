# market-data

Tiny public data feeds maintained by GitHub Actions for the Investify app.

## oil.json — live crude oil prices (USD/bbl)

Updated every ~5 minutes by `scripts/fetch_oil.py` (sources:
TradingView scanner → CNBC → Yahoo), run by a launchd agent
(`com.rajagull.oilfeed`) on the owner's Mac mini. A GitHub Action
(`.github/workflows/oil.yml`) is also present as a backup runner.

Raw URL used by the app:

```
https://raw.githubusercontent.com/rajagull/market-data/main/oil.json
```

Format:

```json
{
  "updatedAt": "2026-11-15T14:35:00Z",
  "source": "tradingview",
  "unit": "USD/bbl",
  "wti":   {"price": 88.56, "previousClose": 88.74, "dayHigh": 89.64, "dayLow": 87.80},
  "brent": {"price": 95.84, "previousClose": 95.82, "dayHigh": 97.12, "dayLow": 95.07}
}
```
