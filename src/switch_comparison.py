"""Equal-capital price-return comparison for confirmed switches."""

from datetime import datetime
from math import isfinite


def compare_since_first_switch(history: list[dict], prices: dict[str, float]) -> list[dict]:
    if not history:
        raise ValueError("No confirmed switches are available for comparison.")
    trades = sorted(history, key=lambda trade: datetime.fromisoformat(trade["switched_at"]))
    first = trades[0]
    capital = 10000.0
    initial_prices = {
        first["sold_ticker"]: first["sold_price"],
        first["bought_ticker"]: first["bought_price"],
    }
    for ticker in ("XST", "XQQ"):
        if ticker not in prices or not isfinite(prices[ticker]) or prices[ticker] <= 0:
            raise ValueError(f"A positive latest price is required for {ticker}.")

    held = first["bought_ticker"]
    entry = first["bought_price"]
    switched_factor = 1.0
    for trade in trades[1:]:
        if trade["sold_ticker"] != held:
            raise ValueError("Switch history is not a continuous sequence of held ETFs.")
        switched_factor *= trade["sold_price"] / entry
        held = trade["bought_ticker"]
        entry = trade["bought_price"]
    switched_factor *= prices[held] / entry
    xqq_factor = prices["XQQ"] / initial_prices["XQQ"]
    xst_factor = prices["XST"] / initial_prices["XST"]
    return [
        {
            "Strategy": name,
            "Initial XQQ price (CAD)": initial_prices["XQQ"] if "XQQ" in tickers else None,
            "Initial XST price (CAD)": initial_prices["XST"] if "XST" in tickers else None,
            "Starting capital (CAD)": capital,
            "Current value (CAD)": capital * factor,
            "Gain / loss (CAD)": capital * (factor - 1),
            "Return (%)": (factor - 1) * 100,
            "Switching advantage (CAD)": capital * (switched_factor - factor),
        }
        for name, factor, tickers in (
            ("Your switches (equal capital)", switched_factor, (first["bought_ticker"],)),
            ("XQQ only", xqq_factor, ("XQQ",)),
            ("XST only", xst_factor, ("XST",)),
            ("50% XQQ / 50% XST", (xqq_factor + xst_factor) / 2, ("XQQ", "XST")),
        )
    ]
