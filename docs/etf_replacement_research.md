# XUT replacement research: original-method pilot

Data cutoff: **2026-11-05**. Retrieved: 2026-11-06T15:44:13.300869+00:00.

## Method

Original method: premium = (defensive ETF Close - Nasdaq Close) / Nasdaq Close * 100; thresholds +/-3% and +/-5%; start in the defensive ETF; switch only to the opposite ETF. Defensive means XUT (utilities) in the pilot and XST (consumer staples) in the reference. Earn each day's return in the previous holding, then execute at that day's close. Initial capital 10,000 in each pair's own currency; fractional shares; unrebalanced 50/50 benchmark. No dividends, fees, slippage or taxes. Signals and executions at the same close are optimistic and not guaranteed executable.

## Critical limitations

Raw share-price differences are not valuations. Share denominations and splits can dominate signals; Yahoo Close is not dividend-adjusted but is normally split-restated, not historical as-traded prices. No rebasing or reconstruction of as-traded prices is used. Zero-switch results are retained. Both XUT/XQQ and XST/XQQ use CAD prices, without FX conversion. XUT is a utilities sector fund, not a like-for-like consumer staples replacement. Correlations use daily returns, not price levels. Historical performance cannot establish the best future investment. XUT replaces the earlier XLP pilot; selecting a new fund after seeing XLP's results introduces selection bias. IYK, KXI, FSTA and VDC remain deferred.

## Results

| Pair / currency | Years | Threshold | Strategy | Return | CAGR | Max drawdown | Switches | Excess vs 50/50 (pp) |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 49.81% | 8.42% | -28.72% | 6 | +13.64 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 20.71% | 3.84% | -32.21% | 0 | -15.47 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 51.64% | 8.68% | -36.47% | 0 | +15.47 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 36.17% | 6.37% | -24.79% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 54.62% | 9.11% | -22.83% | 4 | +18.45 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 20.71% | 3.84% | -32.21% | 0 | -15.47 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 51.64% | 8.68% | -36.47% | 0 | +15.47 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 36.17% | 6.37% | -24.79% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 29.61% | 13.86% | -12.73% | 0 | +1.27 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 29.61% | 13.86% | -12.73% | 0 | +1.27 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 27.06% | 12.73% | -22.81% | 0 | -1.27 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 28.33% | 13.29% | -13.99% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 29.61% | 13.86% | -12.73% | 0 | +1.27 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 29.61% | 13.86% | -12.73% | 0 | +1.27 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 27.06% | 12.73% | -22.81% | 0 | -1.27 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 28.33% | 13.29% | -13.99% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 187.26% | 23.50% | -30.65% | 13 | +120.59 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 81.68% | 12.69% | -10.72% | 0 | +15.02 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 51.64% | 8.68% | -36.47% | 0 | -15.02 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 66.66% | 10.76% | -18.48% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 201.56% | 24.71% | -30.65% | 9 | +134.90 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 81.68% | 12.69% | -10.72% | 0 | +15.02 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 51.64% | 8.68% | -36.47% | 0 | -15.02 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 66.66% | 10.76% | -18.48% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 90.90% | 38.20% | -18.04% | 11 | +62.05 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 30.63% | 14.30% | -10.72% | 0 | +1.78 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 27.06% | 12.73% | -22.81% | 0 | -1.78 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 28.84% | 13.52% | -13.28% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 67.88% | 29.59% | -16.99% | 5 | +39.04 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 30.63% | 14.30% | -10.72% | 0 | +1.78 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 27.06% | 12.73% | -22.81% | 0 | -1.78 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 28.84% | 13.52% | -13.28% | 0 | +0.00 |

## Assessment

- 5y at +/-3%: **6 switches**, return **+49.81%**, excess vs 50/50 **+13.64 pp**.
- 5y at +/-5%: **4 switches**, return **+54.62%**, excess vs 50/50 **+18.45 pp**.
- 2y at +/-3%: **0 switches**, return **+29.61%**, excess vs 50/50 **+1.27 pp**.
- 2y at +/-5%: **0 switches**, return **+29.61%**, excess vs 50/50 **+1.27 pp**.

Assess both thresholds and windows together, including drawdown and excess returns. Any observed advantage is specific to these raw price levels and same-close assumptions; it does not establish a robust or directly executable XST replacement. Some scenarios have no switches and simply hold XUT; earlier switches do not establish ongoing switching activity. XUT switching underperforms the XST/XQQ switching reference in every tested scenario.

XUT replaces the earlier XLP pilot. Both pairs now use CAD and retain XQQ; live holdings and alerts are unchanged. Other candidates remain deferred.

## Data coverage, liquidity and return correlations

- **XUT.TO (CAD)**: 2021-11-05 to 2026-11-05; 1255 sessions; 0 missing; 30-day average volume 566,050 shares / 19,769,379 CAD traded; 90-day averages 443,500 shares / 15,632,781 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.983}].
  iShares S&P/TSX Capped Utilities Index ETF; Canadian utilities, not consumer staples; inception 2011-04-12. [Issuer](https://www.blackrock.com/ca/investors/en/literature/fact-sheet/xut-ishares-s-p-tsx-capped-utilities-index-etf-fund-fact-sheet-en-ca.pdf).
- **XST.TO (CAD)**: 2021-11-05 to 2026-11-05; 1255 sessions; 0 missing; 30-day average volume 25,940 shares / 1,718,268 CAD traded; 90-day averages 21,717 shares / 1,432,594 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.988}, {"date": "2024-08-09", "ratio": 2.0}, {"date": "2024-12-30", "ratio": 0.967}].
  Canadian consumer staples reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239840/ishares-sptsx-capped-consumer-staples-index-etf).
- **XQQ.TO (CAD)**: 2021-11-05 to 2026-11-05; 1255 sessions; 0 missing; 30-day average volume 406,477 shares / 29,651,789 CAD traded; 90-day averages 236,826 shares / 17,079,004 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.965}, {"date": "2024-08-09", "ratio": 3.0}].
  Nasdaq-100 CAD-hedged reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239698/ishares-nasdaq-100-index-etf-cadhedged-fund).
- XUT.TO/XQQ.TO, 5y: 2021-11-05 to 2026-11-05, 1255 paired sessions; return correlation 0.2511; last-year correlation -0.0498 (252 returns).
- XUT.TO/XQQ.TO, 2y: 2024-11-05 to 2026-11-05, 503 paired sessions; return correlation 0.1557; last-year correlation -0.0498 (252 returns).
- XST.TO/XQQ.TO, 5y: 2021-11-05 to 2026-11-05, 1255 paired sessions; return correlation 0.1922; last-year correlation -0.1790 (252 returns).
- XST.TO/XQQ.TO, 2y: 2024-11-05 to 2026-11-05, 503 paired sessions; return correlation -0.0330; last-year correlation -0.1790 (252 returns).

## Reproducibility

Provider: Yahoo Finance via yfinance 1.7.0; auto_adjust=False, actions=True. Each pair uses common observed sessions, without forward filling. Both pairs use CAD with the same XQQ series and cutoff; no FX conversion is applied.
CSV files preserve provider precision; Adj Close and actions are exported for audit but do not drive returns.
Manifest: [coverage and SHA-256 hashes](../src/etf_research_manifest.json). Daily data source: Yahoo Finance, accessed through yfinance. [Provider price-adjustment explanation](https://help.yahoo.com/kb/SLN28256.html).
Method reference: [original strategy document](./XST_XQQ_Switch_Strategy_v1.0_2026-04-17.docx).
Rerun: `python -m src.etf_research`. No account values, holdings or email alerts are used.
