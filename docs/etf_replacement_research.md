# XUT replacement research: original-method pilot

Data cutoff: **2026-11-10**. Retrieved: 2026-11-10T22:06:56.602573+00:00.

## Method

Original method: premium = (defensive ETF Close - Nasdaq Close) / Nasdaq Close * 100; thresholds +/-3% and +/-5%; start in the defensive ETF; switch only to the opposite ETF. Defensive means XUT (utilities) in the pilot and XST (consumer staples) in the reference. Earn each day's return in the previous holding, then execute at that day's close. Initial capital 10,000 in each pair's own currency; fractional shares; unrebalanced 50/50 benchmark. No dividends, fees, slippage or taxes. Signals and executions at the same close are optimistic and not guaranteed executable.

## Critical limitations

Raw share-price differences are not valuations. Share denominations and splits can dominate signals; Yahoo Close is not dividend-adjusted but is normally split-restated, not historical as-traded prices. No rebasing or reconstruction of as-traded prices is used. Zero-switch results are retained. Both XUT/XQQ and XST/XQQ use CAD prices, without FX conversion. XUT is a utilities sector fund, not a like-for-like consumer staples replacement. Correlations use daily returns, not price levels. Historical performance cannot establish the best future investment. XUT replaces the earlier XLP pilot; selecting a new fund after seeing XLP's results introduces selection bias. IYK, KXI, FSTA and VDC remain deferred.

## Results

| Pair / currency | Years | Threshold | Strategy | Return | CAGR | Max drawdown | Switches | Excess vs 50/50 (pp) |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 50.85% | 8.57% | -28.72% | 6 | +9.44 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 21.54% | 3.98% | -32.21% | 0 | -19.87 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 61.27% | 10.03% | -36.47% | 0 | +19.87 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 41.41% | 7.18% | -24.93% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 55.69% | 9.26% | -22.83% | 4 | +14.28 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 21.54% | 3.98% | -32.21% | 0 | -19.87 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 61.27% | 10.03% | -36.47% | 0 | +19.87 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 41.41% | 7.18% | -24.93% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 31.41% | 14.67% | -12.73% | 0 | +2.38 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 31.41% | 14.67% | -12.73% | 0 | +2.38 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 26.65% | 12.57% | -22.81% | 0 | -2.38 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 29.03% | 13.62% | -13.82% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 31.41% | 14.67% | -12.73% | 0 | +2.38 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 31.41% | 14.67% | -12.73% | 0 | +2.38 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 26.65% | 12.57% | -22.81% | 0 | -2.38 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 29.03% | 13.62% | -13.82% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 195.54% | 24.20% | -30.65% | 13 | +124.95 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 79.90% | 12.46% | -10.72% | 0 | +9.31 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 61.27% | 10.03% | -36.47% | 0 | -9.31 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 70.59% | 11.27% | -18.75% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 210.26% | 25.42% | -30.65% | 9 | +139.67 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 79.90% | 12.46% | -10.72% | 0 | +9.31 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 61.27% | 10.03% | -36.47% | 0 | -9.31 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 70.59% | 11.27% | -18.75% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 97.33% | 40.57% | -18.04% | 11 | +69.84 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 28.34% | 13.32% | -10.72% | 0 | +0.84 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 26.65% | 12.57% | -22.81% | 0 | -0.84 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 27.50% | 12.94% | -13.17% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 71.39% | 30.99% | -16.99% | 5 | +43.89 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 28.34% | 13.32% | -10.72% | 0 | +0.84 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 26.65% | 12.57% | -22.81% | 0 | -0.84 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 27.50% | 12.94% | -13.17% | 0 | +0.00 |

## Assessment

- 5y at +/-3%: **6 switches**, return **+50.85%**, excess vs 50/50 **+9.44 pp**.
- 5y at +/-5%: **4 switches**, return **+55.69%**, excess vs 50/50 **+14.28 pp**.
- 2y at +/-3%: **0 switches**, return **+31.41%**, excess vs 50/50 **+2.38 pp**.
- 2y at +/-5%: **0 switches**, return **+31.41%**, excess vs 50/50 **+2.38 pp**.

Assess both thresholds and windows together, including drawdown and excess returns. Any observed advantage is specific to these raw price levels and same-close assumptions; it does not establish a robust or directly executable XST replacement. Some scenarios have no switches and simply hold XUT; earlier switches do not establish ongoing switching activity. XUT switching underperforms the XST/XQQ switching reference in every tested scenario.

XUT replaces the earlier XLP pilot. Both pairs now use CAD and retain XQQ; live holdings and alerts are unchanged. Other candidates remain deferred.

## Data coverage, liquidity and return correlations

- **XUT.TO (CAD)**: 2021-11-10 to 2026-11-10; 1255 sessions; 0 missing; 30-day average volume 566,119 shares / 19,892,501 CAD traded; 90-day averages 449,945 shares / 15,869,242 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.983}].
  iShares S&P/TSX Capped Utilities Index ETF; Canadian utilities, not consumer staples; inception 2011-04-12. [Issuer](https://www.blackrock.com/ca/investors/en/literature/fact-sheet/xut-ishares-s-p-tsx-capped-utilities-index-etf-fund-fact-sheet-en-ca.pdf).
- **XST.TO (CAD)**: 2021-11-10 to 2026-11-10; 1255 sessions; 0 missing; 30-day average volume 26,002 shares / 1,739,625 CAD traded; 90-day averages 22,127 shares / 1,462,123 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.988}, {"date": "2024-08-09", "ratio": 2.0}, {"date": "2024-12-30", "ratio": 0.967}].
  Canadian consumer staples reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239840/ishares-sptsx-capped-consumer-staples-index-etf).
- **XQQ.TO (CAD)**: 2021-11-10 to 2026-11-10; 1255 sessions; 0 missing; 30-day average volume 417,424 shares / 30,189,570 CAD traded; 90-day averages 240,851 shares / 17,301,232 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.965}, {"date": "2024-08-09", "ratio": 3.0}].
  Nasdaq-100 CAD-hedged reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239698/ishares-nasdaq-100-index-etf-cadhedged-fund).
- XUT.TO/XQQ.TO, 5y: 2021-11-10 to 2026-11-10, 1255 paired sessions; return correlation 0.2511; last-year correlation -0.0467 (252 returns).
- XUT.TO/XQQ.TO, 2y: 2024-11-11 to 2026-11-10, 502 paired sessions; return correlation 0.1649; last-year correlation -0.0467 (252 returns).
- XST.TO/XQQ.TO, 5y: 2021-11-10 to 2026-11-10, 1255 paired sessions; return correlation 0.1928; last-year correlation -0.1861 (252 returns).
- XST.TO/XQQ.TO, 2y: 2024-11-11 to 2026-11-10, 502 paired sessions; return correlation -0.0386; last-year correlation -0.1861 (252 returns).

## Reproducibility

Provider: Yahoo Finance via yfinance 1.8.0; auto_adjust=False, actions=True. Each pair uses common observed sessions, without forward filling. Both pairs use CAD with the same XQQ series and cutoff; no FX conversion is applied.
CSV files preserve provider precision; Adj Close and actions are exported for audit but do not drive returns.
Manifest: [coverage and SHA-256 hashes](../src/etf_research_manifest.json). Daily data source: Yahoo Finance, accessed through yfinance. [Provider price-adjustment explanation](https://help.yahoo.com/kb/SLN28256.html).
Method reference: [original strategy document](./XST_XQQ_Switch_Strategy_v1.0_2026-04-17.docx).
Rerun: `python -m src.etf_research`. No account values, holdings or email alerts are used.
