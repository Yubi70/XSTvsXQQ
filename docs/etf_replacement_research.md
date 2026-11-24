# XUT replacement research: original-method pilot

Data cutoff: **2026-11-24**. Retrieved: 2026-11-24T22:06:25.187228+00:00.

## Method

Original method: premium = (defensive ETF Close - Nasdaq Close) / Nasdaq Close * 100; thresholds +/-3% and +/-5%; start in the defensive ETF; switch only to the opposite ETF. Defensive means XUT (utilities) in the pilot and XST (consumer staples) in the reference. Earn each day's return in the previous holding, then execute at that day's close. Initial capital 10,000 in each pair's own currency; fractional shares; unrebalanced 50/50 benchmark. No dividends, fees, slippage or taxes. Signals and executions at the same close are optimistic and not guaranteed executable.

## Critical limitations

Raw share-price differences are not valuations. Share denominations and splits can dominate signals; Yahoo Close is not dividend-adjusted but is normally split-restated, not historical as-traded prices. No rebasing or reconstruction of as-traded prices is used. Zero-switch results are retained. Both XUT/XQQ and XST/XQQ use CAD prices, without FX conversion. XUT is a utilities sector fund, not a like-for-like consumer staples replacement. Correlations use daily returns, not price levels. Historical performance cannot establish the best future investment. XUT replaces the earlier XLP pilot; selecting a new fund after seeing XLP's results introduces selection bias. IYK, KXI, FSTA and VDC remain deferred.

## Results

| Pair / currency | Years | Threshold | Strategy | Return | CAGR | Max drawdown | Switches | Excess vs 50/50 (pp) |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 58.17% | 9.61% | -28.72% | 6 | +20.20 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 27.44% | 4.97% | -32.21% | 0 | -10.53 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 48.51% | 8.23% | -36.08% | 0 | +10.53 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 37.98% | 6.65% | -24.71% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 63.25% | 10.30% | -22.83% | 4 | +25.27 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 27.44% | 4.97% | -32.21% | 0 | -10.53 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 48.51% | 8.23% | -36.08% | 0 | +10.53 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 37.98% | 6.65% | -24.71% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 32.91% | 15.32% | -12.73% | 0 | +5.88 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 32.91% | 15.32% | -12.73% | 0 | +5.88 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 21.16% | 10.09% | -22.81% | 0 | -5.88 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 27.04% | 12.74% | -13.94% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 32.91% | 15.32% | -12.73% | 0 | +5.88 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 32.91% | 15.32% | -12.73% | 0 | +5.88 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 21.16% | 10.09% | -22.81% | 0 | -5.88 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 27.04% | 12.74% | -13.94% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 187.98% | 23.56% | -30.65% | 13 | +117.39 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 92.66% | 14.02% | -10.72% | 0 | +22.07 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 48.51% | 8.23% | -36.08% | 0 | -22.07 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 70.59% | 11.27% | -18.28% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 202.32% | 24.77% | -30.65% | 9 | +131.73 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 92.66% | 14.02% | -10.72% | 0 | +22.07 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 48.51% | 8.23% | -36.08% | 0 | -22.07 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 70.59% | 11.27% | -18.28% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 87.50% | 37.02% | -18.04% | 11 | +60.02 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 33.80% | 15.71% | -10.72% | 0 | +6.32 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 21.16% | 10.09% | -22.81% | 0 | -6.32 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 27.48% | 12.94% | -13.21% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 62.58% | 27.57% | -16.99% | 5 | +35.10 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 33.80% | 15.71% | -10.72% | 0 | +6.32 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 21.16% | 10.09% | -22.81% | 0 | -6.32 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 27.48% | 12.94% | -13.21% | 0 | +0.00 |

## Assessment

- 5y at +/-3%: **6 switches**, return **+58.17%**, excess vs 50/50 **+20.20 pp**.
- 5y at +/-5%: **4 switches**, return **+63.25%**, excess vs 50/50 **+25.27 pp**.
- 2y at +/-3%: **0 switches**, return **+32.91%**, excess vs 50/50 **+5.88 pp**.
- 2y at +/-5%: **0 switches**, return **+32.91%**, excess vs 50/50 **+5.88 pp**.

Assess both thresholds and windows together, including drawdown and excess returns. Any observed advantage is specific to these raw price levels and same-close assumptions; it does not establish a robust or directly executable XST replacement. Some scenarios have no switches and simply hold XUT; earlier switches do not establish ongoing switching activity. XUT switching underperforms the XST/XQQ switching reference in every tested scenario.

XUT replaces the earlier XLP pilot. Both pairs now use CAD and retain XQQ; live holdings and alerts are unchanged. Other candidates remain deferred.

## Data coverage, liquidity and return correlations

- **XUT.TO (CAD)**: 2021-11-24 to 2026-11-24; 1255 sessions; 0 missing; 30-day average volume 591,424 shares / 21,437,594 CAD traded; 90-day averages 494,704 shares / 17,563,832 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.983}].
  iShares S&P/TSX Capped Utilities Index ETF; Canadian utilities, not consumer staples; inception 2011-04-12. [Issuer](https://www.blackrock.com/ca/investors/en/literature/fact-sheet/xut-ishares-s-p-tsx-capped-utilities-index-etf-fund-fact-sheet-en-ca.pdf).
- **XST.TO (CAD)**: 2021-11-24 to 2026-11-24; 1255 sessions; 0 missing; 30-day average volume 49,945 shares / 3,450,562 CAD traded; 90-day averages 30,227 shares / 2,033,176 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.988}, {"date": "2024-08-09", "ratio": 2.0}, {"date": "2024-12-30", "ratio": 0.967}].
  Canadian consumer staples reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239840/ishares-sptsx-capped-consumer-staples-index-etf).
- **XQQ.TO (CAD)**: 2021-11-24 to 2026-11-24; 1255 sessions; 0 missing; 30-day average volume 366,854 shares / 24,422,916 CAD traded; 90-day averages 281,356 shares / 19,767,871 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.965}, {"date": "2024-08-09", "ratio": 3.0}].
  Nasdaq-100 CAD-hedged reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239698/ishares-nasdaq-100-index-etf-cadhedged-fund).
- XUT.TO/XQQ.TO, 5y: 2021-11-24 to 2026-11-24, 1255 paired sessions; return correlation 0.2437; last-year correlation -0.0824 (252 returns).
- XUT.TO/XQQ.TO, 2y: 2024-11-25 to 2026-11-24, 502 paired sessions; return correlation 0.1482; last-year correlation -0.0824 (252 returns).
- XST.TO/XQQ.TO, 5y: 2021-11-24 to 2026-11-24, 1255 paired sessions; return correlation 0.1866; last-year correlation -0.1830 (252 returns).
- XST.TO/XQQ.TO, 2y: 2024-11-25 to 2026-11-24, 502 paired sessions; return correlation -0.0420; last-year correlation -0.1830 (252 returns).

## Reproducibility

Provider: Yahoo Finance via yfinance 1.8.0; auto_adjust=False, actions=True. Each pair uses common observed sessions, without forward filling. Both pairs use CAD with the same XQQ series and cutoff; no FX conversion is applied.
CSV files preserve provider precision; Adj Close and actions are exported for audit but do not drive returns.
Manifest: [coverage and SHA-256 hashes](../src/etf_research_manifest.json). Daily data source: Yahoo Finance, accessed through yfinance. [Provider price-adjustment explanation](https://help.yahoo.com/kb/SLN28256.html).
Method reference: [original strategy document](./XST_XQQ_Switch_Strategy_v1.0_2026-04-17.docx).
Rerun: `python -m src.etf_research`. No account values, holdings or email alerts are used.
