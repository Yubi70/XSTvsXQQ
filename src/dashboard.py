"""
dashboard.py — Streamlit live dashboard for the XST vs XQQ monitor.
Reads monitor_log.csv and auto-refreshes every 30 seconds.

Run with:
    .venv/Scripts/streamlit run src/dashboard.py
"""

import time
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

LOG_PATH = Path(__file__).parent / "monitor_log.csv"
GIT_SYNC_LOG_PATH = Path(__file__).parent / "monitor_git_sync.log"
STATE_PATH = Path(__file__).parent / "position_state.json"
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


@st.cache_data(ttl=REFRESH_SECONDS)
def load_last_git_sync_status() -> str:
    if not GIT_SYNC_LOG_PATH.exists():
        return ""

    try:
        last_line = ""
        with open(GIT_SYNC_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line.strip()
        if not last_line:
            return "Last Git Sync: sync log is empty"
        return f"Last Git Sync: {last_line}"
    except Exception as e:
        return f"Last Git Sync: could not read sync log ({e})"


@st.cache_data(ttl=REFRESH_SECONDS)
def load_position_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def save_position_state(state: dict) -> tuple[bool, str]:
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=True, indent=2)
        load_position_state.clear()
        return True, "Saved"
    except Exception as e:
        return False, str(e)


def parse_price_text(value: str) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return round(float(text), 4)
    except ValueError:
        return None


def parse_amount_text(value: str) -> float | None:
    parsed = parse_price_text(value)
    if parsed is None or parsed <= 0:
        return None
    return parsed


def get_latest_price_snapshot(price_col: str) -> tuple[float | None, pd.Timestamp | None]:
    if df.empty or price_col not in df.columns:
        return None, None

    snap = df.dropna(subset=[price_col]).sort_values("Timestamp")
    if snap.empty:
        return None, None

    row = snap.iloc[-1]
    return float(row[price_col]), pd.to_datetime(row["Timestamp"], errors="coerce")


df = load_log()
latest_raw = df.iloc[-1] if not df.empty else None
valid_df = df[df["Signal"] != "DATA ERROR"].dropna(
    subset=["Price_XST", "Price_XQQ", "Delta_$", "Delta_%"]
)
latest = valid_df.iloc[-1] if not valid_df.empty else None
git_sync_status = load_last_git_sync_status()
if not git_sync_status:
    if latest_raw is not None:
        latest_ts = str(latest_raw["Timestamp"]).split(".")[0]
        git_sync_status = f"Last Git Sync: inferred from latest data update at {latest_ts}"
    else:
        git_sync_status = "Last Git Sync: waiting for first data update"


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


def render_live_monitor_tab() -> None:
    st.caption(git_sync_status)

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
    st.subheader("Delta % over time")
    if filtered_valid_df.empty:
        st.info("No valid data available for chart yet.")
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


def render_since_switch_tab() -> None:
    st.subheader("Since Last Switch: Switched vs No-Switch")
    st.caption(
        "This view uses the latest available price for each ticker independently, "
        "so calculations still work outside business hours even when timestamps differ."
    )
    state = load_position_state()

    if not state:
        state = {
            "holding": "XST",
            "last_switch_date": "",
            "cost_basis": {"XST": None, "XQQ": None},
            "approx_amount_cad": 10000.0,
        }

    state_holding = str(state.get("holding", "XST")).strip().upper()
    if state_holding not in ("XST", "XQQ"):
        state_holding = "XST"
    state_switch_date_text = str(state.get("last_switch_date", "")).strip()
    state_switch_date = pd.to_datetime(state_switch_date_text, errors="coerce")
    if pd.notna(state_switch_date):
        default_switch_date = state_switch_date.date()
    elif not valid_df.empty:
        default_switch_date = valid_df["Timestamp"].max().date()
    else:
        default_switch_date = pd.Timestamp.now().date()

    state_cost_basis = state.get("cost_basis") or {}
    state_xst_text = "" if state_cost_basis.get("XST") is None else f"{float(state_cost_basis.get('XST')):.4f}"
    state_xqq_text = "" if state_cost_basis.get("XQQ") is None else f"{float(state_cost_basis.get('XQQ')):.4f}"
    state_amount = pd.to_numeric(state.get("approx_amount_cad"), errors="coerce")
    state_amount_text = "10000" if pd.isna(state_amount) or float(state_amount) <= 0 else f"{float(state_amount):.2f}"

    with st.expander("Edit switch inputs", expanded=False):
        with st.form("switch_inputs_form"):
            fcol1, fcol2 = st.columns(2)
            form_switch_date = fcol1.date_input("Last switch date", value=default_switch_date)
            form_holding = fcol2.selectbox(
                "Current holding",
                options=["XST", "XQQ"],
                index=0 if state_holding == "XST" else 1,
            )
            pcol1, pcol2 = st.columns(2)
            form_xst = pcol1.text_input("XST trade price", value=state_xst_text, placeholder="e.g. 62.86")
            form_xqq = pcol2.text_input("XQQ trade price", value=state_xqq_text, placeholder="e.g. 66.14")
            form_amount = st.text_input("Approximate amount (CAD)", value=state_amount_text, placeholder="e.g. 10000")
            submitted = st.form_submit_button("Save switch inputs", width="stretch")

        if submitted:
            new_xst = parse_price_text(form_xst)
            new_xqq = parse_price_text(form_xqq)
            new_amount = parse_amount_text(form_amount)
            if new_xst is None or new_xqq is None:
                st.error("Please enter valid numeric prices for both XST and XQQ.")
            elif new_amount is None:
                st.error("Please enter a valid positive approximate amount in CAD.")
            else:
                updated_state = {
                    "holding": form_holding,
                    "last_switch_date": form_switch_date.isoformat(),
                    "cost_basis": {
                        "XST": new_xst,
                        "XQQ": new_xqq,
                    },
                    "approx_amount_cad": new_amount,
                    "updated_at": pd.Timestamp.now(tz="America/Toronto").strftime("%Y-%m-%d %H:%M:%S %Z"),
                }
                ok, msg = save_position_state(updated_state)
                if ok:
                    st.success("Switch inputs saved to position_state.json")
                    state = updated_state
                else:
                    st.error(f"Could not save position_state.json: {msg}")

    holding = str(state.get("holding", "")).strip().upper()
    if holding not in ("XST", "XQQ"):
        st.warning("State holding is missing or invalid. Expected XST or XQQ.")
        return

    cost_basis = state.get("cost_basis") or {}
    current_ticker = holding
    previous_ticker = "XQQ" if current_ticker == "XST" else "XST"
    current_entry = pd.to_numeric(cost_basis.get(current_ticker), errors="coerce")
    previous_entry = pd.to_numeric(cost_basis.get(previous_ticker), errors="coerce")

    if pd.isna(current_entry) or pd.isna(previous_entry):
        st.warning(
            "Missing entry prices in position state. Please set both cost_basis values "
            "(XST and XQQ) to evaluate switched vs no-switch."
        )
        return

    current_now, current_now_ts = get_latest_price_snapshot(f"Price_{current_ticker}")
    previous_now, previous_now_ts = get_latest_price_snapshot(f"Price_{previous_ticker}")

    if current_now is None or previous_now is None:
        st.info("No latest price snapshot yet for one or both tickers.")
        return

    switched_ret = (current_now / float(current_entry)) - 1.0
    no_switch_ret = (previous_now / float(previous_entry)) - 1.0
    edge = switched_ret - no_switch_ret
    approx_amount = pd.to_numeric(state.get("approx_amount_cad"), errors="coerce")
    if pd.isna(approx_amount) or float(approx_amount) <= 0:
        approx_amount = 10000.0

    switched_value_amt = float(approx_amount) * (1.0 + switched_ret)
    no_switch_value_amt = float(approx_amount) * (1.0 + no_switch_ret)
    edge_cad = switched_value_amt - no_switch_value_amt

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Switched return", f"{switched_ret * 100:+.3f}%")
    c2.metric("No-switch return", f"{no_switch_ret * 100:+.3f}%")
    c3.metric("Switch edge", f"{edge * 100:+.3f} pp")
    c4.metric("Switch edge ($)", f"${edge_cad:+,.2f}")

    switched_value = (float(previous_entry) / float(current_entry)) * current_now
    no_switch_value = previous_now
    extra_cad = switched_value - no_switch_value

    st.caption(
        f"For approx ${float(approx_amount):,.2f} invested at switch time: "
        f"switched value ${switched_value_amt:,.2f} vs no-switch ${no_switch_value_amt:,.2f} (edge {edge_cad:+,.2f} CAD). "
    )
    st.caption(
        f"Normalized to selling 1 share of {previous_ticker} at ${float(previous_entry):.2f} on switch day: "
        f"switched path is {extra_cad:+.4f} CAD versus no-switch."
    )
    if pd.notna(current_now_ts) and pd.notna(previous_now_ts):
        current_ts_text = pd.Timestamp(current_now_ts).strftime("%Y-%m-%d %H:%M:%S")
        previous_ts_text = pd.Timestamp(previous_now_ts).strftime("%Y-%m-%d %H:%M:%S")
        st.caption(
            f"Latest prices used: {current_ticker} at {current_ts_text} ET and "
            f"{previous_ticker} at {previous_ts_text} ET (timestamps may differ outside market hours)."
        )

    if edge > 0:
        st.success("Switching was better than not switching so far.")
    elif edge < 0:
        st.warning("Not switching would have been better so far.")
    else:
        st.info("Switched and no-switch paths are currently tied.")

    switch_date_text = str(state.get("last_switch_date", "")).strip()
    switch_ts = pd.to_datetime(switch_date_text, errors="coerce") if switch_date_text else pd.NaT
    if pd.notna(switch_ts):
        since_df = valid_df[valid_df["Timestamp"] >= switch_ts].copy()
        if not since_df.empty:
            switched_index = (since_df[f"Price_{current_ticker}"] / float(current_entry)) * 100
            no_switch_index = (since_df[f"Price_{previous_ticker}"] / float(previous_entry)) * 100

            comp_fig = go.Figure()
            comp_fig.add_trace(go.Scatter(
                x=since_df["Timestamp"],
                y=switched_index,
                mode="lines",
                name=f"Switched ({current_ticker})",
                line=dict(color="#2E8B57", width=2),
            ))
            comp_fig.add_trace(go.Scatter(
                x=since_df["Timestamp"],
                y=no_switch_index,
                mode="lines",
                name=f"No-switch ({previous_ticker})",
                line=dict(color="#FF8C00", width=2),
            ))
            comp_fig.add_hline(y=100, line_dash="dot", line_color="gray")
            comp_fig.update_layout(
                height=360,
                margin=dict(l=0, r=0, t=10, b=0),
                yaxis_title="Indexed value (100 = switch date)",
                xaxis_title="Timestamp (ET)",
            )
            st.plotly_chart(comp_fig, width="stretch")
        else:
            st.info("No valid rows available after last_switch_date yet.")


tab_live, tab_since_switch = st.tabs(["Live Monitor", "Since Last Switch"])
with tab_live:
    render_live_monitor_tab()

with tab_since_switch:
    render_since_switch_tab()

# ── Auto-refresh ──────────────────────────────────────────────────────────────
st.caption(f"Auto-refreshes every {REFRESH_SECONDS}s")
time.sleep(REFRESH_SECONDS)
st.rerun()
