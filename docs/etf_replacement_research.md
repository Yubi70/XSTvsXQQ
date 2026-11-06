# XLP replacement research: original-method pilot

Data cutoff: **2026-11-05**. Retrieved: 2026-11-06T12:34:49.547344+00:00.

## Method

Original method: premium = (staples Close - Nasdaq Close) / Nasdaq Close * 100; thresholds +/-3% and +/-5%; start in staples; switch only to the opposite ETF. Earn each day's return in the previous holding, then execute at that day's close. Initial capital 10,000 in each pair's own currency; fractional shares; unrebalanced 50/50 benchmark. No dividends, fees, slippage or taxes. Signals and executions at the same close are optimistic and not guaranteed executable.

## Critical limitations

Raw share-price differences are not valuations. Share denominations and splits can dominate signals; Yahoo Close is not dividend-adjusted but is normally split-restated, not historical as-traded prices. No rebasing or reconstruction of as-traded prices is used. Zero-switch results are retained. USD XLP/QQQ does not test XLP against CAD-hedged XQQ; USD and CAD dollar results are separate. Correlations use daily returns, not price levels. Historical performance cannot establish the best future investment. Only XLP is analyzed; IYK, KXI, FSTA and VDC are deferred.

## Results

| Pair / currency | Years | Threshold | Strategy | Return | CAGR | Max drawdown | Switches | Excess vs 50/50 (pp) |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| XLP/QQQ (USD) | 5 | 3% | Switching | 25.00% | 4.56% | -17.81% | 0 | -18.67 |
| XLP/QQQ (USD) | 5 | 3% | Staples only | 25.00% | 4.56% | -17.81% | 0 | -18.67 |
| XLP/QQQ (USD) | 5 | 3% | Nasdaq only | 62.33% | 10.18% | -35.62% | 0 | +18.67 |
| XLP/QQQ (USD) | 5 | 3% | 50/50 | 43.67% | 7.52% | -23.48% | 0 | +0.00 |
| XLP/QQQ (USD) | 5 | 5% | Switching | 25.00% | 4.56% | -17.81% | 0 | -18.67 |
| XLP/QQQ (USD) | 5 | 5% | Staples only | 25.00% | 4.56% | -17.81% | 0 | -18.67 |
| XLP/QQQ (USD) | 5 | 5% | Nasdaq only | 62.33% | 10.18% | -35.62% | 0 | +18.67 |
| XLP/QQQ (USD) | 5 | 5% | 50/50 | 43.67% | 7.52% | -23.48% | 0 | +0.00 |
| XLP/QQQ (USD) | 2 | 3% | Switching | 12.82% | 6.22% | -10.75% | 0 | -9.32 |
| XLP/QQQ (USD) | 2 | 3% | Staples only | 12.82% | 6.22% | -10.75% | 0 | -9.32 |
| XLP/QQQ (USD) | 2 | 3% | Nasdaq only | 31.46% | 14.67% | -22.88% | 0 | +9.32 |
| XLP/QQQ (USD) | 2 | 3% | 50/50 | 22.14% | 10.52% | -14.97% | 0 | +0.00 |
| XLP/QQQ (USD) | 2 | 5% | Switching | 12.82% | 6.22% | -10.75% | 0 | -9.32 |
| XLP/QQQ (USD) | 2 | 5% | Staples only | 12.82% | 6.22% | -10.75% | 0 | -9.32 |
| XLP/QQQ (USD) | 2 | 5% | Nasdaq only | 31.46% | 14.67% | -22.88% | 0 | +9.32 |
| XLP/QQQ (USD) | 2 | 5% | 50/50 | 22.14% | 10.52% | -14.97% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Switching | 187.26% | 23.50% | -30.65% | 13 | +120.59 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Staples only | 81.68% | 12.69% | -10.72% | 0 | +15.02 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | Nasdaq only | 51.64% | 8.68% | -36.47% | 0 | -15.02 |
| XST.TO/XQQ.TO (CAD) | 5 | 3% | 50/50 | 66.66% | 10.76% | -18.48% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Switching | 201.56% | 24.71% | -30.65% | 9 | +134.90 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Staples only | 81.68% | 12.69% | -10.72% | 0 | +15.02 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | Nasdaq only | 51.64% | 8.68% | -36.47% | 0 | -15.02 |
| XST.TO/XQQ.TO (CAD) | 5 | 5% | 50/50 | 66.66% | 10.76% | -18.48% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Switching | 90.90% | 38.20% | -18.04% | 11 | +62.05 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Staples only | 30.63% | 14.30% | -10.72% | 0 | +1.78 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | Nasdaq only | 27.06% | 12.73% | -22.81% | 0 | -1.78 |
| XST.TO/XQQ.TO (CAD) | 2 | 3% | 50/50 | 28.84% | 13.52% | -13.28% | 0 | +0.00 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Switching | 67.88% | 29.59% | -16.99% | 5 | +39.04 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Staples only | 30.63% | 14.30% | -10.72% | 0 | +1.78 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | Nasdaq only | 27.06% | 12.73% | -22.81% | 0 | -1.78 |
| XST.TO/XQQ.TO (CAD) | 2 | 5% | 50/50 | 28.84% | 13.52% | -13.28% | 0 | +0.00 |

## Assessment

The original raw-price rules produce **no XLP/QQQ switches** in either window or threshold. The strategy is simply XLP buy-and-hold: this pilot does not support XLP as a functioning replacement for the documented switching approach. This is a share-price-scale limitation, not evidence that XLP is intrinsically unsuitable as a staples investment.

No other candidate was analyzed. Expansion requires a separate decision.

## Data coverage, liquidity and return correlations

- **XLP (USD)**: 2021-11-05 to 2026-11-05; 1255 sessions; 0 missing; 30-day average volume 15,990,763 shares / 1,388,420,607 USD traded; 90-day averages 12,235,642 shares / 1,047,743,671 USD. Split events: [].
  US S&P 500 consumer staples; inception 1998-12-16; gross expense ratio 0.08% (issuer checked 2026-11-06). [Issuer](https://www.ssga.com/us/en/intermediary/etfs/state-street-consumer-staples-select-sector-spdr-etf-xlp).
- **QQQ (USD)**: 2021-11-05 to 2026-11-05; 1255 sessions; 0 missing; 30-day average volume 42,237,340 shares / 30,145,610,296 USD traded; 90-day averages 38,063,969 shares / 27,101,331,523 USD. Split events: [].
  US Nasdaq-100, USD; not equivalent to CAD-hedged XQQ. [Issuer](https://www.invesco.com/qqq-etf/en/about.html).
- **XST.TO (CAD)**: 2021-11-05 to 2026-11-05; 1255 sessions; 0 missing; 30-day average volume 25,940 shares / 1,718,268 CAD traded; 90-day averages 21,717 shares / 1,432,594 CAD. Split events: [{"date": "2021-12-30", "ratio": 0.988}, {"date": "2024-08-09", "ratio": 2.0}, {"date": "2024-12-30", "ratio": 0.967}].
  Canadian consumer staples reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239840/ishares-sptsx-capped-consumer-staples-index-etf).
- **XQQ.TO (CAD)**: 2021-11-05 to 2026-11-05; 1255 sessions; 0 missing; 30-day average volume 406,477 shares / 29,651,789 CAD traded; 90-day averages 236,826 shares / 17,079,004 CAD. Split events: [{"date": "2021-12-30", "ratio": 0.965}, {"date": "2024-08-09", "ratio": 3.0}].
  Nasdaq-100 CAD-hedged reference. [Issuer](https://www.blackrock.com/ca/investors/en/products/239698/ishares-nasdaq-100-index-etf-cadhedged-fund).
- XLP/QQQ, 5y: 2021-11-05 to 2026-11-05, 1255 paired sessions; return correlation 0.2670; last-year correlation -0.2736 (252 returns).
- XLP/QQQ, 2y: 2024-11-05 to 2026-11-05, 502 paired sessions; return correlation -0.0292; last-year correlation -0.2736 (252 returns).
- XST.TO/XQQ.TO, 5y: 2021-11-05 to 2026-11-05, 1255 paired sessions; return correlation 0.1922; last-year correlation -0.1790 (252 returns).
- XST.TO/XQQ.TO, 2y: 2024-11-05 to 2026-11-05, 503 paired sessions; return correlation -0.0330; last-year correlation -0.1790 (252 returns).

## Reproducibility

Provider: Yahoo Finance via yfinance 1.7.0; auto_adjust=False, actions=True. Each pair uses common observed sessions, without forward filling. CAD and USD cohorts are separate; there is no cross-candidate ranking in this single-candidate pilot.
CSV files preserve provider precision; Adj Close and actions are exported for audit but do not drive returns.
Manifest: [coverage and SHA-256 hashes](../src/etf_research_manifest.json). Daily data source: Yahoo Finance, accessed through yfinance. [Provider price-adjustment explanation](https://help.yahoo.com/kb/SLN28256.html).
Method reference: [original strategy document](./XST_XQQ_Switch_Strategy_v1.0_2026-04-17.docx).
Rerun: `python -m src.etf_research`. No account values, holdings or email alerts are used.
