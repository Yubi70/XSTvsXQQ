# XST vs XQQ

Cloud-hosted price monitoring and strategy comparisons for XST.TO and XQQ.TO.

## Project Structure
- `src/` — Source code for analysis and comparison
- `tests/` — Unit tests

## Fully remote operation

Your computer can be turned off:

- [Streamlit dashboard](https://xstvsxqq-lngt5gyi4yz7o7hsmiaufr.streamlit.app/):
  displays the live price log and position state directly from GitHub `main`.
- **Price Monitor** in GitHub Actions: collects prices, sends email alerts,
  and commits the price log and position state.
- **Refresh Historical Price Data** in GitHub Actions: updates historical
  datasets and analysis artifacts on weekdays.
- **Position editing**: use **Edit switch inputs on GitHub** in the dashboard.
  GitHub sign-in and repository permissions control who can commit changes.
  The dashboard never writes to a temporary server file and needs no write token.

Data is cached for 30 minutes. Use **Refresh from GitHub** after committing a
position edit. GitHub may take a few minutes to serve newly committed raw data.
Network or data errors are displayed rather than silently loading a local copy.

### One-time migration from the old Windows monitor

On the Windows machine that previously ran the collector, stop it and remove
its scheduled task in an Administrator terminal:

```powershell
schtasks /end /tn "XSTvsXQQ_Monitor"
schtasks /delete /tn "XSTvsXQQ_Monitor" /f
```

If the monitor was started manually, stop that process with Ctrl+C as well.
An absent or inactive task can report that there is nothing to stop.
The collector no longer supports a local loop, popup, lock, git push, or `.env`.
Its command-line entrypoint rejects execution outside GitHub Actions.

## Streamlit Cloud
Deploy this repository's `main` branch on Streamlit Community Cloud using
`app.py` (or `streamlit_app.py`) as the entrypoint. Keep both GitHub Actions
workflows enabled. Configure the email secrets in GitHub, not on a computer.
See [monitor documentation](docs/monitor.md) for secret names, position fields,
schedule limitations, and troubleshooting. No new Streamlit secrets are required.

## Development and tests

Development tools are optional; they are not needed to operate the hosted app.
Install dependencies with `pip install -r requirements.txt`, then run
`python -m unittest discover -s tests`.

## Monitor Delta Formula
The live monitor uses a symmetric percentage spread based on the average of XST and XQQ prices:

Delta_% = ((Price_XST - Price_XQQ) / ((Price_XST + Price_XQQ) / 2)) * 100

Details: [docs/monitor.md](docs/monitor.md)

## Dashboard Tabs
The web dashboard includes:
- `Live Monitor` tab for real-time prices/delta/logs
- `Since Last Switch` tab for switched vs no-switch comparison, a GitHub edit link, and `Switch edge ($)` output

Worked example: see the **Dashboard Tabs (Web Page)** section in [docs/monitor.md](docs/monitor.md).

Updated chart (last 2 years): [src/delta_last2y_graph.png](src/delta_last2y_graph.png)
