# XUT replacement research: original-method pilot

Data cutoff: **2026-11-19**. Retrieved: 2026-11-19T22:06:44.211810+00:00.

## Method

Original method: premium = (defensive ETF Close - Nasdaq Close) / Nasdaq Close * 100; thresholds +/-3% and +/-5%; start in the defensive ETF; switch only to the opposite ETF. Defensive means XUT (utilities) in the pilot and XST (consumer staples) in the reference. Earn each day's return in the previous holding, then execute at that day's close. Initial capital 10,000 in each pair's own currency; fractional shares; unrebalanced 50/50 benchmark. No dividends, fees, slippage or taxes. Signals and executions at the same close are optimistic and not guaranteed executable.

## Critical limitations

Raw share-price differences are not valuations. Share denominations and splits can dominate signals; Yahoo Close is not dividend-adjusted but is normally split-restated, not historical as-traded prices. No rebasing or reconstruction of as-traded prices is used. Zero-switch results are retained. Both XUT/XQQ and XST/XQQ use CAD prices, without FX conversion. XUT is a utilities sector fund, not a like-for-like consumer staples replacement. Correlations use daily returns, not price levels. Historical performance cannot establish the best future investment. XUT replaces the earlier XLP pilot; selecting a new fund after seeing XLP's results introduces selection bias. IYK, KXI, FSTA and VDC remain deferred.

## Results

| Pair / currency | Years | Threshold | Strategy | Return | CAGR | Max drawdown | Switches | Excess vs 50/50 (pp) |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 53.22% | 8.91% | -28.72% | 6 | +17.31 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 23.45% | 4.30% | -32.21% | 0 | -12.46 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 48.36% | 8.21% | -36.47% | 0 | +12.46 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 35.90% | 6.33% | -24.71% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 58.13% | 9.60% | -22.83% | 4 | +22.23 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 23.45% | 4.30% | -32.21% | 0 | -12.46 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 48.36% | 8.21% | -36.47% | 0 | +12.46 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 35.90% | 6.33% | -24.71% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 31.76% | 14.80% | -12.73% | 0 | +4.18 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 31.76% | 14.80% | -12.73% | 0 | +4.18 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 23.39% | 11.09% | -22.81% | 0 | -4.18 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 27.57% | 12.96% | -13.93% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 31.76% | 14.80% | -12.73% | 0 | +4.18 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 31.76% | 14.80% | -12.73% | 0 | +4.18 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 23.39% | 11.09% | -22.81% | 0 | -4.18 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 27.57% | 12.96% | -13.93% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 184.38% | 23.25% | -30.65% | 13 | +119.27 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 81.87% | 12.71% | -10.72% | 0 | +16.76 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 48.36% | 8.21% | -36.47% | 0 | -16.76 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 65.11% | 10.55% | -18.38% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 198.55% | 24.46% | -30.65% | 9 | +133.43 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 81.87% | 12.71% | -10.72% | 0 | +16.76 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 48.36% | 8.21% | -36.47% | 0 | -16.76 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 65.11% | 10.55% | -18.38% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 92.57% | 38.80% | -18.04% | 11 | +65.19 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 31.37% | 14.63% | -10.72% | 0 | +3.99 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 23.39% | 11.09% | -22.81% | 0 | -3.99 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 27.38% | 12.87% | -13.17% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 66.98% | 29.24% | -16.99% | 5 | +39.60 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 31.37% | 14.63% | -10.72% | 0 | +3.99 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 23.39% | 11.09% | -22.81% | 0 | -3.99 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 27.38% | 12.87% | -13.17% | 0 | +0.00 |

## Assessment

- 5y at +/-3%: **6 switches**, return **+53.22%**, excess vs 50/50 **+17.31 pp**.
- 5y at +/-5%: **4 switches**, return **+58.13%**, excess vs 50/50 **+22.23 pp**.
- 2y at +/-3%: **0 switches**, return **+31.76%**, excess vs 50/50 **+4.18 pp**.
- 2y at +/-5%: **0 switches**, return **+31.76%**, excess vs 50/50 **+4.18 pp**.

Assess both thresholds and windows together, including drawdown and excess returns. Any observed advantage is specific to these raw price levels and same-close assumptions; it does not establish a robust or directly executable XST replacement. Some scenarios have no switches and simply hold XUT; earlier switches do not establish ongoing switching activity. XUT switching underperforms the XST/XQQ switching reference in every tested scenario.

XUT replaces the earlier XLP pilot. Both pairs now use CAD and retain XQQ; live holdings and alerts are unchanged. Other candidates remain deferred.

## Data coverage, liquidity and return correlations

- **XUT.TO (CAD)**: 2021-11-19 to 2026-11-19; 1255 sessions; 0 missing; 30-day average volume 546,987 shares / 19,570,744 CAD traded; 90-day averages 473,178 shares / 16,741,837 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.983}].
  iShares S&P/TSX Capped Utilities Index ETF; Canadian utilities, not consumer staples; inception 2011-04-12. [Issuer](https://www.blackrock.com/ca/investors/en/literature/fact-sheet/xut-ishares-s-p-tsx-capped-utilities-index-etf-fund-fact-sheet-en-ca.pdf).
- **XST.TO (CAD)**: 2021-11-19 to 2026-11-19; 1255 sessions; 0 missing; 30-day average volume 36,972 shares / 2,527,012 CAD traded; 90-day averages 25,601 shares / 1,707,647 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.988}, {"date": "2024-08-09", "ratio": 2.0}, {"date": "2024-12-30", "ratio": 0.967}].
  Canadian consumer staples reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239840/ishares-sptsx-capped-consumer-staples-index-etf).
- **XQQ.TO (CAD)**: 2021-11-19 to 2026-11-19; 1255 sessions; 0 missing; 30-day average volume 307,015 shares / 21,006,025 CAD traded; 90-day averages 258,642 shares / 18,405,124 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.965}, {"date": "2024-08-09", "ratio": 3.0}].
  Nasdaq-100 CAD-hedged reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239698/ishares-nasdaq-100-index-etf-cadhedged-fund).
- XUT.TO/XQQ.TO, 5y: 2021-11-19 to 2026-11-19, 1255 paired sessions; return correlation 0.2495; last-year correlation -0.0713 (252 returns).
- XUT.TO/XQQ.TO, 2y: 2024-11-19 to 2026-11-19, 503 paired sessions; return correlation 0.1605; last-year correlation -0.0713 (252 returns).
- XST.TO/XQQ.TO, 5y: 2021-11-19 to 2026-11-19, 1255 paired sessions; return correlation 0.1911; last-year correlation -0.1924 (252 returns).
- XST.TO/XQQ.TO, 2y: 2024-11-19 to 2026-11-19, 503 paired sessions; return correlation -0.0401; last-year correlation -0.1924 (252 returns).

## Reproducibility

Provider: Yahoo Finance via yfinance 1.8.0; auto_adjust=False, actions=True. Each pair uses common observed sessions, without forward filling. Both pairs use CAD with the same XQQ series and cutoff; no FX conversion is applied.
CSV files preserve provider precision; Adj Close and actions are exported for audit but do not drive returns.
Manifest: [coverage and SHA-256 hashes](../src/etf_research_manifest.json). Daily data source: Yahoo Finance, accessed through yfinance. [Provider price-adjustment explanation](https://help.yahoo.com/kb/SLN28256.html).
Method reference: [original strategy document](./XST_XQQ_Switch_Strategy_v1.0_2026-04-17.docx).
Rerun: `python -m src.etf_research`. No account values, holdings or email alerts are used.
