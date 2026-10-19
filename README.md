# XST vs XQQ

This project provides tools and analysis for comparing XST and XQQ datasets or strategies.

## Project Structure
- `src/` — Source code for analysis and comparison
- `tests/` — Unit tests

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run analysis scripts from the `src` folder.
3. Use the hosted [Streamlit dashboard](https://xstvsxqq-lngt5gyi4yz7o7hsmiaufr.streamlit.app/).

## Cloud-only operation

Streamlit Cloud is the primary dashboard. The `Price Monitor` GitHub Actions
workflow collects prices, sends configured email alerts, and commits both the
price log and position state. No local dashboard or Windows monitor is needed.
The dev container no longer starts Streamlit or opens port 8501 automatically.

On the Windows machine that previously ran the monitor, end and disable its
scheduled task in an Administrator terminal:

```powershell
schtasks /change /tn "XSTvsXQQ_Monitor" /disable
schtasks /end /tn "XSTvsXQQ_Monitor"
```

If the monitor was also started manually, stop that process with Ctrl+C.
The cloud email configuration uses GitHub Actions secrets, not the local `.env`.
See [monitor documentation](docs/monitor.md) for required secret names and timing.
Local scripts remain available for development only.

## Streamlit Cloud
This repository now includes a root entrypoint at `app.py` (and `streamlit_app.py`) so Streamlit Cloud can discover the app without needing to target `src/dashboard.py` manually.

## Streamlit Auto-Update
The project includes `.streamlit/config.toml` with `runOnSave = true`.
When you save changes to the dashboard code, Streamlit automatically reloads the page.

## Description
Replace this section with a detailed description of your project goals and methodology.

## Monitor Delta Formula
The live monitor uses a symmetric percentage spread based on the average of XST and XQQ prices:

Delta_% = ((Price_XST - Price_XQQ) / ((Price_XST + Price_XQQ) / 2)) * 100

Details: [docs/monitor.md](docs/monitor.md)

## Dashboard Tabs
The web dashboard includes:
- `Live Monitor` tab for real-time prices/delta/logs
- `Since Last Switch` tab for switched vs no-switch comparison, including an editable input form and `Switch edge ($)` output

Worked example: see the **Dashboard Tabs (Web Page)** section in [docs/monitor.md](docs/monitor.md).

Updated chart (last 2 years): [src/delta_last2y_graph.png](src/delta_last2y_graph.png)
