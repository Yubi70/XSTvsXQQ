"""
dashboard.py — Streamlit live dashboard for the XST vs XQQ monitor.
Reads monitor_log.csv and auto-refreshes every 30 seconds.

Run with:
    .venv/Scripts/streamlit run src/dashboard.py
"""

import time
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

LOG_PATH = Path(__file__).parent / "monitor_log.csv"
SIGNAL_THRESHOLD = 5.0
REFRESH_SECONDS = 30

st.set_page_config(page_title="XST vs XQQ Monitor", layout="wide")
st.title("XST vs XQQ Live Monitor")


@st.cache_data(ttl=REFRESH_SECONDS)
def load_log() -> pd.DataFrame:
    # Skip malformed rows so one bad write never crashes the dashboard.
    df = pd.read_csv(LOG_PATH, encoding="utf-8-sig", on_bad_lines="skip")
    df["Price_XST"] = pd.to_numeric(df["Price_XST"], errors="coerce")
    df["Price_XQQ"] = pd.to_numeric(df["Price_XQQ"], errors="coerce")
    df["Delta_$"] = pd.to_numeric(df["Delta_$"], errors="coerce")
    df["Delta_%"] = pd.to_numeric(df["Delta_%"], errors="coerce")
    # Normalize mixed formats like "YYYY-mm-dd HH:MM:SS" and "... EDT".
    ts_text = df["Timestamp"].astype(str).str.replace(r"\s+[A-Z]{3}$", "", regex=True)
    df["Timestamp"] = pd.to_datetime(ts_text, utc=False, errors="coerce")
    df = df.dropna(subset=["Timestamp"])
    df = df.sort_values("Timestamp").drop_duplicates(subset=["Timestamp"], keep="last")
    return df


df = load_log()
latest_raw = df.iloc[-1] if not df.empty else None
valid_df = df[df["Signal"] != "DATA ERROR"].dropna(
    subset=["Price_XST", "Price_XQQ", "Delta_$", "Delta_%"]
)
latest = valid_df.iloc[-1] if not valid_df.empty else None

# ── Daily tendency indicators ─────────────────────────────────────────────────
def render_tendency(label: str, change: float, unit_suffix: str, threshold: float) -> None:
    if change > threshold:
        trend_icon, trend_text, trend_color = "▲", "Up", "#138A36"
    elif change < -threshold:
        trend_icon, trend_text, trend_color = "▼", "Down", "#B22222"
    else:
        trend_icon, trend_text, trend_color = "▶", "Flat", "#666666"

    st.markdown(
        f"<div style='font-size:1.02rem; font-weight:600; color:{trend_color};'>"
        f"{label}: {trend_icon} {trend_text} ({change:+.2f}{unit_suffix} vs previous close)</div>",
        unsafe_allow_html=True,
    )


if not valid_df.empty:
    today_start = valid_df["Timestamp"].max().floor('D')
    today_df = valid_df[valid_df["Timestamp"] >= today_start]
    prev_day_df = valid_df[valid_df["Timestamp"] < today_start]
    if not today_df.empty and not prev_day_df.empty:
        prev_close_row = prev_day_df.iloc[-1]
        last_row = today_df.iloc[-1]

        render_tendency(
            "Day delta tendency",
            float(last_row["Delta_%"]) - float(prev_close_row["Delta_%"]),
            " pts",
            0.05,
        )
        render_tendency(
            "Day XST tendency",
            float(last_row["Price_XST"]) - float(prev_close_row["Price_XST"]),
            " CAD",
            0.01,
        )
        render_tendency(
            "Day XQQ tendency",
            float(last_row["Price_XQQ"]) - float(prev_close_row["Price_XQQ"]),
            " CAD",
            0.01,
        )
    else:
        st.info("Day tendencies: waiting for both today's data and previous close data.")
else:
    st.info("Day tendencies: no valid data yet.")

# ── Top metrics ───────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
if latest is not None:
    col1.metric("XST.TO", f"${float(latest['Price_XST']):.2f}")
    col2.metric("XQQ.TO", f"${float(latest['Price_XQQ']):.2f}")
    delta_val = float(latest["Delta_%"])
    col3.metric("Delta %", f"{delta_val:+.2f}%")
    col4.metric("Last updated", str(latest["Timestamp"]).split(".")[0])

    signal = str(latest["Signal"]).strip()
    if signal and signal not in ("", "nan"):
        st.error(f"SWITCH SIGNAL: {signal}", icon="🚨")
    else:
        st.success("No active signal — within normal range.")
else:
    st.warning("No valid price rows yet. Waiting for next successful fetch.")

if latest_raw is not None and str(latest_raw.get("Signal", "")).strip() == "DATA ERROR":
    ts_txt = str(latest_raw["Timestamp"]).split(".")[0]
    st.warning(f"Latest check at {ts_txt} returned DATA ERROR. Dashboard metrics show the most recent valid row.")

# ── Date filter ───────────────────────────────────────────────────────────────
filter_options = ["Today", "Last week", "Last month", "All time"]

query_filter = st.query_params.get("filter", "Last week")
if isinstance(query_filter, list):
    query_filter = query_filter[0] if query_filter else "Last week"
if query_filter not in filter_options:
    query_filter = "Last week"

if "date_filter" not in st.session_state or st.session_state["date_filter"] not in filter_options:
    st.session_state["date_filter"] = query_filter


def sync_filter_query_params() -> None:
    st.query_params["filter"] = st.session_state["date_filter"]


def set_date_filter(value: str) -> None:
    st.session_state["date_filter"] = value
    st.query_params["filter"] = value


quick_filter_cols = st.columns(4)
quick_filter_labels = ["Today", "Last week", "Last month", "All time"]
for col, label in zip(quick_filter_cols, quick_filter_labels):
    col.button(
        label,
        key=f"quick_filter_{label.replace(' ', '_').lower()}",
        width="stretch",
        on_click=set_date_filter,
        args=(label,),
    )

date_filter = st.selectbox(
    "Date filter",
    options=filter_options,
    key="date_filter",
    on_change=sync_filter_query_params,
)

if st.query_params.get("filter") != date_filter:
    st.query_params["filter"] = date_filter

if not df.empty:
    end_ts = df["Timestamp"].max()
    start_ts = None
    if date_filter == "Today":
        start_ts = end_ts.normalize()
    elif date_filter == "Last week":
        start_ts = end_ts - pd.Timedelta(days=7)
    elif date_filter == "Last month":
        start_ts = end_ts - pd.Timedelta(days=30)

    if start_ts is not None:
        filtered_df = df[df["Timestamp"] >= start_ts]
        filtered_valid_df = valid_df[valid_df["Timestamp"] >= start_ts]
    else:
        filtered_df = df
        filtered_valid_df = valid_df
else:
    filtered_df = df
    filtered_valid_df = valid_df

st.divider()

# ── Delta % chart ─────────────────────────────────────────────────────────────
st.subheader("Delta % over time")
if filtered_valid_df.empty:
    st.info("No valid data available for chart yet.")
    view = filtered_valid_df
else:
    view = filtered_valid_df

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=view["Timestamp"],
    y=view["Delta_%"],
    mode="lines+markers",
    name="Delta %",
    line=dict(color="#1f77b4", width=1.8),
    marker=dict(size=3),
))
fig.add_hline(y=SIGNAL_THRESHOLD, line_dash="dash", line_color="red",
              annotation_text=f"+{SIGNAL_THRESHOLD}% threshold")
fig.add_hline(y=-SIGNAL_THRESHOLD, line_dash="dash", line_color="red",
              annotation_text=f"-{SIGNAL_THRESHOLD}% threshold")
fig.add_hline(y=0, line_color="gray", line_width=0.8)
fig.update_layout(
    height=420,
    margin=dict(l=0, r=0, t=20, b=0),
    yaxis_title="Delta %",
    xaxis_title="Timestamp (ET)",
)
st.plotly_chart(fig, width="stretch")

st.divider()

# ── Ticker prices chart ───────────────────────────────────────────────────────
st.subheader("Ticker prices over time")
if filtered_valid_df.empty:
    st.info("No valid data available for ticker price chart yet.")
else:
    price_fig = go.Figure()
    price_fig.add_trace(go.Scatter(
        x=filtered_valid_df["Timestamp"],
        y=filtered_valid_df["Price_XST"],
        mode="lines+markers",
        name="XST.TO",
        line=dict(color="#2E8B57", width=2),
        marker=dict(size=3),
        hovertemplate="%{x}<br>XST.TO: $%{y:.2f}<extra></extra>",
    ))
    price_fig.add_trace(go.Scatter(
        x=filtered_valid_df["Timestamp"],
        y=filtered_valid_df["Price_XQQ"],
        mode="lines+markers",
        name="XQQ.TO",
        line=dict(color="#FF8C00", width=2),
        marker=dict(size=3),
        hovertemplate="%{x}<br>XQQ.TO: $%{y:.2f}<extra></extra>",
    ))
    price_fig.update_layout(
        height=380,
        margin=dict(l=0, r=0, t=20, b=0),
        yaxis_title="Price (CAD)",
        xaxis_title="Timestamp (ET)",
        yaxis=dict(tickprefix="$", tickformat=".2f"),
    )
    st.plotly_chart(price_fig, width="stretch")

st.divider()

# ── Recent log table ──────────────────────────────────────────────────────────
st.subheader("Recent log entries")
recent = filtered_df.tail(50).sort_values("Timestamp", ascending=False).copy()
recent["Price_XST"] = recent["Price_XST"].apply(
    lambda x: "" if pd.isna(x) else f"${x:.2f}"
)
recent["Price_XQQ"] = recent["Price_XQQ"].apply(
    lambda x: "" if pd.isna(x) else f"${x:.2f}"
)
recent["Delta_%"] = recent["Delta_%"].apply(
    lambda x: "" if pd.isna(x) else f"{x:+.2f}%"
)
recent["Delta_$"] = recent["Delta_$"].apply(
    lambda x: "" if pd.isna(x) else f"${x:+.2f}"
)


def highlight_signal(row):
    sig = str(row.get("Signal", "")).strip()
    if sig and sig not in ("", "nan"):
        return ["background-color: #ffd6d6"] * len(row)
    return [""] * len(row)


st.dataframe(
    recent[["Timestamp", "Price_XST", "Price_XQQ", "Delta_$", "Delta_%", "Signal"]]
    .style.apply(highlight_signal, axis=1),
    width="stretch",
    height=400,
)

# ── Auto-refresh ──────────────────────────────────────────────────────────────
st.caption(f"Auto-refreshes every {REFRESH_SECONDS}s")
time.sleep(REFRESH_SECONDS)
st.rerun()
