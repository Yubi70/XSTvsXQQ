"""
monitor.py — Fetches XST.TO and XQQ.TO prices from Yahoo Finance every 30 minutes,
calculates the delta, and appends results to a rolling log (monitor_log.csv).
"""

import os
import csv
import json
import smtplib
import subprocess
import schedule
import time
import atexit
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import yfinance as yf
import ctypes
import threading
import pytz
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

SMTP_SENDER     = os.getenv("SMTP_SENDER")
SMTP_PASSWORD   = os.getenv("SMTP_PASSWORD")
ALERT_RECIPIENTS = [r.strip() for r in os.getenv("ALERT_RECIPIENT", "").split(",") if r.strip()]

TICKERS = ["XST.TO", "XQQ.TO"]
LOG_PATH = os.path.join(os.path.dirname(__file__), "monitor_log.csv")
LOG_FIELDS = ["Timestamp", "Price_XST", "Price_XQQ", "Delta_$", "Delta_%", "Signal"]
SIGNAL_THRESHOLD_PCT = 5.0  # flag when |delta %| >= this value
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
MARKET_OPEN  = (9, 30)   # 9:30 AM ET
MARKET_CLOSE = (16, 0)   # 4:00 PM ET
MARKET_STOP  = (16, 30)  # script self-exits at 4:30 PM ET
FIRST_CHECK_DELAY_MINUTES = 2  # delay opening validation to reduce Yahoo first-minute errors
CHECK_MINUTE_A = (MARKET_OPEN[1] + FIRST_CHECK_DELAY_MINUTES) % 60
CHECK_MINUTE_B = (CHECK_MINUTE_A + 30) % 60
FINAL_CLOSE_CHECK = (16, 2)  # capture one final value just after the close
LOCK_PATH = os.path.join(os.path.dirname(__file__), ".monitor.lock")
_LOCK_HANDLE = None


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
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)

        state = {
            "holding": normalize_holding(payload.get("holding")),
            "cost_basis": _normalize_cost_basis(payload.get("cost_basis")),
        }

        # If state cost is missing, seed from .env so first run can still show P/L.
        if state["cost_basis"]["XST"] is None and ENV_COST_XST is not None:
            state["cost_basis"]["XST"] = ENV_COST_XST
        if state["cost_basis"]["XQQ"] is None and ENV_COST_XQQ is not None:
            state["cost_basis"]["XQQ"] = ENV_COST_XQQ

        return state
    except Exception:
        save_state(default_state)
        return default_state


def save_state(state: dict) -> None:
    payload = {
        "holding": normalize_holding(state.get("holding")),
        "cost_basis": _normalize_cost_basis(state.get("cost_basis")),
        "updated_at": datetime.now(MARKET_TZ).strftime("%Y-%m-%d %H:%M:%S %Z"),
    }
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


def acquire_single_instance_lock() -> bool:
    global _LOCK_HANDLE
    try:
        _LOCK_HANDLE = open(LOCK_PATH, "a+")
        _LOCK_HANDLE.seek(0)
        _LOCK_HANDLE.write("0")
        _LOCK_HANDLE.flush()
        _LOCK_HANDLE.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(_LOCK_HANDLE.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(_LOCK_HANDLE.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        _LOCK_HANDLE.seek(0)
        _LOCK_HANDLE.write(str(os.getpid()))
        _LOCK_HANDLE.truncate()
        _LOCK_HANDLE.flush()
        return True
    except OSError:
        return False


def release_single_instance_lock() -> None:
    global _LOCK_HANDLE
    if _LOCK_HANDLE is None:
        return
    try:
        if os.name == "nt":
            import msvcrt
            _LOCK_HANDLE.seek(0)
            msvcrt.locking(_LOCK_HANDLE.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(_LOCK_HANDLE.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass
    finally:
        _LOCK_HANDLE.close()
        _LOCK_HANDLE = None


def is_market_open() -> bool:
    now = datetime.now(MARKET_TZ)
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    t = (now.hour, now.minute)
    return MARKET_OPEN <= t < MARKET_CLOSE


def is_within_collection_window() -> bool:
    now = datetime.now(MARKET_TZ)
    if now.weekday() >= 5:
        return False
    t = (now.hour, now.minute)
    return MARKET_OPEN <= t < MARKET_CLOSE or t == FINAL_CLOSE_CHECK



def fetch_prices() -> dict[str, float]:
    data = yf.download(TICKERS, period="1d", interval="1m", progress=False, auto_adjust=True)
    prices: dict[str, float] = {}
    for ticker in TICKERS:
        try:
            price = float(data["Close"][ticker].dropna().iloc[-1])
            prices[ticker] = round(price, 4)
        except Exception as e:
            print(f"  [WARN] Could not fetch {ticker}: {e}")
            prices[ticker] = None
    return prices


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
    signal = "XST HIGH vs XQQ" if delta_pct >= SIGNAL_THRESHOLD_PCT else \
             "XQQ HIGH vs XST" if delta_pct <= -SIGNAL_THRESHOLD_PCT else ""
    return {
        "Price_XST": xst,
        "Price_XQQ": xqq,
        "Delta_$": delta_abs,
        "Delta_%": delta_pct,
        "Signal": signal,
    }


def write_log(row: dict) -> None:
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
GIT_SYNC_LOG_PATH = os.path.join(os.path.dirname(__file__), "monitor_git_sync.log")


def _append_git_sync_log(message: str) -> None:
    ts = datetime.now(MARKET_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    with open(GIT_SYNC_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")


def git_push_log() -> None:
    """Commit and push the updated monitor_log.csv to GitHub."""
    try:
        status = subprocess.run(
            ["git", "-C", REPO_ROOT, "status", "--porcelain", "src/monitor_log.csv"],
            capture_output=True,
            text=True,
            check=True,
        )
        if not status.stdout.strip():
            _append_git_sync_log("No monitor_log.csv changes to push.")
            return

        subprocess.run(
            ["git", "-C", REPO_ROOT, "add", "src/monitor_log.csv"],
            capture_output=True,
            text=True,
            check=True,
        )
        commit = subprocess.run(
            ["git", "-C", REPO_ROOT, "commit", "-m", "chore: update monitor_log.csv"],
            capture_output=True,
            text=True,
        )
        if commit.returncode != 0 and "nothing to commit" not in (commit.stdout + commit.stderr).lower():
            raise subprocess.CalledProcessError(commit.returncode, commit.args, commit.stdout, commit.stderr)

        subprocess.run(
            ["git", "-C", REPO_ROOT, "push", "origin", "main"],
            capture_output=True,
            text=True,
            check=True,
        )
        _append_git_sync_log("Pushed monitor_log.csv to origin/main.")
        print("  monitor_log.csv pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        details = (e.stderr or e.stdout or str(e)).strip()
        _append_git_sync_log(f"Git sync failed: {details}")
        print(f"  [WARN] Git push failed: {details}")


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

    def send():
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SMTP_SENDER, SMTP_PASSWORD)
                server.sendmail(SMTP_SENDER, ALERT_RECIPIENTS, msg.as_string())
            print(f"  Email alert sent to {', '.join(ALERT_RECIPIENTS)}")
        except Exception as e:
            print(f"  [WARN] Email failed: {e}")

    threading.Thread(target=send, daemon=True).start()


def send_notification(signal: str, xst: float, xqq: float, delta_pct: float) -> None:
    title = f"Switch Signal: {signal}"
    msg = f"XST.TO: ${xst}  |  XQQ.TO: ${xqq}\nDelta: {delta_pct:+.2f}%\n\nConsider rebalancing!"

    # Run in a background thread so the monitor loop isn't blocked
    def show_popup():
        try:
            ctypes.windll.user32.MessageBoxW(0, msg, title, 0x00001030)
        except Exception:
            pass

    threading.Thread(target=show_popup, daemon=True).start()


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
    threading.Thread(target=git_push_log, daemon=True).start()

    print(f"  XST.TO : {result['Price_XST']}")
    print(f"  XQQ.TO : {result['Price_XQQ']}")
    print(f"  Delta  : {result['Delta_$']} CAD  ({result['Delta_%']}%)")
    if position_pnl["Status"] == "NO COST":
        print(f"  Position P/L ({holding}): set LAST_SWITCH_COST_{holding} in .env to track win/loss.")
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
        send_notification(result["Signal"], result["Price_XST"], result["Price_XQQ"], result["Delta_%"])
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
    if not acquire_single_instance_lock():
        print("Another monitor instance is already running. Exiting.")
        return
    atexit.register(release_single_instance_lock)

    print("=== XST vs XQQ Price Monitor ===")
    print(f"Checking every 30 minutes. Log: {LOG_PATH}")
    print(f"Scheduled checks at :{CHECK_MINUTE_A:02d} and :{CHECK_MINUTE_B:02d} each hour during market hours.")
    print(f"Final close capture scheduled for {FINAL_CLOSE_CHECK[0]:02d}:{FINAL_CLOSE_CHECK[1]:02d} ET.")
    print("Auto-exits at 16:30 ET. Press Ctrl+C to stop manually.\n")

    now = datetime.now(MARKET_TZ)
    open_time = now.replace(hour=MARKET_OPEN[0], minute=MARKET_OPEN[1], second=0, microsecond=0)
    first_check_time = open_time + timedelta(minutes=FIRST_CHECK_DELAY_MINUTES)

    if is_market_open() and now >= first_check_time:
        run_check()  # run immediately only if we are already past the opening delay
    elif now.weekday() < 5 and open_time <= now < first_check_time:
        print(f"Waiting until {first_check_time.strftime('%H:%M ET')} for first validation of the day.")

    # Anchor checks to wall-clock minutes, e.g. 09:32, 10:02, 10:32...
    schedule.every().hour.at(f":{CHECK_MINUTE_A:02d}").do(run_check)
    schedule.every().hour.at(f":{CHECK_MINUTE_B:02d}").do(run_check)

    while True:
        now = datetime.now(MARKET_TZ)
        if now.weekday() < 5 and (now.hour, now.minute) >= MARKET_STOP:
            print(f"\n[{now.strftime('%Y-%m-%d %H:%M')} ET] 16:30 reached — shutting down.")
            break
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitor stopped manually.")
