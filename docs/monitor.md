# XST vs XQQ Price Monitor — Documentation

## Overview
This tool automatically monitors the price spread between two Canadian ETFs —
**XST.TO** (Staples) and **XQQ.TO** (NASDAQ 100 Hedged) — and alerts you when
the gap is large enough to warrant a portfolio switch.

---

## How It Works

The project uses **cloud-only operation**: Streamlit Cloud displays the data and
the `Price Monitor` GitHub Actions workflow runs the collector. No local server
or Windows scheduled monitor is required; your computer can be off.
The dashboard reads the live log and position state from GitHub `main`, not
from your computer or a writable Streamlit server file.

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
There are no Windows popups or background email threads.
An SMTP error fails the workflow visibly before the holding is flipped, allowing
the next run to retry the alert.

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
Use **Refresh from GitHub** to clear the dashboard's live-data caches. GitHub's
raw-data service can take a few minutes to reflect a new commit.
The separate `Refresh Historical Price Data` workflow updates historical
datasets and generated analysis artifacts at 22:00 UTC on weekdays.

---

## Configuration

For cloud operation, configure these **GitHub Actions repository secrets**:
`SMTP_SENDER`, `SMTP_PASSWORD`, `ALERT_RECIPIENT`, `START_HOLDING`,
`LAST_SWITCH_COST_XST`, and `LAST_SWITCH_COST_XQQ`. The last three seed missing
state values; the committed `src/position_state.json` maintains the current
holding and cost basis between runs. A local `.env` is not uploaded to Actions.
The collector does not load `.env` at all. `SMTP_PASSWORD` is a Gmail App
Password, and `ALERT_RECIPIENT` accepts comma-separated email addresses.
Never put credentials in the position file or commit them to the repository.

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

## Remote Persistence

In cloud operation, the workflow commits and pushes `monitor_log.csv` and
`position_state.json` to `origin/main` when either changes. Failures appear in
the GitHub Actions run logs. GitHub Actions owns all collector commits; the
Python collector never invokes git or runs in a loop.

If someone edits position state during a collection run, a conflicting rebase
fails visibly rather than overwriting that edit. Resolve the conflict or rerun
the workflow from GitHub after the edit is committed.

---

## Dashboard Tabs (Web Page)

The Streamlit dashboard (`src/dashboard.py`) has five tabs:

1. **Live Monitor**
  - Real-time monitor view with delta charts, price charts, and recent log entries.
2. **Since Last Switch**
  - Compares your actual switched path versus a no-switch path since your recorded switch date.
  - Uses the latest available price per ticker even when timestamps differ, so the section remains usable outside market hours.
  - Includes **Edit switch inputs on GitHub** to update:
    - `Last switch date`
    - `Current holding` (`XST` or `XQQ`)
    - `XST trade price`
    - `XQQ trade price`
    - `Approximate amount (CAD)`
  - Shows `Switch edge (%)` in percent (2 decimal places) and `Switch edge ($)` in CAD.
  - Always displays the date/hour of the latest price used per ticker (may differ outside market hours).
  - GitHub sign-in and repository permissions protect editing. There is no
    dashboard write token and no temporary dashboard save.

3. **The Historical Theory**
  - Historical strategy results and comparison charts.
4. **Historical Asymmetric Theory**
  - Directional-threshold strategy results and downloadable report.
5. **Documentation**
  - Renders this file (`docs/monitor.md`) as formatted Markdown directly in the web page.
  - Updates automatically whenever the file is changed.

### Editing position inputs from any browser

1. Open **Since Last Switch → Edit switch inputs on GitHub**.
2. Sign in with a GitHub account allowed to edit this repository.
3. Edit `src/position_state.json`, keeping valid JSON, and commit to `main`.
4. Return to the dashboard and select **Refresh from GitHub**. If GitHub is
   still serving the previous raw file, wait a few minutes and refresh again.

Example structure (replace these illustrative values with your actual inputs):

```json
{
  "holding": "XST",
  "cost_basis": {"XST": 62.86, "XQQ": 66.14},
  "last_switch_date": "2026-04-24",
  "approx_amount_cad": 10000.0
}
```

`holding` must be `XST` or `XQQ`. Costs must be positive JSON numbers, or `null`
when unknown. `last_switch_date` uses `YYYY-MM-DD`, and `approx_amount_cad` is
a positive number. When the last two fields are absent, the dashboard retains
its existing default inputs. The collector preserves these extra fields when
updating holding/costs; `updated_at` is the collector's last state-write time,
not the trade date.

The repository and these inputs are public. Do not enter account numbers,
credentials, or other private information. No Streamlit secrets are needed.
Invalid JSON or invalid inputs produce a dashboard error with the edit link
still available for repair. A corrupt collector state fails the workflow
instead of being silently replaced with defaults.

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
  monitor_log.csv       — Rolling log of all price checks (auto-created)
  position_state.json   — Canonical position inputs committed to GitHub
  github_data.py        — Read-only GitHub live-data client and state validation
  refresh_asymmetric_theory.py — Builds asymmetric theory CSV/PNG/DOCX artifacts
  historical_asymmetric_theory.docx — Asymmetric theory report
requirements.txt        — Python dependencies
```

---

## Setup & Run

### Online setup

Open the hosted Streamlit dashboard. Keep the `Price Monitor` workflow enabled
and configure its email secrets. Deploy `main` with `app.py` or
`streamlit_app.py` on Streamlit Community Cloud; an existing deployment using
`src/dashboard.py` works too. Keep the historical-data
workflow enabled too. There is no local collector to launch.

On the Windows machine that previously ran the monitor, use an Administrator
terminal to prevent duplicate collection:

```powershell
schtasks /end /tn "XSTvsXQQ_Monitor"
schtasks /delete /tn "XSTvsXQQ_Monitor" /f
```

If the task is not running, the second command may report that there is no
running instance. Stop any manually launched monitor with Ctrl+C as well.

The Windows setup script, all-day loop, local git-sync code, desktop popup, and
their dependencies have been removed. Old generated local logs are ignored
and are not used by the dashboard. The Actions command is
`python -m src.monitor --once`; it rejects execution outside Actions.

### Optional development validation

Install dependencies with `pip install -r requirements.txt` and run
`python -m unittest discover -s tests`. Tests use temporary files and mocked
remote data; they do not send emails or edit online position state.
