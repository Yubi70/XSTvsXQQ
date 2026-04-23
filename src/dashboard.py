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
    df = pd.read_csv(LOG_PATH, encoding="utf-8-sig")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], utc=False, errors="coerce")
    df = df[df["Signal"] != "DATA ERROR"].dropna(subset=["Timestamp", "Delta_%"])
    df = df.sort_values("Timestamp").drop_duplicates(subset=["Timestamp"])
    return df


df = load_log()
latest = df.iloc[-1] if not df.empty else None

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

st.divider()

# ── Delta % chart ─────────────────────────────────────────────────────────────
st.subheader("Delta % over time")
days = st.slider("Show last N days", min_value=1, max_value=30, value=7)
cutoff = df["Timestamp"].max() - pd.Timedelta(days=days)
view = df[df["Timestamp"] >= cutoff]

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
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Recent log table ──────────────────────────────────────────────────────────
st.subheader("Recent log entries")
recent = df.tail(50).sort_values("Timestamp", ascending=False).copy()
recent["Delta_%"] = recent["Delta_%"].apply(lambda x: f"{x:+.2f}%")
recent["Delta_$"] = recent["Delta_$"].apply(lambda x: f"${x:+.4f}")


def highlight_signal(row):
    sig = str(row.get("Signal", "")).strip()
    if sig and sig not in ("", "nan"):
        return ["background-color: #ffd6d6"] * len(row)
    return [""] * len(row)


st.dataframe(
    recent[["Timestamp", "Price_XST", "Price_XQQ", "Delta_$", "Delta_%", "Signal"]]
    .style.apply(highlight_signal, axis=1),
    use_container_width=True,
    height=400,
)

# ── Auto-refresh ──────────────────────────────────────────────────────────────
st.caption(f"Auto-refreshes every {REFRESH_SECONDS}s")
time.sleep(REFRESH_SECONDS)
st.rerun()
