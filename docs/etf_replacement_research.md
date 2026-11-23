# XUT replacement research: original-method pilot

Data cutoff: **2026-11-23**. Retrieved: 2026-11-23T22:06:03.826054+00:00.

## Method

Original method: premium = (defensive ETF Close - Nasdaq Close) / Nasdaq Close * 100; thresholds +/-3% and +/-5%; start in the defensive ETF; switch only to the opposite ETF. Defensive means XUT (utilities) in the pilot and XST (consumer staples) in the reference. Earn each day's return in the previous holding, then execute at that day's close. Initial capital 10,000 in each pair's own currency; fractional shares; unrebalanced 50/50 benchmark. No dividends, fees, slippage or taxes. Signals and executions at the same close are optimistic and not guaranteed executable.

## Critical limitations

Raw share-price differences are not valuations. Share denominations and splits can dominate signals; Yahoo Close is not dividend-adjusted but is normally split-restated, not historical as-traded prices. No rebasing or reconstruction of as-traded prices is used. Zero-switch results are retained. Both XUT/XQQ and XST/XQQ use CAD prices, without FX conversion. XUT is a utilities sector fund, not a like-for-like consumer staples replacement. Correlations use daily returns, not price levels. Historical performance cannot establish the best future investment. XUT replaces the earlier XLP pilot; selecting a new fund after seeing XLP's results introduces selection bias. IYK, KXI, FSTA and VDC remain deferred.

## Results

| Pair / currency | Years | Threshold | Strategy | Return | CAGR | Max drawdown | Switches | Excess vs 50/50 (pp) |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 56.60% | 9.39% | -28.72% | 6 | +17.63 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 26.18% | 4.76% | -32.21% | 0 | -12.79 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 51.76% | 8.70% | -36.08% | 0 | +12.79 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 38.97% | 6.80% | -24.74% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 61.63% | 10.08% | -22.83% | 4 | +22.66 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 26.18% | 4.76% | -32.21% | 0 | -12.79 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 51.76% | 8.70% | -36.08% | 0 | +12.79 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 38.97% | 6.80% | -24.74% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 31.90% | 14.90% | -12.73% | 0 | +4.26 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 31.90% | 14.90% | -12.73% | 0 | +4.26 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 23.38% | 11.11% | -22.81% | 0 | -4.26 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 27.64% | 13.02% | -13.94% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 31.90% | 14.90% | -12.73% | 0 | +4.26 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 31.90% | 14.90% | -12.73% | 0 | +4.26 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 23.38% | 11.11% | -22.81% | 0 | -4.26 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 27.64% | 13.02% | -13.94% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 188.90% | 23.64% | -30.65% | 13 | +119.37 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 87.30% | 13.37% | -10.72% | 0 | +17.77 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 51.76% | 8.70% | -36.08% | 0 | -17.77 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 69.53% | 11.14% | -18.43% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 203.29% | 24.85% | -30.65% | 9 | +133.76 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 87.30% | 13.37% | -10.72% | 0 | +17.77 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 51.76% | 8.70% | -36.08% | 0 | -17.77 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 69.53% | 11.14% | -18.43% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 90.93% | 38.33% | -18.04% | 11 | +63.22 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 32.04% | 14.96% | -10.72% | 0 | +4.33 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 23.38% | 11.11% | -22.81% | 0 | -4.33 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 27.71% | 13.05% | -13.21% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 65.55% | 28.78% | -16.99% | 5 | +37.85 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 32.04% | 14.96% | -10.72% | 0 | +4.33 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 23.38% | 11.11% | -22.81% | 0 | -4.33 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 27.71% | 13.05% | -13.21% | 0 | +0.00 |

## Assessment

- 5y at +/-3%: **6 switches**, return **+56.60%**, excess vs 50/50 **+17.63 pp**.
- 5y at +/-5%: **4 switches**, return **+61.63%**, excess vs 50/50 **+22.66 pp**.
- 2y at +/-3%: **0 switches**, return **+31.90%**, excess vs 50/50 **+4.26 pp**.
- 2y at +/-5%: **0 switches**, return **+31.90%**, excess vs 50/50 **+4.26 pp**.

Assess both thresholds and windows together, including drawdown and excess returns. Any observed advantage is specific to these raw price levels and same-close assumptions; it does not establish a robust or directly executable XST replacement. Some scenarios have no switches and simply hold XUT; earlier switches do not establish ongoing switching activity. XUT switching underperforms the XST/XQQ switching reference in every tested scenario.

XUT replaces the earlier XLP pilot. Both pairs now use CAD and retain XQQ; live holdings and alerts are unchanged. Other candidates remain deferred.

## Data coverage, liquidity and return correlations

- **XUT.TO (CAD)**: 2021-11-23 to 2026-11-23; 1255 sessions; 0 missing; 30-day average volume 594,374 shares / 21,466,177 CAD traded; 90-day averages 489,554 shares / 17,366,356 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.983}].
  iShares S&P/TSX Capped Utilities Index ETF; Canadian utilities, not consumer staples; inception 2011-04-12. [Issuer](https://www.blackrock.com/ca/investors/en/literature/fact-sheet/xut-ishares-s-p-tsx-capped-utilities-index-etf-fund-fact-sheet-en-ca.pdf).
- **XST.TO (CAD)**: 2021-11-23 to 2026-11-23; 1255 sessions; 0 missing; 30-day average volume 47,412 shares / 3,264,311 CAD traded; 90-day averages 29,252 shares / 1,963,308 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.988}, {"date": "2024-08-09", "ratio": 2.0}, {"date": "2024-12-30", "ratio": 0.967}].
  Canadian consumer staples reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239840/ishares-sptsx-capped-consumer-staples-index-etf).
- **XQQ.TO (CAD)**: 2021-11-23 to 2026-11-23; 1255 sessions; 0 missing; 30-day average volume 356,469 shares / 23,841,149 CAD traded; 90-day averages 277,195 shares / 19,516,191 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.965}, {"date": "2024-08-09", "ratio": 3.0}].
  Nasdaq-100 CAD-hedged reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239698/ishares-nasdaq-100-index-etf-cadhedged-fund).
- XUT.TO/XQQ.TO, 5y: 2021-11-23 to 2026-11-23, 1255 paired sessions; return correlation 0.2447; last-year correlation -0.0775 (251 returns).
- XUT.TO/XQQ.TO, 2y: 2024-11-25 to 2026-11-23, 501 paired sessions; return correlation 0.1513; last-year correlation -0.0775 (251 returns).
- XST.TO/XQQ.TO, 5y: 2021-11-23 to 2026-11-23, 1255 paired sessions; return correlation 0.1877; last-year correlation -0.1782 (251 returns).
- XST.TO/XQQ.TO, 2y: 2024-11-25 to 2026-11-23, 501 paired sessions; return correlation -0.0391; last-year correlation -0.1782 (251 returns).

## Reproducibility

Provider: Yahoo Finance via yfinance 1.8.0; auto_adjust=False, actions=True. Each pair uses common observed sessions, without forward filling. Both pairs use CAD with the same XQQ series and cutoff; no FX conversion is applied.
CSV files preserve provider precision; Adj Close and actions are exported for audit but do not drive returns.
Manifest: [coverage and SHA-256 hashes](../src/etf_research_manifest.json). Daily data source: Yahoo Finance, accessed through yfinance. [Provider price-adjustment explanation](https://help.yahoo.com/kb/SLN28256.html).
Method reference: [original strategy document](./XST_XQQ_Switch_Strategy_v1.0_2026-04-17.docx).
Rerun: `python -m src.etf_research`. No account values, holdings or email alerts are used.
