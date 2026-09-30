"""Refresh daily XST/XQQ price history and derived dashboard data."""

from pathlib import Path

import pandas as pd
import yfinance as yf

from src.compare_prices import main as refresh_delta_signals
from src.refresh_asymmetric_theory import main as refresh_asymmetric_theory


SRC = Path(__file__).parent
TICKERS = {
    "XST.TO": SRC / "XST Historical Data (1).csv",
    "XQQ.TO": SRC / "XQQ Historical Data (1).csv",
}
HISTORY_COLUMNS = ["Date", "Price", "Open", "High", "Low", "Vol.", "Change %"]


def download_history(ticker: str) -> pd.DataFrame:
    history = yf.Ticker(ticker).history(
        period="3mo", interval="1d", auto_adjust=False, actions=False
    )
    if history.empty or "Close" not in history.columns:
        raise ValueError(f"Yahoo Finance returned no daily closes for {ticker}")

    dates = pd.DatetimeIndex(history.index)
    if dates.tz is not None:
        dates = dates.tz_localize(None)

    close = pd.to_numeric(history["Close"], errors="coerce")
    volume = pd.to_numeric(history.get("Volume"), errors="coerce")
    change_pct = close.pct_change().mul(100)
    result = pd.DataFrame(
        {
            "Date": dates.strftime("%Y-%m-%d"),
            "Price": close.round(2),
            "Open": pd.to_numeric(history.get("Open"), errors="coerce").round(2),
            "High": pd.to_numeric(history.get("High"), errors="coerce").round(2),
            "Low": pd.to_numeric(history.get("Low"), errors="coerce").round(2),
            "Vol.": volume.map(
                lambda value: "" if pd.isna(value) else (
                    f"{value / 1000:.2f}K" if value >= 1000 else str(int(value))
                )
            ),
            "Change %": change_pct.map(
                lambda value: "" if pd.isna(value) else f"{value:.2f}%"
            ),
        },
        columns=HISTORY_COLUMNS,
    )
    return result.dropna(subset=["Date", "Price"])


def merge_history(existing: pd.DataFrame, refreshed: pd.DataFrame) -> pd.DataFrame:
    if refreshed.empty:
        raise ValueError("Refusing to replace history with an empty Yahoo response")

    previous = existing.copy()
    incoming = refreshed.copy()
    previous["Date"] = pd.to_datetime(previous["Date"], errors="coerce")
    incoming["Date"] = pd.to_datetime(incoming["Date"], errors="coerce")
    previous = previous.dropna(subset=["Date", "Price"])
    incoming = incoming.dropna(subset=["Date", "Price"])

    if not previous.empty and incoming["Date"].max() < previous["Date"].max():
        raise ValueError("Yahoo history is older than the locally stored price data")

    merged = pd.concat([previous, incoming], ignore_index=True)
    merged = merged.drop_duplicates(subset=["Date"], keep="first")
    merged = merged.sort_values("Date", ascending=False).reset_index(drop=True)
    merged["Date"] = merged["Date"].dt.strftime("%Y-%m-%d")
    return merged.reindex(columns=HISTORY_COLUMNS)


def main() -> None:
    updated = {}
    for ticker, path in TICKERS.items():
        existing = pd.read_csv(path)
        history = download_history(ticker)
        updated[path] = merge_history(existing, history)

    for path, history in updated.items():
        history.to_csv(path, index=False)
        print(f"Updated {path} through {history['Date'].max()}")

    refresh_delta_signals()
    refresh_asymmetric_theory()


if __name__ == "__main__":
    main()