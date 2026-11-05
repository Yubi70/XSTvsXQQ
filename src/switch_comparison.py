"""Equal-capital price-return comparison for confirmed switches."""

from datetime import datetime
from math import isfinite


def compare_since_first_switch(history: list[dict], prices: dict[str, float]) -> list[dict]:
    if not history:
        raise ValueError("No confirmed switches are available for comparison.")
    trades = sorted(history, key=lambda trade: datetime.fromisoformat(trade["switched_at"]))
    first = trades[0]
    quantity = first.get("sold_quantity")
    if quantity is None:
        raise ValueError("Set the first switch's sold quantity to establish equal starting capital.")
    capital = quantity * first["sold_price"]
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
            "Starting capital (CAD)": capital,
            "Current value (CAD)": capital * factor,
            "Gain / loss (CAD)": capital * (factor - 1),
            "Return (%)": (factor - 1) * 100,
            "Switching advantage (CAD)": capital * (switched_factor - factor),
        }
        for name, factor in (
            ("Your switches (equal capital)", switched_factor),
            ("XQQ only", xqq_factor),
            ("XST only", xst_factor),
            ("50% XQQ / 50% XST", (xqq_factor + xst_factor) / 2),
        )
    ]
