# XST vs XQQ Price Monitor — Documentation

## Overview
This tool automatically monitors the price spread between two Canadian ETFs —
**XST.TO** (Staples) and **XQQ.TO** (NASDAQ 100 Hedged) — and alerts you when
the gap is large enough to warrant a portfolio switch.

---

## How It Works

Every **30 minutes** during market hours, the monitor:
1. Fetches the latest prices for **XST.TO** and **XQQ.TO** from Yahoo Finance
2. Calculates the **delta** (% difference) using the average of both prices as denominator
3. Logs the result to `src/monitor_log.csv`
4. If the delta reaches the **5% threshold**, sends a **switch signal**

Delta formula used by the monitor:

```
Delta_% = ((Price_XST - Price_XQQ) / ((Price_XST + Price_XQQ) / 2)) * 100
```

---

## Switch Signal

A signal is triggered when:

| Signal | Condition |
|---|---|
| `XST HIGH vs XQQ` | XST is ≥ 5% higher than XQQ — consider selling XST, buying XQQ |
| `XQQ HIGH vs XST` | XQQ is ≥ 5% higher than XST — consider selling XQQ, buying XST |

When a signal fires you receive:
- **Windows popup** — stays on screen until you click OK
- **Email alert** — sent to all configured recipients

---

## Schedule

| Time (ET) | Action |
|---|---|
| **9:00 AM** Mon–Fri | Script auto-starts via Windows Task Scheduler |
| **9:30 AM** | First price check runs |
| Every **30 min** | Price check runs |
| **4:00 PM** | Market closed — checks skipped |
| **4:30 PM** | Script shuts down automatically |

---

## Configuration

All settings are stored in `.env` at the project root:

```
SMTP_SENDER=hubert.smtp@gmail.com       # Gmail account used to send alerts
SMTP_PASSWORD=xxxx xxxx xxxx xxxx       # Gmail App Password
ALERT_RECIPIENT=email1@x.com,email2@x.com  # Alert recipients (comma-separated)
```

To change the signal threshold, edit `src/monitor.py`:
```python
SIGNAL_THRESHOLD_PCT = 5.0  # trigger at 5% delta
```

---

## Output Log

Every check is appended to `src/monitor_log.csv`:

| Column | Description |
|---|---|
| `Timestamp` | Date and time of the check in ET (America/Toronto) |
| `Price_XST` | XST.TO closing price (CAD) |
| `Price_XQQ` | XQQ.TO closing price (CAD) |
| `Delta_$` | Price difference in CAD |
| `Delta_%` | Percentage difference from average price (1 decimal) |
| `Signal` | Switch signal if threshold reached, blank otherwise |

---

## Files

```
src/
  monitor.py       — Main monitoring script
  setup_task.py    — Registers the Windows Task Scheduler task
  monitor_log.csv  — Rolling log of all price checks (auto-created)
.env               — Credentials and recipients (never commit this file)
requirements.txt   — Python dependencies
```

---

## Setup & Run

**Install dependencies:**
```
pip install -r requirements.txt
```

**Run manually:**
```
.venv\Scripts\python src\monitor.py
```

**Register auto-start task** (Admin terminal required):
```
schtasks /create /tn "XSTvsXQQ_Monitor" /tr "\"c:\Python\XSTvsXQQ\.venv\Scripts\python.exe\" \"c:\Python\XSTvsXQQ\src\monitor.py\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 09:00 /rl HIGHEST /f
```

**Remove auto-start task:**
```
schtasks /delete /tn "XSTvsXQQ_Monitor" /f
```
