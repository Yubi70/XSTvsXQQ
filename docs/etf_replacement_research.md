# XUT replacement research: original-method pilot

Data cutoff: **2026-11-16**. Retrieved: 2026-11-16T22:06:19.987663+00:00.

## Method

Original method: premium = (defensive ETF Close - Nasdaq Close) / Nasdaq Close * 100; thresholds +/-3% and +/-5%; start in the defensive ETF; switch only to the opposite ETF. Defensive means XUT (utilities) in the pilot and XST (consumer staples) in the reference. Earn each day's return in the previous holding, then execute at that day's close. Initial capital 10,000 in each pair's own currency; fractional shares; unrebalanced 50/50 benchmark. No dividends, fees, slippage or taxes. Signals and executions at the same close are optimistic and not guaranteed executable.

## Critical limitations

Raw share-price differences are not valuations. Share denominations and splits can dominate signals; Yahoo Close is not dividend-adjusted but is normally split-restated, not historical as-traded prices. No rebasing or reconstruction of as-traded prices is used. Zero-switch results are retained. Both XUT/XQQ and XST/XQQ use CAD prices, without FX conversion. XUT is a utilities sector fund, not a like-for-like consumer staples replacement. Correlations use daily returns, not price levels. Historical performance cannot establish the best future investment. XUT replaces the earlier XLP pilot; selecting a new fund after seeing XLP's results introduces selection bias. IYK, KXI, FSTA and VDC remain deferred.

## Results

| Pair / currency | Years | Threshold | Strategy | Return | CAGR | Max drawdown | Switches | Excess vs 50/50 (pp) |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 54.39% | 9.08% | -28.72% | 6 | +14.66 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 24.39% | 4.46% | -32.21% | 0 | -15.33 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 55.06% | 9.17% | -36.47% | 0 | +15.33 |
| XUT.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 39.73% | 6.92% | -24.77% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 59.34% | 9.77% | -22.83% | 4 | +19.62 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 24.39% | 4.46% | -32.21% | 0 | -15.33 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 55.06% | 9.17% | -36.47% | 0 | +15.33 |
| XUT.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 39.73% | 6.92% | -24.77% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 32.59% | 15.20% | -12.73% | 0 | +2.48 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 32.59% | 15.20% | -12.73% | 0 | +2.48 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 27.64% | 13.02% | -22.81% | 0 | -2.48 |
| XUT.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 30.11% | 14.12% | -13.94% | 0 | +0.00 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 32.59% | 15.20% | -12.73% | 0 | +2.48 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 32.59% | 15.20% | -12.73% | 0 | +2.48 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 27.64% | 13.02% | -22.81% | 0 | -2.48 |
| XUT.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 30.11% | 14.12% | -13.94% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 186.42% | 23.43% | -30.65% | 13 | +117.30 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Defensive only | 83.18% | 12.87% | -10.72% | 0 | +14.06 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 55.06% | 9.17% | -36.47% | 0 | -14.06 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 69.12% | 11.08% | -18.69% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 200.69% | 24.63% | -30.65% | 9 | +131.57 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Defensive only | 83.18% | 12.87% | -10.72% | 0 | +14.06 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 55.06% | 9.17% | -36.47% | 0 | -14.06 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 69.12% | 11.08% | -18.69% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 95.99% | 40.16% | -18.04% | 11 | +65.32 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Defensive only | 33.71% | 15.69% | -10.72% | 0 | +3.03 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 27.64% | 13.02% | -22.81% | 0 | -3.03 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 30.67% | 14.36% | -13.25% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 69.94% | 30.48% | -16.99% | 5 | +39.27 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Defensive only | 33.71% | 15.69% | -10.72% | 0 | +3.03 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 27.64% | 13.02% | -22.81% | 0 | -3.03 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 30.67% | 14.36% | -13.25% | 0 | +0.00 |

## Assessment

- 5y at +/-3%: **6 switches**, return **+54.39%**, excess vs 50/50 **+14.66 pp**.
- 5y at +/-5%: **4 switches**, return **+59.34%**, excess vs 50/50 **+19.62 pp**.
- 2y at +/-3%: **0 switches**, return **+32.59%**, excess vs 50/50 **+2.48 pp**.
- 2y at +/-5%: **0 switches**, return **+32.59%**, excess vs 50/50 **+2.48 pp**.

Assess both thresholds and windows together, including drawdown and excess returns. Any observed advantage is specific to these raw price levels and same-close assumptions; it does not establish a robust or directly executable XST replacement. Some scenarios have no switches and simply hold XUT; earlier switches do not establish ongoing switching activity. XUT switching underperforms the XST/XQQ switching reference in every tested scenario.

XUT replaces the earlier XLP pilot. Both pairs now use CAD and retain XQQ; live holdings and alerts are unchanged. Other candidates remain deferred.

## Data coverage, liquidity and return correlations

- **XUT.TO (CAD)**: 2021-11-16 to 2026-11-16; 1255 sessions; 0 missing; 30-day average volume 551,898 shares / 19,557,181 CAD traded; 90-day averages 455,999 shares / 16,097,109 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.983}].
  iShares S&P/TSX Capped Utilities Index ETF; Canadian utilities, not consumer staples; inception 2011-04-12. [Issuer](https://www.blackrock.com/ca/investors/en/literature/fact-sheet/xut-ishares-s-p-tsx-capped-utilities-index-etf-fund-fact-sheet-en-ca.pdf).
- **XST.TO (CAD)**: 2021-11-16 to 2026-11-16; 1255 sessions; 0 missing; 30-day average volume 28,030 shares / 1,893,730 CAD traded; 90-day averages 22,385 shares / 1,483,363 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.988}, {"date": "2024-08-09", "ratio": 2.0}, {"date": "2024-12-30", "ratio": 0.967}].
  Canadian consumer staples reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239840/ishares-sptsx-capped-consumer-staples-index-etf).
- **XQQ.TO (CAD)**: 2021-11-16 to 2026-11-16; 1255 sessions; 0 missing; 30-day average volume 415,822 shares / 29,839,924 CAD traded; 90-day averages 246,522 shares / 17,660,156 CAD. Provider-reported split events: [{"date": "2021-12-30", "ratio": 0.965}, {"date": "2024-08-09", "ratio": 3.0}].
  Nasdaq-100 CAD-hedged reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239698/ishares-nasdaq-100-index-etf-cadhedged-fund).
- XUT.TO/XQQ.TO, 5y: 2021-11-16 to 2026-11-16, 1255 paired sessions; return correlation 0.2491; last-year correlation -0.0745 (251 returns).
- XUT.TO/XQQ.TO, 2y: 2024-11-18 to 2026-11-16, 501 paired sessions; return correlation 0.1591; last-year correlation -0.0745 (251 returns).
- XST.TO/XQQ.TO, 5y: 2021-11-16 to 2026-11-16, 1255 paired sessions; return correlation 0.1891; last-year correlation -0.2012 (251 returns).
- XST.TO/XQQ.TO, 2y: 2024-11-18 to 2026-11-16, 501 paired sessions; return correlation -0.0453; last-year correlation -0.2012 (251 returns).

## Reproducibility

Provider: Yahoo Finance via yfinance 1.8.0; auto_adjust=False, actions=True. Each pair uses common observed sessions, without forward filling. Both pairs use CAD with the same XQQ series and cutoff; no FX conversion is applied.
CSV files preserve provider precision; Adj Close and actions are exported for audit but do not drive returns.
Manifest: [coverage and SHA-256 hashes](../src/etf_research_manifest.json). Daily data source: Yahoo Finance, accessed through yfinance. [Provider price-adjustment explanation](https://help.yahoo.com/kb/SLN28256.html).
Method reference: [original strategy document](./XST_XQQ_Switch_Strategy_v1.0_2026-04-17.docx).
Rerun: `python -m src.etf_research`. No account values, holdings or email alerts are used.
