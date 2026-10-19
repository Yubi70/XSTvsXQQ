# XST vs XQQ Price Monitor — Documentation

## Overview
This tool automatically monitors the price spread between two Canadian ETFs —
**XST.TO** (Staples) and **XQQ.TO** (NASDAQ 100 Hedged) — and alerts you when
the gap is large enough to warrant a portfolio switch.

---

## How It Works

The project uses **cloud-only operation**: Streamlit Cloud displays the data and
the `Price Monitor` GitHub Actions workflow runs the collector. No local server
or Windows scheduled monitor is required.

Approximately every **30 minutes** during market hours, the workflow:
1. Fetches the latest prices for **XST.TO** and **XQQ.TO** from Yahoo Finance
2. Calculates the **delta** (% difference) using the average of both prices as denominator
3. Logs the result to `src/monitor_log.csv`
4. If the delta reaches the directional thresholds, sends a **switch signal**

Delta formula used by the monitor:

```
Delta_% = ((Price_XST - Price_XQQ) / ((Price_XST + Price_XQQ) / 2)) * 100
```

---

## Switch Signal

A signal is triggered when:

| Signal | Condition |
|---|---|
| `XST HIGH vs XQQ` | Delta is ≥ +11.5% — consider selling XST, buying XQQ |
| `XQQ HIGH vs XST` | Delta is ≤ -7.0% — consider selling XQQ, buying XST |

When a signal fires, an **email alert** is sent to all configured recipients.
The one-shot cloud collector waits for the send attempt before exiting.
Windows popups are only available when running the optional local monitor.

### Reverse-only mode (position-aware alerts)

The monitor now tracks which ETF you currently hold and only alerts for the opposite switch:

- If holding is `XST`: only `XST HIGH vs XQQ` will alert (sell XST, buy XQQ)
- If holding is `XQQ`: only `XQQ HIGH vs XST` will alert (sell XQQ, buy XST)

After an actionable alert is triggered, the holding mode auto-flips for the next cycle.
State is stored in `src/position_state.json`.

---

## Schedule

| Time (ET) | Action |
|---|---|
| Mon–Fri, 13:00–21:30 UTC | GitHub Actions schedules checks every 30 minutes |
| During market hours | Collector fetches prices; checks outside the collection window are skipped |
| After each collection | Workflow commits the price log and position state to GitHub |

GitHub Actions scheduled runs can be delayed; exact collection times are not
guaranteed. The dashboard caches data and refreshes every 30 minutes, so
`Last updated` shows the latest loaded observation, not the current time.
The date filter only changes charts and table ranges, not that timestamp.

---

## Configuration

For cloud operation, configure these **GitHub Actions repository secrets**:
`SMTP_SENDER`, `SMTP_PASSWORD`, `ALERT_RECIPIENT`, `START_HOLDING`,
`LAST_SWITCH_COST_XST`, and `LAST_SWITCH_COST_XQQ`. The last three seed missing
state values; the committed `src/position_state.json` maintains the current
holding and cost basis between runs. A local `.env` is not uploaded to Actions.

For optional local development, the equivalent settings go in `.env`:

```
SMTP_SENDER=hubert.smtp@gmail.com       # Gmail account used to send alerts
SMTP_PASSWORD=xxxx xxxx xxxx xxxx       # Gmail App Password
ALERT_RECIPIENT=email1@x.com,email2@x.com  # Alert recipients (comma-separated)
START_HOLDING=XQQ                          # Initial holding mode if no state file exists
LAST_SWITCH_COST_XST=62.1500               # Optional: your most recent XST buy price
LAST_SWITCH_COST_XQQ=59.9000               # Optional: your most recent XQQ buy price
```

To change the signal threshold, edit `src/monitor.py`:
```python
SWITCH_UP_THRESHOLD_PCT = 11.5   # XST -> XQQ
SWITCH_DOWN_THRESHOLD_PCT = 7.0  # XQQ -> XST
```

If cost values are provided, each check prints whether your current holding is **WINNING** or **LOSING**:

```
Position P/L (XQQ) from 59.9: +1.2300 CAD (+2.05%) -> WINNING
```

On an actionable switch, the monitor automatically updates the new holding's entry cost in `src/position_state.json` using the switch-time price.

---

## Git Auto-Sync

In cloud operation, the workflow commits and pushes `monitor_log.csv` and
`position_state.json` to `origin/main` when either changes. Failures appear in
the GitHub Actions run logs.

The following behavior applies only to the optional local monitor:

- Only runs if the file has actually changed since the last commit
- Runs in a background thread so it never blocks the check cycle
- All push results (success or failure) are recorded in `src/monitor_git_sync.log`

If git is not configured or the push fails, the monitor continues running normally and logs a warning.

---

## Dashboard Tabs (Web Page)

The Streamlit dashboard (`src/dashboard.py`) now has three tabs:

1. **Live Monitor**
  - Real-time monitor view with delta charts, price charts, and recent log entries.
2. **Since Last Switch**
  - Compares your actual switched path versus a no-switch path since your recorded switch date.
  - Uses the latest available price per ticker even when timestamps differ, so the section remains usable outside market hours.
  - Includes an editable form to update:
    - `Last switch date`
    - `Current holding` (`XST` or `XQQ`)
    - `XST trade price`
    - `XQQ trade price`
    - `Approximate amount (CAD)`
  - Shows `Switch edge (%)` in percent (2 decimal places) and `Switch edge ($)` in CAD.
  - Always displays the date/hour of the latest price used per ticker (may differ outside market hours).
  - Edits made in Streamlit Cloud are local to that deployed instance; they are
    not committed to GitHub or sent to the Actions collector and may be lost on
    redeployment. Change the repository's position state to persist collector inputs.

3. **Documentation**
  - Renders this file (`docs/monitor.md`) as formatted Markdown directly in the web page.
  - Updates automatically whenever the file is changed.

The dashboard runs with Streamlit `runOnSave` enabled via `.streamlit/config.toml`, so code changes reload the web page automatically after save.

### Example Calculation

Assume your switch inputs are:

- Last switch date: `2026-04-24`
- Current holding: `XST`
- XST trade price: `62.86`
- XQQ trade price: `66.14`
- Approximate amount: `10000` CAD

And latest prices are:

- `Price_XST = 63.38`
- `Price_XQQ = 66.63`

Then:

- Switched return = `(63.38 / 62.86) - 1 = +0.827%`
- No-switch return = `(66.63 / 66.14) - 1 = +0.741%`
- Switch edge (%) = `0.827% - 0.741% = +0.09%`

For `10000` CAD:

- Switched value = `10000 * (1 + 0.00827) = 10082.70`
- No-switch value = `10000 * (1 + 0.00741) = 10074.10`
- **Switch edge ($) = 10082.70 - 10074.10 = +8.60 CAD**

The dashboard also shows a normalized per-share comparison in the caption.

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

> P/L status is printed to the console each cycle and calculated from the current holding's latest price minus its saved entry cost.

---

## Files

```
src/
  monitor.py            — Main monitoring script
  setup_task.py         — Registers the Windows Task Scheduler task
  monitor_log.csv       — Rolling log of all price checks (auto-created)
  monitor_git_sync.log  — Log of all Git push attempts (auto-created)
  position_state.json   — Current holding mode, persisted across restarts
  refresh_asymmetric_theory.py — Builds asymmetric theory CSV/PNG/DOCX artifacts
  historical_asymmetric_theory.docx — Asymmetric theory report
  .monitor.lock         — Single-instance lock file (auto-managed, do not delete)
.env                    — Credentials and recipients (never commit this file)
requirements.txt        — Python dependencies
```

> **Single-instance lock:** The monitor creates `.monitor.lock` on startup and holds an exclusive file lock while running. If you try to start a second instance it will exit immediately with the message *"Another monitor instance is already running."* The lock is released automatically on exit.

---

## Setup & Run

### Cloud-only use

Open the hosted Streamlit dashboard. Keep the `Price Monitor` workflow enabled
and configure its email secrets. Do not launch a second local collector.

On the Windows machine that previously ran the monitor, use an Administrator
terminal to prevent duplicate collection:

```powershell
schtasks /change /tn "XSTvsXQQ_Monitor" /disable
schtasks /end /tn "XSTvsXQQ_Monitor"
```

If the task is not running, the second command may report that there is no
running instance. Stop any manually launched monitor with Ctrl+C as well.

### Optional local development

The commands below are retained for development, not normal cloud operation.

**Install dependencies:**
```
pip install -r requirements.txt
```

**Build asymmetric theory artifacts (+11.5% / -7.0%):**
```
python src/refresh_asymmetric_theory.py
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
