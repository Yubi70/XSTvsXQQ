"""Read-only presentation of the generated XUT research snapshot."""

import hashlib
import json
import math
from io import StringIO
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

if __package__:
    from .etf_research import CURVE_COLUMNS, FUNDS, PAIRS, SUMMARY_COLUMNS, SWITCH_COLUMNS, history_name
else:
    from etf_research import CURVE_COLUMNS, FUNDS, PAIRS, SUMMARY_COLUMNS, SWITCH_COLUMNS, history_name


ROOT = Path(__file__).resolve().parents[1]


def load_snapshot(root: Path = ROOT) -> tuple[dict, dict[str, str], pd.DataFrame]:
    try:
        manifest = json.loads((root / "src/etf_research_manifest.json").read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("schema_version") != 2 or manifest.get("pilot") != "XUT":
            raise ValueError("Unrecognized XUT research manifest; regenerate the current pilot.")
        expected = {
            "src/etf_research_summary.csv", "docs/etf_replacement_research.md",
            *(f"src/{history_name(ticker)}" for ticker in FUNDS),
        }
        for staples, nasdaq, _ in PAIRS:
            for years in (5, 2):
                for threshold in (3, 5):
                    key = f"{staples.replace('.', '_')}_{nasdaq.replace('.', '_')}_{years}y_{threshold}pct"
                    expected.update(f"src/etf_research_{key}_{kind}.csv" for kind in ("curve", "switches"))
        if set(manifest.get("sha256", {})) != expected:
            raise ValueError("Research manifest has missing or unexpected artifact paths.")
        texts = {}
        for relative in expected:
            data = (root / relative).read_bytes()
            if hashlib.sha256(data).hexdigest() != manifest["sha256"][relative]:
                raise ValueError(f"Research snapshot is inconsistent: {relative}. Wait for the refresh to finish.")
            texts[relative] = data.decode("utf-8")
        summary = pd.read_csv(StringIO(texts["src/etf_research_summary.csv"]))
        if list(summary.columns) != SUMMARY_COLUMNS or len(summary) != 32:
            raise ValueError("Invalid research summary schema or row count.")
        expected_rows = {
            (f"{staples}/{nasdaq}", currency, years, threshold, strategy)
            for staples, nasdaq, currency in PAIRS
            for years in (5, 2) for threshold in (3, 5)
            for strategy in ("Switching", "Defensive only", "Nasdaq only", "50/50")
        }
        if set(summary[["Pair", "Currency", "Years", "Threshold", "Strategy"]].itertuples(index=False, name=None)) != expected_rows:
            raise ValueError("Invalid or duplicate research summary scenarios.")
        numeric = [column for column in SUMMARY_COLUMNS
                   if column not in ("Pair", "Currency", "Start", "End", "Strategy", "Mean completed holding days")]
        if not summary[numeric].map(lambda value: isinstance(value, (int, float)) and math.isfinite(value)).all().all():
            raise ValueError("Non-finite research summary metrics.")
        if set(manifest["funds"]) != set(FUNDS) or len(manifest["samples"]) != 4:
            raise ValueError("Invalid research coverage metadata.")
        expected_samples = {(f"{staples}/{nasdaq}", years) for staples, nasdaq, _ in PAIRS for years in (5, 2)}
        if {(sample["pair"], sample["years"]) for sample in manifest["samples"]} != expected_samples:
            raise ValueError("Missing or duplicate research sample metadata.")
        for sample in manifest["samples"]:
            pd.Timestamp(sample["start"])
            pd.Timestamp(sample["end"])
            if sample["sessions"] < 3 or sample["one_year_observations"] < 2:
                raise ValueError("Insufficient research sample observations.")
            for field in ("daily_return_correlation", "one_year_return_correlation"):
                if not math.isfinite(sample[field]) or not -1 <= sample[field] <= 1:
                    raise ValueError("Invalid research return correlation.")
        for ticker, fund in manifest["funds"].items():
            required = {"currency", "rows", "first_session", "last_session", "missing_sessions",
                        "split_events", "description", "source", "mean_share_volume_30",
                        "mean_dollar_volume_30", "mean_share_volume_90"}
            if not isinstance(fund, dict) or not required <= fund.keys() or fund["currency"] != FUNDS[ticker]["currency"]:
                raise ValueError(f"Invalid research fund metadata: {ticker}.")
            for field in ("rows", "mean_share_volume_30", "mean_dollar_volume_30", "mean_share_volume_90"):
                if not math.isfinite(fund[field]) or fund[field] < 0:
                    raise ValueError(f"Invalid research liquidity metadata: {ticker}.")
        for field in ("methodology", "limitations", "provider", "retrieved_at"):
            if not isinstance(manifest[field], str) or not manifest[field]:
                raise ValueError(f"Missing research metadata: {field}.")
        cutoff = pd.Timestamp(manifest["cutoff"])
        if pd.isna(cutoff) or cutoff.tzinfo is not None or cutoff != cutoff.normalize():
            raise ValueError("Invalid research cutoff date.")
        for relative, text in texts.items():
            if relative.endswith("_curve.csv"):
                curve = pd.read_csv(StringIO(text))
                if list(curve.columns) != CURVE_COLUMNS or len(curve) < 3:
                    raise ValueError(f"Invalid research curve schema: {relative}.")
                dates = pd.to_datetime(curve["Date"], errors="raise")
                numeric = [column for column in CURVE_COLUMNS if column not in ("Date", "Holding")]
                if (dates.isna().any() or dates.duplicated().any() or not dates.is_monotonic_increasing
                        or (dates > cutoff).any()
                        or not curve[numeric].map(lambda value: isinstance(value, (int, float)) and math.isfinite(value)).all().all()):
                    raise ValueError(f"Invalid research curve observations: {relative}.")
            elif relative.endswith("_switches.csv"):
                if list(pd.read_csv(StringIO(text)).columns) != SWITCH_COLUMNS:
                    raise ValueError(f"Invalid research switch-log schema: {relative}.")
        report = texts["docs/etf_replacement_research.md"]
        if "## Assessment\n" not in report or "## Data coverage" not in report:
            raise ValueError("Missing research report sections.")
        return manifest, texts, summary
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, pd.errors.ParserError) as error:
        raise ValueError(f"Cannot load the XUT research snapshot: {error}") from error


def compact_table(frame: pd.DataFrame, identifier: str) -> None:
    st.markdown(
        f"<style>#{identifier} {{width:100%; table-layout:fixed; font-size:0.8rem;}}"
        f"#{identifier} th, #{identifier} td "
        "{overflow-wrap:anywhere; white-space:normal; padding:0.4rem; text-align:right;}"
        f"#{identifier} th:first-child, #{identifier} td:first-child "
        "{text-align:left;}</style>" + frame.to_html(index=False, border=0, table_id=identifier, escape=True),
        unsafe_allow_html=True,
    )


def render_research_tab() -> None:
    st.subheader("ETF Replacement Research: XUT Pilot")
    try:
        manifest, texts, summary = load_snapshot()
    except ValueError as error:
        st.error(str(error))
        st.info("Generate a complete snapshot with python -m src.etf_research, or run Refresh Historical Price Data on GitHub.")
        return
    st.caption(
        f"Completed-session cutoff: {manifest['cutoff']}. Retrieved: {manifest['retrieved_at']}. "
        "Research only: live monitoring, holdings and confirmed switches are unchanged."
    )
    cutoff = pd.Timestamp(manifest["cutoff"])
    today = pd.Timestamp.now(tz="America/Toronto").tz_localize(None).normalize()
    if cutoff > today:
        st.error("Research cutoff is in the future; regenerate the snapshot.")
        return
    if (today - cutoff).days > 7:
        st.warning("This research snapshot is more than seven calendar days old. Refresh it before relying on its results.")
    st.warning(
        "Raw ETF share prices are arbitrary, not valuations. Different share denominations and split conventions "
        "can prevent all switches. Same-close signals/execution are optimistic. "
        "XUT is utilities, not consumer staples. Both pairs retain XQQ and use CAD."
    )
    with st.expander("Methodology and data limitations"):
        st.write(manifest["methodology"])
        st.write(manifest["limitations"])
        st.caption(manifest["provider"])
    years = st.selectbox("Research horizon", [5, 2], format_func=lambda value: f"{value} years", key="research_years")
    threshold = st.selectbox("Original switching threshold", [3, 5], format_func=lambda value: f"+/-{value}%", key="research_threshold")
    for staples, nasdaq, currency in PAIRS:
        pair = f"{staples}/{nasdaq}"
        role = "pilot" if staples == "XUT.TO" else "reference"
        st.markdown(f"#### {pair} — {currency} {role}")
        sample = next(item for item in manifest["samples"] if item["pair"] == pair and item["years"] == years)
        st.caption(
            f"{sample['start']} to {sample['end']}: {sample['sessions']} common daily sessions. "
            f"Daily-return correlation: {sample['daily_return_correlation']:+.4f}; "
            f"last year: {sample['one_year_return_correlation']:+.4f} "
            f"({sample['one_year_observations']} returns)."
        )
        selected = summary[
            (summary["Pair"] == pair) & (summary["Years"] == years) & (summary["Threshold"] == threshold)
        ]
        rows = []
        for row in selected.to_dict("records"):
            rows.append({
                "Strategy": row["Strategy"].replace("Defensive only", f"{staples.removesuffix('.TO')} only"),
                "Value": f"{row['Final value']:,.2f}",
                "Return": f"{row['Return %']:+.2f}%", "CAGR": f"{row['CAGR %']:+.2f}%",
                "Drawdown": f"{row['Max drawdown %']:.2f}%", "Volatility": f"{row['Annual volatility %']:.2f}%",
                "Switches": row["Switches"], "vs 50/50": f"{row['Excess vs 50/50 (pp)']:+.2f} pp",
            })
        compact_table(pd.DataFrame(rows), f"research-{role}-summary")
        st.caption(f"All values in this section are {currency}, starting at 10,000. Negative drawdown = peak-to-trough loss.")
        key = f"{staples.replace('.', '_')}_{nasdaq.replace('.', '_')}_{years}y_{threshold}pct"
        curve_text = texts[f"src/etf_research_{key}_curve.csv"]
        switch_text = texts[f"src/etf_research_{key}_switches.csv"]
        curve = pd.read_csv(StringIO(curve_text), parse_dates=["Date"])
        switches = pd.read_csv(StringIO(switch_text))
        if list(curve.columns) != CURVE_COLUMNS or list(switches.columns) != SWITCH_COLUMNS:
            st.error(f"Invalid research curve or switch-log schema for {pair}.")
            return
        fig = go.Figure()
        for name in ("Switching", "Defensive only", "Nasdaq only", "50/50"):
            label = name.replace("Defensive only", f"{staples.removesuffix('.TO')} only")
            fig.add_trace(go.Scatter(x=curve["Date"], y=curve[name], name=label, mode="lines"))
        fig.update_layout(height=340, margin=dict(l=0, r=0, t=35, b=0),
                          yaxis_title=f"Value ({currency})", legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True, key=f"research_equity_{role}")
        premium = go.Figure(go.Scatter(
            x=curve["Date"], y=curve["Premium %"], name="Raw-price premium", mode="lines",
        ))
        for level in (threshold, -threshold):
            premium.add_hline(y=level, line_dash="dash", annotation_text=f"{level:+}%")
        premium.update_layout(height=270, margin=dict(l=0, r=0, t=15, b=0),
                              yaxis_title=f"({staples.removesuffix('.TO')} - XQQ) / XQQ %")
        st.plotly_chart(premium, use_container_width=True, key=f"research_premium_{role}")
        with st.expander(f"{pair} switch log and downloads"):
            if switches.empty:
                st.info(f"No switches under these raw-price rules. Switching equals {staples} buy-and-hold.")
            else:
                st.dataframe(switches, hide_index=True, use_container_width=True)
            st.download_button("Download daily equity/premium curve", curve_text, f"{key}_curve.csv", "text/csv", key=f"curve_{role}")
            st.download_button("Download switch log", switch_text, f"{key}_switches.csv", "text/csv", key=f"switches_{role}")
    st.markdown("#### Pilot assessment")
    st.markdown(texts["docs/etf_replacement_research.md"].split("## Assessment\n", 1)[1].split("## Data coverage", 1)[0])
    with st.expander("Daily histories, liquidity, coverage and sources"):
        rows = []
        for ticker, fund in manifest["funds"].items():
            rows.append({
                "Ticker": ticker, "Currency": fund["currency"], "Sessions": fund["rows"],
                "30d shares/day": f"{fund['mean_share_volume_30']:,.0f}",
                "30d traded/day": f"{fund['mean_dollar_volume_30']:,.0f}",
                "90d shares/day": f"{fund['mean_share_volume_90']:,.0f}",
            })
            st.caption(
                f"{ticker}: {fund['first_session']} to {fund['last_session']}; "
                f"missing sessions: {len(fund['missing_sessions'])}; "
                f"provider split events: {fund['split_events']}. {fund['description']}"
            )
            st.link_button(f"{ticker} issuer source", fund["source"])
            st.download_button(f"Download {ticker} daily history", texts[f"src/{history_name(ticker)}"], history_name(ticker), "text/csv", key=f"history_{ticker}")
        compact_table(pd.DataFrame(rows), "research-liquidity")
    st.download_button("Download full research summary", texts["src/etf_research_summary.csv"], "etf_research_summary.csv", "text/csv")
    st.download_button("Download research report", texts["docs/etf_replacement_research.md"], "etf_replacement_research.md", "text/markdown")
    st.download_button("Download coverage / integrity manifest", json.dumps(manifest, indent=2), "etf_research_manifest.json", "application/json")
