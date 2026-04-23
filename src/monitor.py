"""
monitor.py — Fetches XST.TO and XQQ.TO prices from Yahoo Finance every 30 minutes,
calculates the delta, and appends results to a rolling log (monitor_log.csv).
"""

import os
import csv
import smtplib
import schedule
import time
import atexit
from datetime import datetime
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


MARKET_TZ = pytz.timezone("America/Toronto")
MARKET_OPEN  = (9, 30)   # 9:30 AM ET
MARKET_CLOSE = (16, 0)   # 4:00 PM ET
MARKET_STOP  = (16, 30)  # script self-exits at 4:30 PM ET
LOCK_PATH = os.path.join(os.path.dirname(__file__), ".monitor.lock")
_LOCK_HANDLE = None


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
    if not is_market_open():
        now = datetime.now(MARKET_TZ)
        print(f"\n[{now.strftime('%Y-%m-%d %H:%M')} ET] Market closed — skipping check.")
        return

    ts_et = datetime.now(MARKET_TZ)
    ts = ts_et.strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"\n[{ts}] Fetching prices...")
    prices = fetch_prices()
    result = compute_delta(prices)
    row = {"Timestamp": ts, **result}
    write_log(row)

    print(f"  XST.TO : {result['Price_XST']}")
    print(f"  XQQ.TO : {result['Price_XQQ']}")
    print(f"  Delta  : {result['Delta_$']} CAD  ({result['Delta_%']}%)")
    if result["Signal"]:
        print(f"  *** SIGNAL: {result['Signal']} ***")
        send_notification(result["Signal"], result["Price_XST"], result["Price_XQQ"], result["Delta_%"])
        send_email(result["Signal"], result["Price_XST"], result["Price_XQQ"], result["Delta_%"])
    print(f"  Logged to {LOG_PATH}")


def main() -> None:
    if not acquire_single_instance_lock():
        print("Another monitor instance is already running. Exiting.")
        return
    atexit.register(release_single_instance_lock)

    print("=== XST vs XQQ Price Monitor ===")
    print(f"Checking every 30 minutes. Log: {LOG_PATH}")
    print("Auto-exits at 16:30 ET. Press Ctrl+C to stop manually.\n")

    run_check()  # run immediately on start
    schedule.every(30).minutes.do(run_check)

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
