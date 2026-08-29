# IIMC Corporate Finance Assignment — Insights

Source: `IIMC_Corporate_Finance_Assignment_Arpit_Goyal.xlsx` (Downloads), read and summarized on 2026-08-29.

The workbook builds a sector-specific "Master Ratio Matrix" (liquidity / solvency / activity / profitability / valuation thresholds calibrated per sector) and then screens real peer sets from Screener.in against those thresholds across five sectors: **Aerospace & Defence, Capital Markets, E-Retail & E-Commerce, 2-3 Wheelers, and Civil Construction.**

## Overall Approach — What's Strong

- **Sector-relative thresholds, not one-size-fits-all.** Current Ratio floor ranges from >1.0x (Capital Markets, asset-light) to >1.6x (Civil Construction, long WIP cycles) to >2.0x (Aerospace, government billing delays). This is the right instinct — a blanket ratio screen would misjudge structurally different business models.
- **Willingness to recalibrate mid-analysis.** In Capital Markets, the first pass at Current Ratio >1.5x failed 13/25 names including elite-ROCE companies (SBI Funds Mgt: 81.5% OPM, 56.5% ROCE, failed only on a 0.92 current ratio). The assignment explicitly re-ran with a lower, sector-appropriate bar (>1.0x) rather than mechanically rejecting strong businesses — good analytical judgment.
- **Flagging threshold edge cases instead of hiding them.** Hero MotoCorp (2/3 Wheelers) is called out as failing purely on Current/Quick Ratio despite ROCE 35.2%, ROE 28.1%, Interest Coverage 94x — with an explicit note that mature 2W majors run tight/negative working capital by design, so the miss may be a screen miscalibration rather than real weakness. Same treatment for SBI Funds Mgt, CDSL, Macfos, Womancart, G R Infraprojects, Welspun Enterprises.

## Sector-by-Sector Highlights

| Sector | Passed / Universe sampled | Top pick | Notable near-misses |
|---|---|---|---|
| Aerospace & Defence | 5 of 25 (33 total) | Hindustan Aeronautics (D/E 0, Int Cov 2130x, ROCE 32%) | Bharat Dynamics, Zen Technologies, Paras Defence — miss on OPM/ROCE only |
| Capital Markets | 10 of 25 (72 total, recalibrated) | BSE (OPM 64%, ROCE 60%, PEG 0.39) | SBI Funds Mgt, CDSL — miss only on Current Ratio |
| E-Retail & E-Commerce | 2 of 20 (full universe) | Cartrade Tech | Macfos, Womancart — miss only on Debt/Equity |
| 2-3 Wheelers | 1 of 13 (full universe) | Eicher Motors (only company to clear every gate) | Hero MotoCorp — misses only on liquidity, arguably miscalibrated |
| Civil Construction | 6 of 25 (175 total) | Central Mine Planning, Engineers India, Techno Electric | Kalpataru, G R Infra, Welspun — single-metric misses |

## Cross-Sector Observations

1. **Pass rates track business-model maturity, not sector "quality."** E-Commerce (2/20) and 2-3 Wheelers (1/13) have the lowest hit rates — one because the sector is still loss-making and consolidating, the other because only a handful of legacy OEMs have decades of disciplined capital allocation. Aerospace and Capital Markets clear at much higher rates once thresholds are correctly calibrated to the business model.
2. **PEG ratios stay well under 1.5x for nearly every "Passed" name** across sectors (e.g., HAL 2.19 is actually the outlier on the higher side; BSE 0.39, Cartrade 0.69, Eicher 1.58) — suggesting the screen is doing real work filtering out names where growth doesn't justify the multiple, not just picking whatever is popular.
3. **Civil Construction is the only sector where meaningful leverage (D/E < 1.0x) is treated as normal** rather than a red flag — correctly reflecting that EPC/construction economics require equipment and working-capital debt, unlike the asset-light or cash-rich sectors in the same workbook.
4. **Sample coverage varies a lot and matters for interpretation.** Aerospace, Capital Markets, and Civil Construction only screen the top slice by market cap (25 of 33, 72, and 175 companies respectively) — the "Passed" lists are large-cap-biased and don't reflect the full universe, which the workbook itself flags for Civil Construction ("small, large-cap-biased slice of a much bigger universe").
5. **Cross-sector "best in class" by pure numbers:** BSE (Capital Markets) and Hindustan Aeronautics (Aerospace) stand out for near-zero debt combined with >30% ROCE and reasonable PEG — the two strongest risk-adjusted profiles across all five sectors.

## Possible Gaps / Questions for Follow-Up

- No explicit weighting or composite score across categories — the screen is pass/fail per threshold, so a name that fails one ratio narrowly (e.g., Welspun Enterprises, G R Infraprojects, CDSL) is bucketed identically to one that fails badly. A "near-miss" tier is implicitly discussed in prose but not formalized as a rank.
- Valuation checks (P/E vs. 5-yr median, EV/EBITDA vs. historical median) are defined in the Master Ratio Matrix but the actual expanded screener tables mostly report current P/E and EV/EBITDA rather than the 5-yr median comparison — worth confirming these were checked qualitatively vs. quantitatively in the write-up.
- Only Aerospace and Capital Markets sheets define Dividend Yield / P/B as additional valuation lenses; these aren't carried through to the other three sectors even though they could matter (e.g., Civil Construction PSU names).
