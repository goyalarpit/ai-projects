"""
Single-stock lookup tool for the Aerospace & Defence sector — fetches key
fundamental ratios via yfinance and checks them against the sector
thresholds from the IIMC Corporate Finance assignment's Master Ratio Matrix.

Usage:
    python stock_lookup.py HAL.NS
    python stock_lookup.py BEL          # bare symbol -> auto-suffixed .NS

This is a screening aid, not investment advice. Scoped to one sector for
now — more sectors can be added once this is validated.
"""

import sys

from ratios import evaluate, fetch_ratios, fmt_market_cap, resolve_ticker

# Aerospace & Defence thresholds, ported from the assignment's Master Ratio Matrix.
THRESHOLDS = {
    "current_ratio": {"op": ">=", "value": 1.5, "label": "Current Ratio", "unit": "x"},
    "quick_ratio": {"op": ">=", "value": 1.0, "label": "Quick Ratio", "unit": "x"},
    "debt_equity": {"op": "<=", "value": 0.3, "label": "Debt / Equity", "unit": "x"},
    "interest_coverage": {"op": ">=", "value": 10.0, "label": "Interest Coverage", "unit": "x"},
    "opm": {"op": ">=", "value": 18.0, "label": "Operating Margin", "unit": "%"},
    "roce": {"op": ">=", "value": 18.0, "label": "ROCE", "unit": "%"},
    "peg": {"op": "<=", "value": 1.5, "label": "PEG Ratio", "unit": "x"},
    "ev_ebitda": {"op": "range", "low": 15.0, "high": 25.0, "label": "EV / EBITDA", "unit": "x"},
}


def print_report(ticker_symbol, meta, ratios, rows, passed, total):
    print("=" * 65)
    print(f"{meta['name']}  ({ticker_symbol})")
    print(f"Sector: {meta['sector'] or 'N/A'}   Industry: {meta['industry'] or 'N/A'}")
    print("=" * 65)
    print(f"Price: {ratios['current_price']}   Market Cap: {fmt_market_cap(ratios['market_cap'])}   "
          f"Trailing P/E: {ratios['trailing_pe']}   P/B: {ratios['pb']}")
    print()
    print("Checked against Aerospace & Defence thresholds (IIMC assignment Master Ratio Matrix)")
    print("-" * 65)
    print(f"{'Ratio':<22}{'Actual':<12}{'Requirement':<18}{'Verdict':<10}")
    print("-" * 65)
    for label, actual, requirement, verdict in rows:
        print(f"{label:<22}{actual:<12}{requirement:<18}{verdict:<10}")
    print("-" * 65)

    if total == 0:
        print("Not enough data available to form a verdict.")
    else:
        print(f"{passed}/{total} thresholds passed.")

    print()
    print("Note: this is a mechanical ratio screen, not investment advice.")


def main():
    if len(sys.argv) != 2:
        print("Usage: python stock_lookup.py <TICKER>")
        print("Example: python stock_lookup.py HAL.NS")
        sys.exit(1)

    ticker_symbol = resolve_ticker(sys.argv[1])

    try:
        meta, ratios = fetch_ratios(ticker_symbol)
    except Exception as exc:
        print(f"Error fetching data for '{ticker_symbol}': {exc}")
        sys.exit(1)

    rows, passed, total = evaluate(ratios, THRESHOLDS)
    print_report(ticker_symbol, meta, ratios, rows, passed, total)


if __name__ == "__main__":
    main()
