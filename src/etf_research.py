"""Reproducible XLP/QQQ pilot using the original raw-close switching rules."""

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path

import exchange_calendars as xcals
import pandas as pd
import yfinance as yf


SRC = Path(__file__).parent
ROOT = SRC.parent
PREFIX = "etf_research_"
HISTORY_COLUMNS = [
    "Date", "Open", "High", "Low", "Close", "Adj Close", "Volume",
    "Dividends", "Stock Splits",
]
FUNDS = {
    "XLP": {
        "currency": "USD", "calendar": "XNYS",
        "source": "https://www.ssga.com/us/en/intermediary/etfs/state-street-consumer-staples-select-sector-spdr-etf-xlp",
        "description": "US S&P 500 consumer staples; inception 1998-12-16; gross expense ratio 0.08% (issuer checked 2026-11-06).",
    },
    "QQQ": {
        "currency": "USD", "calendar": "XNYS",
        "source": "https://www.invesco.com/qqq-etf/en/about.html",
        "description": "US Nasdaq-100, USD; not equivalent to CAD-hedged XQQ.",
    },
    "XST.TO": {
        "currency": "CAD", "calendar": "XTSE",
        "source": "https://www.blackrock.com/ca/investors/en/products/239840/ishares-sptsx-capped-consumer-staples-index-etf",
        "description": "Canadian consumer staples reference.",
    },
    "XQQ.TO": {
        "currency": "CAD", "calendar": "XTSE",
        "source": "https://www.blackrock.com/ca/investors/en/products/239698/ishares-nasdaq-100-index-etf-cadhedged-fund",
        "description": "Nasdaq-100 CAD-hedged reference.",
    },
}
PAIRS = (("XLP", "QQQ", "USD"), ("XST.TO", "XQQ.TO", "CAD"))
SUMMARY_COLUMNS = [
    "Pair", "Currency", "Years", "Threshold", "Start", "End", "Sessions",
    "Strategy", "Final value", "Return %", "CAGR %", "Max drawdown %",
    "Annual volatility %", "Switches", "Mean completed holding days",
    "Excess vs staples (pp)", "Excess vs Nasdaq (pp)", "Excess vs 50/50 (pp)",
]
SWITCH_COLUMNS = ["Date", "From", "To", "Premium %", "Sale price", "Buy price", "Value"]
CURVE_COLUMNS = ["Date", "Staples close", "Nasdaq close", "Premium %", "Holding", "Switching", "Staples only", "Nasdaq only", "50/50"]
METHODOLOGY = (
    "Original method: premium = (staples Close - Nasdaq Close) / Nasdaq Close * 100; "
    "thresholds +/-3% and +/-5%; start in staples; switch only to the opposite ETF. "
    "Earn each day's return in the previous holding, then execute at that day's close. "
    "Initial capital 10,000 in each pair's own currency; fractional shares; "
    "unrebalanced 50/50 benchmark. No dividends, fees, slippage or taxes. "
    "Signals and executions at the same close are optimistic and not guaranteed executable."
)
LIMITATIONS = (
    "Raw share-price differences are not valuations. Share denominations and splits can "
    "dominate signals; Yahoo Close is not dividend-adjusted but is normally split-restated, "
    "not historical as-traded prices. No rebasing or reconstruction of as-traded prices is used. "
    "Zero-switch results are retained. USD XLP/QQQ does not test XLP against CAD-hedged XQQ; "
    "USD and CAD dollar results are separate. Correlations use daily returns, not price levels. "
    "Historical performance cannot establish the best future investment. Only XLP is analyzed; "
    "IYK, KXI, FSTA and VDC are deferred."
)


def history_name(ticker: str) -> str:
    return f"{PREFIX}{ticker.replace('.', '_')}_daily.csv"


def completed_cutoff(now: pd.Timestamp) -> pd.Timestamp:
    if now.tzinfo is None:
        raise ValueError("The research clock must be timezone-aware.")
    dates = []
    for name in ("XNYS", "XTSE"):
        calendar = xcals.get_calendar(
            name, start=now.date() - pd.Timedelta(days=20),
            end=now.date() + pd.Timedelta(days=2),
        )
        closed = calendar.schedule[calendar.schedule["close"] <= now]
        if closed.empty:
            raise ValueError(f"No completed session found for {name}.")
        dates.append(pd.Timestamp(closed.index[-1]).tz_localize(None))
    return min(dates)


def validate_history(frame: pd.DataFrame, start: pd.Timestamp, cutoff: pd.Timestamp) -> pd.DataFrame:
    missing = set(HISTORY_COLUMNS) - set(frame.columns)
    if missing or frame.empty:
        raise ValueError(f"Empty or incomplete daily history; missing columns: {sorted(missing)}")
    frame = frame[HISTORY_COLUMNS].reset_index(drop=True).copy()
    frame["Date"] = pd.to_datetime(frame["Date"], errors="raise")
    if frame["Date"].isna().any() or frame["Date"].duplicated().any():
        raise ValueError("Daily history contains missing or duplicate dates.")
    if (frame["Date"] < start).any() or (frame["Date"] > cutoff).any():
        raise ValueError("Daily history is outside the requested completed-session window.")
    for column in HISTORY_COLUMNS[1:]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if not frame[column].map(lambda value: pd.notna(value) and math.isfinite(value)).all():
            raise ValueError(f"Invalid daily values in {column}.")
        if column in ("Open", "High", "Low", "Close", "Adj Close"):
            if (frame[column] <= 0).any():
                raise ValueError(f"Non-positive price in {column}.")
        elif (frame[column] < 0).any():
            raise ValueError(f"Negative daily value in {column}.")
    if ((frame["High"] < frame[["Open", "Close", "Low"]].max(axis=1))
            | (frame["Low"] > frame[["Open", "Close", "High"]].min(axis=1))).any():
        raise ValueError("Daily OHLC ranges are inconsistent.")
    return frame.sort_values("Date").reset_index(drop=True)


def download_history(ticker: str, start: pd.Timestamp, cutoff: pd.Timestamp) -> pd.DataFrame:
    history = yf.Ticker(ticker).history(
        start=start.date().isoformat(),
        end=(cutoff + pd.Timedelta(days=1)).date().isoformat(),
        interval="1d", auto_adjust=False, actions=True,
    )
    if history.empty:
        raise ValueError(f"Yahoo returned no daily history for {ticker}.")
    history = history.copy()
    history["Date"] = pd.DatetimeIndex(history.index).tz_localize(None).normalize()
    return validate_history(history, start, cutoff)


def align_pair(staples: pd.DataFrame, nasdaq: pd.DataFrame) -> pd.DataFrame:
    merged = staples[["Date", "Close"]].merge(
        nasdaq[["Date", "Close"]], on="Date", how="inner", suffixes=("_staples", "_nasdaq"),
        validate="one_to_one",
    ).sort_values("Date").reset_index(drop=True)
    if len(merged) < 2:
        raise ValueError("At least two common daily observations are required.")
    return merged


def backtest(frame: pd.DataFrame, staples: str, nasdaq: str, threshold: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    if threshold <= 0 or not math.isfinite(threshold):
        raise ValueError("Threshold must be positive and finite.")
    frame = frame.sort_values("Date").reset_index(drop=True)
    if len(frame) < 2 or frame["Date"].duplicated().any():
        raise ValueError("Backtests require at least two unique daily observations.")
    values = frame[["Close_staples", "Close_nasdaq"]]
    if not values.map(lambda value: math.isfinite(value) and value > 0).all().all():
        raise ValueError("Backtest prices must be positive and finite.")
    holding, value = staples, 10000.0
    curves, switches = [], []
    first = frame.iloc[0]
    previous = None
    for row in frame.itertuples(index=False):
        prices = {staples: row.Close_staples, nasdaq: row.Close_nasdaq}
        if previous is not None:
            value *= prices[holding] / previous[holding]
        premium = (row.Close_staples - row.Close_nasdaq) / row.Close_nasdaq * 100
        target = nasdaq if premium >= threshold else staples if premium <= -threshold else holding
        if target != holding:
            switches.append({
                "Date": row.Date, "From": holding, "To": target, "Premium %": premium,
                "Sale price": prices[holding], "Buy price": prices[target], "Value": value,
            })
            holding = target
        staples_value = 10000 * row.Close_staples / first["Close_staples"]
        nasdaq_value = 10000 * row.Close_nasdaq / first["Close_nasdaq"]
        curves.append({
            "Date": row.Date, "Staples close": row.Close_staples, "Nasdaq close": row.Close_nasdaq,
            "Premium %": premium, "Holding": holding, "Switching": value,
            "Staples only": staples_value, "Nasdaq only": nasdaq_value,
            "50/50": (staples_value + nasdaq_value) / 2,
        })
        previous = prices
    return pd.DataFrame(curves, columns=CURVE_COLUMNS), pd.DataFrame(switches, columns=SWITCH_COLUMNS)


def performance(series: pd.Series, dates: pd.Series) -> dict:
    if len(series) < 3:
        raise ValueError("Risk metrics require at least three daily observations.")
    years = (dates.iloc[-1] - dates.iloc[0]).days / 365.25
    factor = series.iloc[-1] / series.iloc[0]
    if years <= 0:
        raise ValueError("Performance requires a positive date span.")
    return {
        "Final value": float(series.iloc[-1]), "Return %": (factor - 1) * 100,
        "CAGR %": (factor ** (1 / years) - 1) * 100,
        "Max drawdown %": float((series / series.cummax() - 1).min()) * 100,
        "Annual volatility %": float(series.pct_change(fill_method=None).dropna().std(ddof=1) * math.sqrt(252) * 100),
    }


def quality_metadata(ticker: str, frame: pd.DataFrame, start: pd.Timestamp, cutoff: pd.Timestamp) -> dict:
    calendar = xcals.get_calendar(FUNDS[ticker]["calendar"], start=start, end=cutoff)
    expected = calendar.sessions_in_range(start, cutoff).tz_localize(None)
    actual = pd.DatetimeIndex(frame["Date"])
    missing = expected.difference(actual)
    if len(actual.difference(expected)):
        raise ValueError(f"{ticker} includes non-session dates.")
    returns = frame["Close"].pct_change(fill_method=None)
    split_rows = frame[frame["Stock Splits"] != 0]
    metadata = {
        **FUNDS[ticker], "ticker": ticker, "first_session": str(actual.min().date()),
        "last_session": str(actual.max().date()), "rows": len(frame),
        "missing_sessions": [str(value.date()) for value in missing],
        "split_events": [
            {"date": str(row.Date.date()), "ratio": row._asdict()["Stock_Splits"]}
            for row in split_rows.rename(columns={"Stock Splits": "Stock_Splits"}).itertuples(index=False)
        ],
        "large_close_moves": [
            str(frame.loc[index, "Date"].date()) for index in returns[returns.abs() > 0.3].index
        ],
    }
    for sessions in (30, 90):
        tail = frame.tail(sessions)
        metadata[f"volume_sessions_{sessions}"] = len(tail)
        metadata[f"mean_share_volume_{sessions}"] = float(tail["Volume"].mean())
        metadata[f"mean_dollar_volume_{sessions}"] = float((tail["Volume"] * tail["Close"]).mean())
    return metadata


def csv_text(frame: pd.DataFrame) -> str:
    return frame.to_csv(index=False, date_format="%Y-%m-%d")


def build_outputs(histories: dict[str, pd.DataFrame], cutoff: pd.Timestamp, retrieved: pd.Timestamp) -> dict[str, str]:
    start = cutoff - pd.DateOffset(years=5)
    manifest = {
        "schema_version": 1, "pilot": "XLP", "cutoff": str(cutoff.date()),
        "requested_start": str(start.date()), "retrieved_at": retrieved.isoformat(),
        "provider": f"Yahoo Finance via yfinance {yf.__version__}; auto_adjust=False, actions=True",
        "methodology": METHODOLOGY, "limitations": LIMITATIONS, "funds": {}, "samples": [],
    }
    outputs = {}
    summary = []
    for ticker in FUNDS:
        histories[ticker] = validate_history(histories[ticker], start, cutoff)
        outputs[f"src/{history_name(ticker)}"] = csv_text(histories[ticker])
        manifest["funds"][ticker] = quality_metadata(ticker, histories[ticker], start, cutoff)
        # All pilot funds predate this window: truncated five-year downloads must fail visibly.
        if manifest["funds"][ticker]["missing_sessions"]:
            raise ValueError(f"{ticker} is missing exchange sessions: {manifest['funds'][ticker]['missing_sessions'][:5]}")
    for staples, nasdaq, currency in PAIRS:
        pair = f"{staples}/{nasdaq}"
        aligned = align_pair(histories[staples], histories[nasdaq])
        for years in (5, 2):
            window = aligned[aligned["Date"] >= cutoff - pd.DateOffset(years=years)].copy()
            if len(window) < 3:
                raise ValueError(f"Insufficient {years}-year observations for {pair}.")
            returns = window.set_index("Date")[["Close_staples", "Close_nasdaq"]].pct_change(fill_method=None).dropna()
            one_year = returns[returns.index >= cutoff - pd.DateOffset(years=1)]
            correlations = {
                "daily_return_correlation": float(returns.corr().iloc[0, 1]),
                "one_year_return_correlation": float(one_year.corr().iloc[0, 1]),
                "return_observations": len(returns), "one_year_observations": len(one_year),
            }
            if not all(math.isfinite(correlations[key]) for key in ("daily_return_correlation", "one_year_return_correlation")):
                raise ValueError(f"Insufficient return variation for correlation: {pair}")
            manifest["samples"].append({
                "pair": pair, "years": years, "start": str(window["Date"].min().date()),
                "end": str(window["Date"].max().date()), "sessions": len(window), **correlations,
            })
            for threshold in (3, 5):
                curve, switches = backtest(window, staples, nasdaq, threshold)
                key = f"{staples.replace('.', '_')}_{nasdaq.replace('.', '_')}_{years}y_{threshold}pct"
                outputs[f"src/{PREFIX}{key}_curve.csv"] = csv_text(curve)
                outputs[f"src/{PREFIX}{key}_switches.csv"] = csv_text(switches)
                dates = [window["Date"].iloc[0], *switches["Date"].tolist()]
                durations = [(right - left).days for left, right in zip(dates, dates[1:])]
                baseline_returns = {name: (curve[name].iloc[-1] / 10000 - 1) * 100 for name in ("Staples only", "Nasdaq only", "50/50")}
                for strategy in ("Switching", "Staples only", "Nasdaq only", "50/50"):
                    metrics = performance(curve[strategy], curve["Date"])
                    summary.append({
                        "Pair": pair, "Currency": currency, "Years": years, "Threshold": threshold,
                        "Start": str(window["Date"].min().date()), "End": str(window["Date"].max().date()),
                        "Sessions": len(window), "Strategy": strategy, **metrics,
                        "Switches": len(switches) if strategy == "Switching" else 0,
                        "Mean completed holding days": sum(durations) / len(durations) if durations and strategy == "Switching" else None,
                        **{f"Excess vs {label} (pp)": metrics["Return %"] - baseline_returns[name]
                           for label, name in (("staples", "Staples only"), ("Nasdaq", "Nasdaq only"), ("50/50", "50/50"))},
                    })
    summary_frame = pd.DataFrame(summary, columns=SUMMARY_COLUMNS)
    outputs[f"src/{PREFIX}summary.csv"] = csv_text(summary_frame)
    outputs["docs/etf_replacement_research.md"] = research_report(summary_frame, manifest)
    manifest["sha256"] = {
        path: hashlib.sha256(text.encode("utf-8")).hexdigest() for path, text in outputs.items()
    }
    outputs[f"src/{PREFIX}manifest.json"] = json.dumps(manifest, indent=2, allow_nan=False) + "\n"
    return outputs


def research_report(summary: pd.DataFrame, manifest: dict) -> str:
    lines = [
        "# XLP replacement research: original-method pilot", "",
        f"Data cutoff: **{manifest['cutoff']}**. Retrieved: {manifest['retrieved_at']}.",
        "", "## Method", "", METHODOLOGY, "", "## Critical limitations", "", LIMITATIONS,
        "", "## Results", "",
        "| Pair / currency | Years | Threshold | Strategy | Return | CAGR | Max drawdown | Switches | Excess vs 50/50 (pp) |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary.to_dict("records"):
        lines.append(
            f"| {row['Pair']} ({row['Currency']}) | {row['Years']} | {row['Threshold']}% | {row['Strategy']} "
            f"| {row['Return %']:.2f}% | {row['CAGR %']:.2f}% | {row['Max drawdown %']:.2f}% "
            f"| {row['Switches']} | {row['Excess vs 50/50 (pp)']:+.2f} |"
        )
    pilot = summary[(summary["Pair"] == "XLP/QQQ") & (summary["Strategy"] == "Switching")]
    if (pilot["Switches"] == 0).all():
        conclusion = (
            "The original raw-price rules produce **no XLP/QQQ switches** in either window or threshold. "
            "The strategy is simply XLP buy-and-hold: this pilot does not support XLP as a functioning "
            "replacement for the documented switching approach. This is a share-price-scale limitation, "
            "not evidence that XLP is intrinsically unsuitable as a staples investment."
        )
    else:
        conclusion = (
            "Assess both thresholds and windows together, including drawdown and excess returns. "
            "Any observed advantage is specific to these raw price levels and same-close assumptions; "
            "it does not establish a robust or directly executable XST replacement."
        )
    lines += ["", "## Assessment", "", conclusion, "", "No other candidate was analyzed. Expansion requires a separate decision.",
              "", "## Data coverage, liquidity and return correlations", ""]
    for ticker, fund in manifest["funds"].items():
        lines += [
            f"- **{ticker} ({fund['currency']})**: {fund['first_session']} to {fund['last_session']}; "
            f"{fund['rows']} sessions; {len(fund['missing_sessions'])} missing; "
            f"30-day average volume {fund['mean_share_volume_30']:,.0f} shares / "
            f"{fund['mean_dollar_volume_30']:,.0f} {fund['currency']} traded; "
            f"90-day averages {fund['mean_share_volume_90']:,.0f} shares / "
            f"{fund['mean_dollar_volume_90']:,.0f} {fund['currency']}. "
            f"Split events: {json.dumps(fund['split_events'])}.",
            f"  {fund['description']} [Issuer]({fund['source']}).",
        ]
    for sample in manifest["samples"]:
        lines.append(
            f"- {sample['pair']}, {sample['years']}y: {sample['start']} to {sample['end']}, "
            f"{sample['sessions']} paired sessions; return correlation {sample['daily_return_correlation']:.4f}; "
            f"last-year correlation {sample['one_year_return_correlation']:.4f} "
            f"({sample['one_year_observations']} returns)."
        )
    lines += [
        "", "## Reproducibility", "",
        f"Provider: {manifest['provider']}. Each pair uses common observed sessions, without forward filling. "
        "CAD and USD cohorts are separate; there is no cross-candidate ranking in this single-candidate pilot.",
        "CSV files preserve provider precision; Adj Close and actions are exported for audit but do not drive returns.",
        "Manifest: [coverage and SHA-256 hashes](../src/etf_research_manifest.json). "
        "Daily data source: Yahoo Finance, accessed through yfinance. "
        "[Provider price-adjustment explanation](https://help.yahoo.com/kb/SLN28256.html).",
        "Method reference: [original strategy document](./XST_XQQ_Switch_Strategy_v1.0_2026-04-17.docx).",
        "Rerun: `python -m src.etf_research`. No account values, holdings or email alerts are used.",
        "",
    ]
    return "\n".join(lines)


def publish_outputs(outputs: dict[str, str], root: Path) -> None:
    staged = []
    try:
        for relative, text in outputs.items():
            target = root / relative
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=target.parent, delete=False) as handle:
                handle.write(text)
                staged.append((Path(handle.name), target))
        # Manifest is written last: readers verify hashes and reject incomplete snapshots.
        for source, target in staged:
            os.replace(source, target)
    finally:
        for source, _ in staged:
            source.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cutoff", help="Completed session cutoff YYYY-MM-DD (cannot be in the future).")
    args = parser.parse_args()
    now = pd.Timestamp.now(tz="UTC")
    completed = completed_cutoff(now)
    cutoff = pd.Timestamp(args.cutoff) if args.cutoff else completed
    if cutoff.tzinfo is not None or cutoff.normalize() != cutoff or cutoff > completed:
        parser.error("Cutoff must be a date no later than the latest completed session.")
    start = cutoff - pd.DateOffset(years=5)
    histories = {}
    for ticker in FUNDS:
        print(f"Downloading {ticker}: {start.date()} through {cutoff.date()}", flush=True)
        histories[ticker] = download_history(ticker, start, cutoff)
    outputs = build_outputs(histories, cutoff, now)
    publish_outputs(outputs, ROOT)
    print(f"Published {len(outputs)} validated XLP pilot artifacts.")


if __name__ == "__main__":
    main()
