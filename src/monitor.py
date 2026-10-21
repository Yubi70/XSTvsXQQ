"""
monitor.py — Fetches XST.TO and XQQ.TO prices from Yahoo Finance every 30 minutes,
calculates the delta, and appends results to a rolling log (monitor_log.csv).
"""

import os
import csv
import json
import smtplib
import argparse
import math
import tempfile
from datetime import date, datetime, timedelta
from email.mime.text import MIMEText
import pandas as pd
import yfinance as yf
import pytz
import exchange_calendars as xcals

from src.github_data import validate_position_state

SMTP_SENDER     = os.getenv("SMTP_SENDER")
SMTP_PASSWORD   = os.getenv("SMTP_PASSWORD")
ALERT_RECIPIENTS = [r.strip() for r in os.getenv("ALERT_RECIPIENT", "").split(",") if r.strip()]

TICKERS = ["XST.TO", "XQQ.TO"]
LOG_PATH = os.path.join(os.path.dirname(__file__), "monitor_log.csv")
LOG_FIELDS = ["Timestamp", "Price_XST", "Price_XQQ", "Delta_$", "Delta_%", "Signal", "Observation"]
SWITCH_UP_THRESHOLD_PCT = 11.5    # XST -> XQQ when delta >= +11.5%
SWITCH_DOWN_THRESHOLD_PCT = 7.0   # XQQ -> XST when delta <= -7.0%
STATE_PATH = os.path.join(os.path.dirname(__file__), "position_state.json")
VALID_HOLDINGS = {"XST", "XQQ"}
DEFAULT_HOLDING = os.getenv("START_HOLDING", "XQQ").strip().upper()


def _parse_optional_float(raw: str | None) -> float | None:
    try:
        value = float((raw or "").strip())
        return round(value, 4)
    except (TypeError, ValueError):
        return None


ENV_COST_XST = _parse_optional_float(os.getenv("LAST_SWITCH_COST_XST"))
ENV_COST_XQQ = _parse_optional_float(os.getenv("LAST_SWITCH_COST_XQQ"))


MARKET_TZ = pytz.timezone("America/Toronto")
SESSION_LOOKBACK_DAYS = 30
CLOSE_PUBLICATION_DELAY = timedelta(minutes=15)


def normalize_holding(holding: str | None) -> str:
    value = (holding or "").strip().upper()
    return value if value in VALID_HOLDINGS else "XQQ"


def opposite_holding(holding: str) -> str:
    return "XQQ" if holding == "XST" else "XST"


def expected_signal_for_holding(holding: str) -> str:
    if holding == "XST":
        return "XST HIGH vs XQQ"  # sell XST, buy XQQ
    return "XQQ HIGH vs XST"      # sell XQQ, buy XST


def _default_state() -> dict:
    return {
        "holding": normalize_holding(DEFAULT_HOLDING),
        "cost_basis": {
            "XST": ENV_COST_XST,
            "XQQ": ENV_COST_XQQ,
        },
    }


def _normalize_cost_basis(raw_cost_basis: dict | None) -> dict[str, float | None]:
    payload = raw_cost_basis or {}
    return {
        "XST": _parse_optional_float(str(payload.get("XST")) if payload.get("XST") is not None else None),
        "XQQ": _parse_optional_float(str(payload.get("XQQ")) if payload.get("XQQ") is not None else None),
    }


def load_state() -> dict:
    default_state = _default_state()
    if not os.path.isfile(STATE_PATH):
        save_state(default_state)
        return default_state
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        payload = validate_position_state(json.load(f))

    state = {
        **payload,
        "holding": normalize_holding(payload.get("holding")),
        "cost_basis": _normalize_cost_basis(payload.get("cost_basis")),
    }

    # Repository secrets seed missing costs, not existing position data.
    if state["cost_basis"]["XST"] is None and ENV_COST_XST is not None:
        state["cost_basis"]["XST"] = ENV_COST_XST
    if state["cost_basis"]["XQQ"] is None and ENV_COST_XQQ is not None:
        state["cost_basis"]["XQQ"] = ENV_COST_XQQ

    return state


def save_state(state: dict) -> None:
    payload = {
        **state,
        "holding": normalize_holding(state.get("holding")),
        "cost_basis": _normalize_cost_basis(state.get("cost_basis")),
        "updated_at": datetime.now(MARKET_TZ).strftime("%Y-%m-%d %H:%M:%S %Z"),
    }
    validate_position_state(payload)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)


def load_holding_state() -> str:
    return normalize_holding(load_state().get("holding"))


def save_holding_state(holding: str) -> None:
    state = load_state()
    state["holding"] = normalize_holding(holding)
    save_state(state)


def _price_key_for_holding(holding: str) -> str:
    return "Price_XST" if holding == "XST" else "Price_XQQ"


def compute_position_pnl(result: dict, holding: str, state: dict) -> dict[str, float | str | None]:
    price_key = _price_key_for_holding(holding)
    current_price = result.get(price_key)
    entry_cost = (state.get("cost_basis") or {}).get(holding)

    if current_price is None:
        return {
            "Entry_Cost": entry_cost,
            "PnL_$": None,
            "PnL_%": None,
            "Status": "NO PRICE",
        }
    if entry_cost is None:
        return {
            "Entry_Cost": None,
            "PnL_$": None,
            "PnL_%": None,
            "Status": "NO COST",
        }

    pnl_abs = round(current_price - entry_cost, 4)
    pnl_pct = None if entry_cost == 0 else round((pnl_abs / entry_cost) * 100, 2)

    if pnl_abs > 0:
        status = "WINNING"
    elif pnl_abs < 0:
        status = "LOSING"
    else:
        status = "BREAKEVEN"

    return {
        "Entry_Cost": round(entry_cost, 4),
        "PnL_$": pnl_abs,
        "PnL_%": pnl_pct,
        "Status": status,
    }


def filter_actionable_signal(raw_signal: str, holding: str) -> str:
    if raw_signal in ("", "DATA ERROR"):
        return raw_signal
    return raw_signal if raw_signal == expected_signal_for_holding(holding) else ""


def session_schedule(start: date, end: date) -> pd.DataFrame:
    calendar = xcals.get_calendar(
        "XTSE", start=start - timedelta(days=7), end=end + timedelta(days=7)
    )
    return calendar.schedule.loc[start.isoformat():end.isoformat()]


def is_within_collection_window() -> bool:
    now = datetime.now(MARKET_TZ)
    schedule = session_schedule(now.date(), now.date())
    if schedule.empty:
        return False
    session = schedule.iloc[0]
    return session["open"] <= now < session["close"]



def fetch_prices() -> dict[str, float]:
    prices: dict[str, float | None] = {ticker: None for ticker in TICKERS}
    for attempt in range(3):
        try:
            data = yf.download(TICKERS, period="1d", interval="1m", progress=False, auto_adjust=True)
            if data is None or getattr(data, "empty", False):
                raise ValueError("Yahoo returned an empty price table")

            close_sources = []
            if isinstance(data, dict):
                maybe_close = data.get("Close")
                if maybe_close is not None:
                    close_sources.append(maybe_close)
            else:
                if hasattr(data, "columns") and "Close" in data.columns:
                    close_sources.append(data["Close"])
                elif hasattr(data, "columns"):
                    close_sources.append(data)

            if not close_sources:
                raise ValueError("Yahoo returned a response without a Close frame")

            updated_any = False
            for ticker in TICKERS:
                for close_source in close_sources:
                    try:
                        series = None
                        if isinstance(close_source, pd.DataFrame):
                            if ticker in close_source.columns:
                                series = close_source[ticker]
                            else:
                                for col in close_source.columns:
                                    if isinstance(col, tuple) and col[-1] == ticker:
                                        series = close_source[col]
                                        break
                        elif isinstance(close_source, pd.Series):
                            if close_source.name == ticker:
                                series = close_source
                            elif close_source.name in (None, "Close"):
                                series = close_source

                        if series is None:
                            continue

                        valid = pd.to_numeric(series, errors="coerce").dropna()
                        if valid.empty:
                            continue

                        prices[ticker] = round(float(valid.iloc[-1]), 4)
                        updated_any = True
                        break
                    except Exception:
                        continue

                if prices.get(ticker) is None:
                    print(f"  [WARN] Could not fetch {ticker}: no valid close value in response")

            if all(prices.get(ticker) is not None for ticker in TICKERS):
                return {ticker: float(value) for ticker, value in prices.items()}
            if attempt < 2 and updated_any:
                print(f"  [WARN] Partial Yahoo price payload on attempt {attempt + 1}; retrying...")
                continue
            if attempt < 2:
                print(f"  [WARN] Yahoo download failed on attempt {attempt + 1}; retrying...")
                continue
            return {ticker: float(value) if value is not None else None for ticker, value in prices.items()}
        except Exception as e:
            print(f"  [WARN] Yahoo download failed on attempt {attempt + 1}: {e}")
            if attempt == 2:
                return {ticker: None for ticker in TICKERS}

    return {ticker: float(value) if value is not None else None for ticker, value in prices.items()}


def compute_delta(prices: dict[str, float]) -> dict:
    xst = prices.get("XST.TO")
    xqq = prices.get("XQQ.TO")
    if xst is None or xqq is None:
        return {"Price_XST": xst, "Price_XQQ": xqq, "Delta_$": None, "Delta_%": None, "Signal": "DATA ERROR"}
    delta_abs = round(xst - xqq, 4)
    avg_price = (xst + xqq) / 2
    if avg_price == 0:
        return {"Price_XST": xst, "Price_XQQ": xqq, "Delta_$": delta_abs, "Delta_%": None, "Signal": "DATA ERROR"}
    delta_pct = round(((xst - xqq) / avg_price) * 100, 1)
    signal = "XST HIGH vs XQQ" if delta_pct >= SWITCH_UP_THRESHOLD_PCT else \
             "XQQ HIGH vs XST" if delta_pct <= -SWITCH_DOWN_THRESHOLD_PCT else ""
    return {
        "Price_XST": xst,
        "Price_XQQ": xqq,
        "Delta_$": delta_abs,
        "Delta_%": delta_pct,
        "Signal": signal,
    }


def read_log_rows() -> list[dict]:
    if not os.path.isfile(LOG_PATH) or os.path.getsize(LOG_PATH) == 0:
        return []
    with open(LOG_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames not in (LOG_FIELDS, LOG_FIELDS[:-1]):
            raise ValueError("Unrecognized monitor log columns; refusing to overwrite the log.")
        rows = list(reader)
    for row in rows:
        if None in row or any(row.get(field) is None for field in LOG_FIELDS[:-1]):
            raise ValueError("Malformed monitor log row; refusing to overwrite the log.")
        row["Observation"] = row.get("Observation") or "LIVE"
    return rows


def replace_log(rows: list[dict]) -> None:
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", newline="", encoding="utf-8",
            dir=os.path.dirname(LOG_PATH), delete=False,
        ) as output:
            temporary_path = output.name
            writer = csv.DictWriter(output, fieldnames=LOG_FIELDS)
            writer.writeheader()
            writer.writerows(sorted(rows, key=lambda row: row["Timestamp"][:19]))
        os.replace(temporary_path, LOG_PATH)
    finally:
        if temporary_path is not None and os.path.exists(temporary_path):
            os.unlink(temporary_path)


def write_log(row: dict) -> None:
    file_exists = os.path.isfile(LOG_PATH) and os.path.getsize(LOG_PATH) > 0
    if file_exists:
        with open(LOG_PATH, newline="", encoding="utf-8-sig") as f:
            header = next(csv.reader(f))
        if header != LOG_FIELDS:
            replace_log(read_log_rows())
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({**row, "Observation": row.get("Observation", "LIVE")})


def record_session_boundaries(now: datetime | None = None) -> None:
    """Repair opening/closing observations without replaying historical alerts."""
    now = now or datetime.now(MARKET_TZ)
    if now.tzinfo is None:
        raise ValueError("Session recovery requires a timezone-aware current time.")
    now = now.astimezone(MARKET_TZ)
    start = now.date() - timedelta(days=SESSION_LOOKBACK_DAYS)
    schedule = session_schedule(start, now.date())
    expected = []
    for session_date, session in schedule.iterrows():
        for observation, field, time_key in (("OPEN", "Open", "open"), ("CLOSE", "Close", "close")):
            timestamp = session[time_key].tz_convert(MARKET_TZ)
            available_at = timestamp + (CLOSE_PUBLICATION_DELAY if observation == "CLOSE" else timedelta())
            if available_at <= now:
                expected.append((session_date.date(), observation, field, timestamp))
    if not expected:
        return

    histories = {}
    for ticker in TICKERS:
        history = yf.Ticker(ticker).history(
            start=start.isoformat(), end=(now.date() + timedelta(days=1)).isoformat(),
            interval="1d", auto_adjust=False, actions=False, timeout=30, raise_errors=True,
        )
        if history.empty or not {"Open", "Close"}.issubset(history.columns):
            raise ValueError(f"Yahoo returned no daily Open/Close data for {ticker}.")
        dates = pd.DatetimeIndex(history.index)
        if dates.tz is not None:
            dates = dates.tz_convert(MARKET_TZ)
        history = history.copy()
        history.index = dates.date
        if history.index.has_duplicates:
            raise ValueError(f"Yahoo returned duplicate daily sessions for {ticker}.")
        histories[ticker] = history

    rows = read_log_rows()
    positions = {
        (row["Timestamp"], row["Observation"]): index
        for index, row in enumerate(rows) if row["Observation"] in ("OPEN", "CLOSE")
    }
    changed = False
    missing = []
    for session_date, observation, field, timestamp in expected:
        prices = {}
        for ticker, history in histories.items():
            value = history.at[session_date, field] if session_date in history.index else None
            if value is None or pd.isna(value) or not math.isfinite(float(value)) or float(value) <= 0:
                missing.append(f"{ticker} {session_date} {observation}")
            else:
                prices[ticker] = round(float(value), 4)
        if len(prices) != len(TICKERS):
            continue
        result = compute_delta(prices)
        result["Signal"] = ""
        row = {
            "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S %Z"),
            **result, "Observation": observation,
        }
        row = {field_name: str(row[field_name]) for field_name in LOG_FIELDS}
        key = (row["Timestamp"], observation)
        if key not in positions:
            positions[key] = len(rows)
            rows.append(row)
            changed = True
        elif rows[positions[key]] != row:
            rows[positions[key]] = row
            changed = True
    if changed:
        replace_log(rows)
        print("Saved Yahoo session opening/closing prices; no historical alerts were sent.")
    else:
        print("Session opening/closing prices are already up to date.")
    if missing:
        raise ValueError("Yahoo session prices unavailable; retry on the next run: " + ", ".join(missing))


def send_email(signal: str, xst: float, xqq: float, delta_pct: float) -> None:
    if not SMTP_SENDER or not SMTP_PASSWORD or not ALERT_RECIPIENTS:
        print("  [WARN] Email not configured — skipping email alert.")
        return
    subject = f"Switch Signal: {signal}"
    body = (
        f"XST vs XQQ Monitor — Switch Alert\n"
        f"{'='*40}\n"
        f"Signal  : {signal}\n"
        f"XST.TO  : ${xst}\n"
        f"XQQ.TO  : ${xqq}\n"
        f"Delta   : {delta_pct:+.1f}%\n\n"
        f"Consider rebalancing your position.\n"
    )
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"]    = SMTP_SENDER
    msg["To"]      = ", ".join(ALERT_RECIPIENTS)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
        server.login(SMTP_SENDER, SMTP_PASSWORD)
        server.sendmail(SMTP_SENDER, ALERT_RECIPIENTS, msg.as_string())
    print(f"  Email alert sent to {', '.join(ALERT_RECIPIENTS)}")


def run_check() -> None:
    if not is_within_collection_window():
        now = datetime.now(MARKET_TZ)
        print(f"\n[{now.strftime('%Y-%m-%d %H:%M')} ET] Market closed — skipping check.")
        return

    ts_et = datetime.now(MARKET_TZ)
    ts = ts_et.strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"\n[{ts}] Fetching prices...")
    state = load_state()
    holding = normalize_holding(state.get("holding"))
    print(f"  Current holding mode: {holding} (waiting for: {expected_signal_for_holding(holding)})")
    prices = fetch_prices()
    result = compute_delta(prices)
    position_pnl = compute_position_pnl(result, holding, state)
    raw_signal = result["Signal"]
    result["Signal"] = filter_actionable_signal(raw_signal, holding)
    row = {"Timestamp": ts, **result}
    write_log(row)

    print(f"  XST.TO : {result['Price_XST']}")
    print(f"  XQQ.TO : {result['Price_XQQ']}")
    print(f"  Delta  : {result['Delta_$']} CAD  ({result['Delta_%']}%)")
    if position_pnl["Status"] == "NO COST":
        print(f"  Position P/L ({holding}): set cost_basis in the GitHub position state to track win/loss.")
    elif position_pnl["Status"] == "NO PRICE":
        print(f"  Position P/L ({holding}): unavailable (price fetch failed).")
    else:
        print(
            f"  Position P/L ({holding}) from {position_pnl['Entry_Cost']}: "
            f"{position_pnl['PnL_$']:+.4f} CAD ({position_pnl['PnL_%']:+.2f}%) -> {position_pnl['Status']}"
        )
    if raw_signal and raw_signal != "DATA ERROR" and not result["Signal"]:
        print(f"  Threshold reached ({raw_signal}) but ignored because current holding is {holding}.")
    if result["Signal"]:
        print(f"  *** SIGNAL: {result['Signal']} ***")
        send_email(result["Signal"], result["Price_XST"], result["Price_XQQ"], result["Delta_%"])
        new_holding = opposite_holding(holding)
        state["holding"] = new_holding
        new_price_key = _price_key_for_holding(new_holding)
        new_entry_price = result.get(new_price_key)
        if new_entry_price is not None:
            state.setdefault("cost_basis", {})[new_holding] = round(new_entry_price, 4)
        save_state(state)
        print(f"  Holding mode flipped to {new_holding}. Next expected signal: {expected_signal_for_holding(new_holding)}")
    print(f"  Logged to {LOG_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Single-check collector for GitHub Actions.")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--once", action="store_true", help="Run one live price check.")
    modes.add_argument("--session-boundaries", action="store_true", help="Recover session Open/Close prices.")
    arguments = parser.parse_args()
    if os.getenv("GITHUB_ACTIONS") != "true":
        parser.error("Run the Price Monitor workflow on GitHub; local collection is disabled.")
    if arguments.session_boundaries:
        record_session_boundaries()
    else:
        run_once()


def run_once() -> None:
    """Single-shot entrypoint for remote schedulers (e.g. GitHub Actions cron)."""
    print("=== XST vs XQQ Price Monitor (single check) ===")
    run_check()


if __name__ == "__main__":
    main()
