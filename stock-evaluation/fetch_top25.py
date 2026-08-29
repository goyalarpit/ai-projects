"""
Fetches fresh fundamental ratios for India's top 25 NSE large-caps (by
current market cap, picked from a broader candidate list of ~50 well-known
names since exact rank order shifts) and writes docs/data.json for the
GitHub Pages dashboard (docs/index.html).

Run this whenever you want the dashboard refreshed:
    python fetch_top25.py
"""

import json
import os
from datetime import datetime, timezone

import yfinance as yf

from ratios import evaluate, fetch_ratios, resolve_ticker

# Broader candidate list of large NSE names; we rank by live market cap and
# keep the top 25, so the exact ordering doesn't need to be precise here.
CANDIDATES = [
    "RELIANCE", "TCS", "HDFCBANK", "BHARTIARTL", "ICICIBANK", "SBIN", "INFY",
    "LICI", "BAJFINANCE", "HINDUNILVR", "ITC", "LT", "MARUTI", "KOTAKBANK",
    "AXISBANK", "SUNPHARMA", "NTPC", "ADANIENT", "ADANIPORTS", "M&M", "TITAN",
    "ULTRACEMCO", "WIPRO", "ASIANPAINT", "NESTLEIND", "HCLTECH", "COALINDIA",
    "ONGC", "POWERGRID", "TATAMOTORS", "JSWSTEEL", "BAJAJ-AUTO", "TATASTEEL",
    "GRASIM", "ADANIGREEN", "DMART", "BAJAJFINSV", "HDFCLIFE", "SBILIFE",
    "INDUSINDBK", "TECHM", "DRREDDY", "CIPLA", "EICHERMOT", "HEROMOTOCO",
    "BRITANNIA", "DIVISLAB", "APOLLOHOSP", "TRENT", "VBL", "PIDILITIND",
]

# Generic, sector-agnostic value-investing thresholds — the top-25 spans
# banks, IT, FMCG, energy etc., so no single sector's Master Ratio Matrix
# applies. Deliberately small/lenient; flags a stock as "worth a look",
# not a verdict. Debt/Equity is informational for banks/NBFCs (structurally
# high leverage is normal for them) rather than a real red flag.
GENERIC_THRESHOLDS = {
    "peg": {"op": "<=", "value": 1.5, "label": "PEG Ratio", "unit": "x"},
    "debt_equity": {"op": "<=", "value": 1.0, "label": "Debt / Equity", "unit": "x"},
    "current_ratio": {"op": ">=", "value": 1.0, "label": "Current Ratio", "unit": "x"},
    "opm": {"op": ">=", "value": 0.0, "label": "Operating Margin", "unit": "%"},
    "roce": {"op": ">=", "value": 15.0, "label": "ROCE", "unit": "%"},
}


def rank_by_market_cap(candidates, keep=25):
    caps = []
    for symbol in candidates:
        ticker_symbol = resolve_ticker(symbol)
        try:
            fast = yf.Ticker(ticker_symbol).fast_info
            market_cap = fast.get("marketCap") or fast.get("market_cap")
        except Exception:
            market_cap = None
        if market_cap:
            caps.append((ticker_symbol, market_cap))
        print(f"  scanned {ticker_symbol}: {market_cap}")

    caps.sort(key=lambda pair: pair[1], reverse=True)
    return [symbol for symbol, _ in caps[:keep]]


def build_snapshot(ticker_symbols):
    companies = []
    for ticker_symbol in ticker_symbols:
        print(f"  fetching {ticker_symbol}...")
        try:
            meta, ratios = fetch_ratios(ticker_symbol)
        except Exception as exc:
            print(f"  skipping {ticker_symbol}: {exc}")
            continue

        rows, passed, total = evaluate(ratios, GENERIC_THRESHOLDS)
        companies.append({
            "ticker": ticker_symbol,
            "name": meta["name"],
            "sector": meta["sector"],
            "industry": meta["industry"],
            "price": ratios["current_price"],
            "market_cap": ratios["market_cap"],
            "trailing_pe": ratios["trailing_pe"],
            "pb": ratios["pb"],
            "ev_ebitda": ratios["ev_ebitda"],
            "peg": ratios["peg"],
            "debt_equity": ratios["debt_equity"],
            "current_ratio": ratios["current_ratio"],
            "quick_ratio": ratios["quick_ratio"],
            "opm": ratios["opm"],
            "roce": ratios["roce"],
            "dividend_yield": ratios["dividend_yield"],
            "thresholds_passed": passed,
            "thresholds_total": total,
        })

    companies.sort(key=lambda c: c["market_cap"] or 0, reverse=True)
    return companies


def main():
    print(f"Ranking {len(CANDIDATES)} candidates by market cap...")
    top25 = rank_by_market_cap(CANDIDATES, keep=25)

    print(f"\nFetching full ratios for top {len(top25)} by market cap...")
    companies = build_snapshot(top25)

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "thresholds": GENERIC_THRESHOLDS,
        "companies": companies,
    }

    # docs/ lives at the repo root (GitHub Pages only serves repo root or a
    # root-level /docs folder), while this script lives in stock-evaluation/.
    out_path = os.path.join(os.path.dirname(__file__), "..", "docs", "data.json")
    with open(out_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    print(f"\nWrote {out_path} with {len(companies)} companies.")


if __name__ == "__main__":
    main()
