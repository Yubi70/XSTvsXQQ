# XUT replacement research: original-method pilot

Data cutoff: **2026-11-12**. Retrieved: 2026-11-12T22:06:46.134980+00:00.

## Method

Original method: premium = (defensive ETF Close - Nasdaq Close) / Nasdaq Close * 100; thresholds +/-3% and +/-5%; start in the defensive ETF; switch only to the opposite ETF. Defensive means XUT (utilities) in the pilot and XST (consumer staples) in the reference. Earn each day's return in the previous holding, then execute at that day's close. Initial capital 10,000 in each pair's own currency; fractional shares; unrebalanced 50/50 benchmark. No dividends, fees, slippage or taxes. Signals and executions at the same close are optimistic and not guaranteed executable.

## Critical limitations

Raw share-price differences are not valuations. Share denominations and splits can dominate signals; Yahoo Close is not dividend-adjusted but is normally split-restated, not historical as-traded prices. No rebasing or reconstruction of as-traded prices is used. Zero-switch results are retained. Both XUT/XQQ and XST/XQQ use CAD prices, without FX conversion. XUT is a utilities sector fund, not a like-for-like consumer staples replacement. Correlations use daily returns, not price levels. Historical performance cannot establish the best future investment. XUT replaces the earlier XLP pilot; selecting a new fund after seeing XLP's results introduces selection bias. IYK, KXI, FSTA and VDC remain deferred.

## Results

| Pair / currency | Years | Threshold | Strategy | Return | CAGR | Max drawdown | Switches | Excess vs 50/50 (pp) |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 51.98% | 8.73% | -28.72% | 6 | +9.58 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 22.45% | 4.13% | -32.21% | 0 | -19.94 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 62.34% | 10.18% | -36.47% | 0 | +19.94 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 42.39% | 7.33% | -24.81% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 56.86% | 9.42% | -22.83% | 4 | +14.46 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 22.45% | 4.13% | -32.21% | 0 | -19.94 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 62.34% | 10.18% | -36.47% | 0 | +19.94 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 42.39% | 7.33% | -24.81% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 31.73% | 14.78% | -12.73% | 0 | +1.19 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 31.73% | 14.78% | -12.73% | 0 | +1.19 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 29.34% | 13.74% | -22.81% | 0 | -1.19 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 30.53% | 14.26% | -13.81% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 31.73% | 14.78% | -12.73% | 0 | +1.19 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 31.73% | 14.78% | -12.73% | 0 | +1.19 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 29.34% | 13.74% | -22.81% | 0 | -1.19 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 30.53% | 14.26% | -13.81% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 200.90% | 24.65% | -30.65% | 13 | +129.34 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 80.79% | 12.58% | -10.72% | 0 | +9.23 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 62.34% | 10.18% | -36.47% | 0 | -9.23 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 71.56% | 11.40% | -18.66% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 215.89% | 25.87% | -30.65% | 9 | +144.33 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 80.79% | 12.58% | -10.72% | 0 | +9.23 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 62.34% | 10.18% | -36.47% | 0 | -9.23 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 71.56% | 11.40% | -18.66% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 99.35% | 41.23% | -18.04% | 11 | +70.70 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 27.97% | 13.13% | -10.72% | 0 | -0.68 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 29.34% | 13.74% | -22.81% | 0 | +0.68 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 28.66% | 13.44% | -13.22% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 73.14% | 31.61% | -16.99% | 5 | +44.48 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 27.97% | 13.13% | -10.72% | 0 | -0.68 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 29.34% | 13.74% | -22.81% | 0 | +0.68 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 28.66% | 13.44% | -13.22% | 0 | +0.00 |

## Assessment

- 5y at +/-3%: **6 switches**, return **+51.98%**, excess vs 50/50 **+9.58 pp**.
- 5y at +/-5%: **4 switches**, return **+56.86%**, excess vs 50/50 **+14.46 pp**.
- 2y at +/-3%: **0 switches**, return **+31.73%**, excess vs 50/50 **+1.19 pp**.
- 2y at +/-5%: **0 switches**, return **+31.73%**, excess vs 50/50 **+1.19 pp**.

Assess both thresholds and windows together, including drawdown and excess returns. Any observed advantage is specific to these raw price levels and same-close assumptions; it does not establish a robust or directly executable XST replacement. Some scenarios have no switches and simply hold XUT; earlier switches do not establish ongoing switching activity. XUT switching underperforms the XST/XQQ switching reference in every tested scenario.

XUT replaces the earlier XLP pilot. Both pairs now use CAD and retain XQQ; live holdings and alerts are unchanged. Other candidates remain deferred.

## Data coverage, liquidity and return correlations

- **XUT.TO (CAD)**: 2021-11-12 to 2026-11-12; 1255 sessions; 0 missing; 30-day average volume 553,123 shares / 19,500,518 CAD traded; 90-day averages 450,551 shares / 15,892,894 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.983}].
  iShares S&P/TSX Capped Utilities Index ETF; Canadian utilities, not consumer staples; inception 2011-04-12. [Issuer](https://www.blackrock.com/ca/investors/en/literature/fact-sheet/xut-ishares-s-p-tsx-capped-utilities-index-etf-fund-fact-sheet-en-ca.pdf).
- **XST.TO (CAD)**: 2021-11-12 to 2026-11-12; 1255 sessions; 0 missing; 30-day average volume 27,004 shares / 1,815,059 CAD traded; 90-day averages 22,307 shares / 1,476,068 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.988}, {"date": "2024-08-09", "ratio": 2.0}, {"date": "2024-12-30", "ratio": 0.967}].
  Canadian consumer staples reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239840/ishares-sptsx-capped-consumer-staples-index-etf).
- **XQQ.TO (CAD)**: 2021-11-12 to 2026-11-12; 1255 sessions; 0 missing; 30-day average volume 418,418 shares / 30,181,022 CAD traded; 90-day averages 243,531 shares / 17,475,552 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.965}, {"date": "2024-08-09", "ratio": 3.0}].
  Nasdaq-100 CAD-hedged reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239698/ishares-nasdaq-100-index-etf-cadhedged-fund).
- XUT.TO/XQQ.TO, 5y: 2021-11-12 to 2026-11-12, 1255 paired sessions; return correlation 0.2515; last-year correlation -0.0477 (252 returns).
- XUT.TO/XQQ.TO, 2y: 2024-11-12 to 2026-11-12, 503 paired sessions; return correlation 0.1652; last-year correlation -0.0477 (252 returns).
- XST.TO/XQQ.TO, 5y: 2021-11-12 to 2026-11-12, 1255 paired sessions; return correlation 0.1927; last-year correlation -0.1878 (252 returns).
- XST.TO/XQQ.TO, 2y: 2024-11-12 to 2026-11-12, 503 paired sessions; return correlation -0.0380; last-year correlation -0.1878 (252 returns).

## Reproducibility

Provider: Yahoo Finance via yfinance 1.8.0; auto_adjust=False, actions=True. Each pair uses common observed sessions, without forward filling. Both pairs use CAD with the same XQQ series and cutoff; no FX conversion is applied.
CSV files preserve provider precision; Adj Close and actions are exported for audit but do not drive returns.
Manifest: [coverage and SHA-256 hashes](../src/etf_research_manifest.json). Daily data source: Yahoo Finance, accessed through yfinance. [Provider price-adjustment explanation](https://help.yahoo.com/kb/SLN28256.html).
Method reference: [original strategy document](./XST_XQQ_Switch_Strategy_v1.0_2026-04-17.docx).
Rerun: `python -m src.etf_research`. No account values, holdings or email alerts are used.
