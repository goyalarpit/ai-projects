"""
Shared fundamental-ratio fetch/compute logic, used by both stock_lookup.py
(single-ticker CLI) and fetch_top25.py (batch snapshot for the GitHub Pages
dashboard). Pulled out to one place so both stay in sync.

yfinance's built-in `.info` fields for operatingMargins, enterpriseToEbitda,
currentRatio and quickRatio are unreliable/stale for many NSE tickers —
verified against the IIMC assignment's own numbers for HAL and BEL, where
computing directly from the raw financial statements tracked much closer
(see stock-evaluation/IIMC_Corporate_Finance_Assignment_Insights.md).
"""

import yfinance as yf


def resolve_ticker(raw):
    raw = raw.strip().upper()
    if "." not in raw:
        raw += ".NS"
    return raw


def pct(value):
    """yfinance returns some fields as fractions (0.18) and others already
    as percentages depending on field/version; normalize to percent."""
    if value is None:
        return None
    return value * 100 if abs(value) <= 5 else value


def first_present(row_names, df):
    for name in row_names:
        if name in df.index:
            return df.loc[name].iloc[0]
    return None


def compute_ev_ebitda(info, financials):
    try:
        ev = info.get("enterpriseValue")
        ebitda = first_present(["EBITDA"], financials)
        if not ev or not ebitda:
            return info.get("enterpriseToEbitda")
        return float(ev) / float(ebitda)
    except Exception:
        return info.get("enterpriseToEbitda")


def compute_opm(financials):
    try:
        operating_income = first_present(["Operating Income"], financials)
        revenue = first_present(["Total Revenue", "Operating Revenue"], financials)
        if not operating_income or not revenue:
            return None
        return float(operating_income) / float(revenue) * 100
    except Exception:
        return None


def compute_roce(financials, balance_sheet):
    # Capital Employed = Total Debt + Stockholders' Equity (matches Screener.in's
    # methodology) — Total Assets - Current Liabilities understates ROCE
    # significantly for asset-heavy balance sheets like HAL's.
    try:
        ebit = first_present(["EBIT", "Operating Income"], financials)
        total_debt = first_present(["Total Debt"], balance_sheet)
        equity = first_present(
            ["Stockholders Equity", "Common Stock Equity"], balance_sheet
        )
        if ebit is None or total_debt is None or equity is None:
            return None
        capital_employed = float(total_debt) + float(equity)
        if not capital_employed:
            return None
        return float(ebit) / capital_employed * 100
    except Exception:
        return None


def compute_current_ratio(balance_sheet):
    try:
        current_assets = first_present(["Current Assets"], balance_sheet)
        current_liab = first_present(
            ["Current Liabilities", "Total Current Liabilities"], balance_sheet
        )
        if not current_assets or not current_liab:
            return None
        return float(current_assets) / float(current_liab)
    except Exception:
        return None


def compute_quick_ratio(balance_sheet):
    try:
        current_assets = first_present(["Current Assets"], balance_sheet)
        current_liab = first_present(
            ["Current Liabilities", "Total Current Liabilities"], balance_sheet
        )
        inventory = first_present(["Inventory"], balance_sheet)
        if not current_assets or not current_liab:
            return None
        inventory = float(inventory) if inventory else 0.0
        return (float(current_assets) - inventory) / float(current_liab)
    except Exception:
        return None


def compute_interest_coverage(financials):
    try:
        ebit = first_present(["EBIT", "Operating Income"], financials)
        interest_expense = first_present(
            ["Interest Expense", "Interest Expense Non Operating"], financials
        )
        if ebit is None or not interest_expense:
            return None
        return float(ebit) / abs(float(interest_expense))
    except Exception:
        return None


def fetch_ratios(ticker_symbol):
    """Fetch and compute all ratios for one ticker. Returns (meta, ratios).
    Raises ValueError if no market data is found for the symbol."""
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    if not info or (info.get("regularMarketPrice") is None and info.get("currentPrice") is None):
        raise ValueError(f"No market data found for '{ticker_symbol}' — check the symbol.")

    try:
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
    except Exception:
        financials, balance_sheet = None, None

    peg = info.get("trailingPegRatio") or info.get("pegRatio")
    if peg is None:
        trailing_pe = info.get("trailingPE")
        growth = info.get("earningsGrowth")
        if trailing_pe and growth and growth > 0:
            peg = trailing_pe / (growth * 100)

    de = info.get("debtToEquity")
    if de is not None:
        de = de / 100  # yfinance reports this as a percentage (e.g. 41.5 => 0.415x)

    ratios = {
        "trailing_pe": info.get("trailingPE"),
        "pb": info.get("priceToBook"),
        "debt_equity": de,
        "peg": peg,
        # dividendYield is already a raw percent in this yfinance version (0.47 = 0.47%),
        # unlike operatingMargins/returnOnEquity which are fractions — verified against
        # Reliance (0.47 raw vs its real-world ~0.4-0.5% yield); do not run through pct().
        "dividend_yield": info.get("dividendYield"),
        "market_cap": info.get("marketCap"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
    }

    have_financials = (
        financials is not None
        and balance_sheet is not None
        and not financials.empty
        and not balance_sheet.empty
    )
    if have_financials:
        ratios["opm"] = compute_opm(financials)
        ratios["roce"] = compute_roce(financials, balance_sheet)
        ratios["interest_coverage"] = compute_interest_coverage(financials)
        ratios["current_ratio"] = compute_current_ratio(balance_sheet)
        ratios["quick_ratio"] = compute_quick_ratio(balance_sheet)
        ratios["ev_ebitda"] = compute_ev_ebitda(info, financials)
    else:
        ratios["opm"] = pct(info.get("operatingMargins"))  # fallback only
        ratios["roce"] = None
        ratios["interest_coverage"] = None
        ratios["current_ratio"] = info.get("currentRatio")
        ratios["quick_ratio"] = info.get("quickRatio")
        ratios["ev_ebitda"] = info.get("enterpriseToEbitda")

    meta = {
        "name": info.get("longName") or info.get("shortName") or ticker_symbol,
        "sector": info.get("sector"),
        "industry": info.get("industry"),
    }
    return meta, ratios


def evaluate(ratios, thresholds):
    """Check ratios against a threshold dict. Returns (rows, passed, total)
    where rows is a list of (label, actual_str, requirement_str, verdict)."""
    rows = []
    passed = 0
    total = 0
    for key, spec in thresholds.items():
        actual = ratios.get(key)
        label, unit = spec["label"], spec["unit"]

        if spec["op"] == "range":
            requirement = f"{spec['low']}{unit} - {spec['high']}{unit}"
        elif spec["op"] == ">=":
            requirement = f">= {spec['value']}{unit}"
        else:
            requirement = f"<= {spec['value']}{unit}"

        if actual is None:
            rows.append((label, "N/A", requirement, "N/A"))
            continue

        total += 1
        if spec["op"] == "range":
            ok = spec["low"] <= actual <= spec["high"]
        elif spec["op"] == ">=":
            ok = actual >= spec["value"]
        else:
            ok = actual <= spec["value"]

        if ok:
            passed += 1
        rows.append((label, f"{actual:.2f}{unit}", requirement, "PASS" if ok else "FAIL"))

    return rows, passed, total


def fmt_market_cap(value):
    if value is None:
        return "N/A"
    if value >= 1e12:
        return f"{value / 1e12:.2f}T"
    if value >= 1e9:
        return f"{value / 1e9:.2f}B"
    return f"{value:,.0f}"
