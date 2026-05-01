# XST vs XQQ

This project provides tools and analysis for comparing XST and XQQ datasets or strategies.

## Project Structure
- `src/` — Source code for analysis and comparison
- `tests/` — Unit tests

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run analysis scripts from the `src` folder.
3. Run dashboard: `streamlit run src/dashboard.py`

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
