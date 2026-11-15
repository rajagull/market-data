#!/usr/bin/env python3
"""Fetch live crude oil prices (WTI + Brent, USD/bbl) and write oil.json.

Sources, in order: TradingView scanner -> CNBC -> Yahoo Finance.
Runs in GitHub Actions every 5 minutes; the Investify app reads the
resulting oil.json from this repo's raw URL, so the phone only ever
talks to githubusercontent.com.
"""
import json
import sys
import urllib.request
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept": "application/json"}


def get_json(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def from_tradingview():
    out = {}
    for key, sym in (("wti", "NYMEX:CL1!"), ("brent", "NYMEX:BZ1!")):
        import urllib.parse
        url = ("https://scanner.tradingview.com/symbol?symbol="
               + urllib.parse.quote(sym)
               + "&fields=close,open,high,low,change,change_abs")
        d = get_json(url)
        close = float(d["close"])
        prev = close - float(d.get("change_abs", 0))
        out[key] = {"price": close, "previousClose": prev,
                    "dayHigh": float(d.get("high", close)),
                    "dayLow": float(d.get("low", close))}
    return out, "tradingview"


def from_cnbc():
    import urllib.parse
    url = ("https://quote.cnbc.com/quote-html-webservice/restQuote/"
           "symbolType/symbol?symbols=" + urllib.parse.quote("@CL.1|@LCO.1")
           + "&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json")
    d = get_json(url)
    out = {}
    for q in d["FormattedQuoteResult"]["FormattedQuote"]:
        last = float(str(q["last"]).replace(",", ""))
        prev = float(str(q["previous_day_closing"]).replace(",", ""))
        entry = {"price": last, "previousClose": prev,
                 "dayHigh": float(str(q["high"]).replace(",", "")),
                 "dayLow": float(str(q["low"]).replace(",", ""))}
        if q["symbol"] == "@CL.1":
            out["wti"] = entry
        elif q["symbol"] == "@LCO.1":
            out["brent"] = entry
    return out, "cnbc"


def from_yahoo():
    out = {}
    for key, sym in (("wti", "CL=F"), ("brent", "BZ=F")):
        import urllib.parse
        url = ("https://query1.finance.yahoo.com/v8/finance/chart/"
               + urllib.parse.quote(sym) + "?range=1d&interval=5m")
        d = get_json(url)
        meta = d["chart"]["result"][0]["meta"]
        price = float(meta["regularMarketPrice"])
        prev = float(meta.get("chartPreviousClose", price))
        out[key] = {"price": price, "previousClose": prev,
                    "dayHigh": float(meta.get("regularMarketDayHigh", price)),
                    "dayLow": float(meta.get("regularMarketDayLow", price))}
    return out, "yahoo"


def main():
    data, source = None, None
    for fn in (from_tradingview, from_cnbc, from_yahoo):
        try:
            candidate, source = fn()
            if candidate.get("wti") and candidate.get("brent"):
                data = candidate
                break
            print(f"{fn.__name__}: incomplete result {list(candidate)}",
                  file=sys.stderr)
        except Exception as e:  # noqa: BLE001 - try next source
            print(f"{fn.__name__} failed: {e}", file=sys.stderr)
    if not data:
        print("All sources failed", file=sys.stderr)
        sys.exit(1)
    payload = {
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
        "unit": "USD/bbl",
        **data,
    }
    with open("oil.json", "w") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
