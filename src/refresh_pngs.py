from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd


SRC = Path(__file__).parent

XST_HIST = SRC / "XST Historical Data (1).csv"
XQQ_HIST = SRC / "XQQ Historical Data (1).csv"


def load_hist(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["Date", "Price"])
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"].astype(str).str.replace(",", ""), errors="coerce")
    return df.dropna().sort_values("Date").reset_index(drop=True)


def load_merged() -> pd.DataFrame:
    xst = load_hist(XST_HIST).rename(columns={"Price": "Price_XST"})
    xqq = load_hist(XQQ_HIST).rename(columns={"Price": "Price_XQQ"})
    df = pd.merge(xst, xqq, on="Date", how="inner")
    avg = (df["Price_XST"] + df["Price_XQQ"]) / 2
    df["Delta %"] = ((df["Price_XST"] - df["Price_XQQ"]) / avg) * 100
    return df.sort_values("Date").reset_index(drop=True)


def windowed(df: pd.DataFrame, years: int) -> pd.DataFrame:
    cutoff = df["Date"].max() - pd.DateOffset(years=years)
    return df[df["Date"] >= cutoff].copy().reset_index(drop=True)


def pct_change_since_start(series: pd.Series) -> float:
    if len(series) < 2 or series.iloc[0] == 0:
        return 0.0
    return (series.iloc[-1] / series.iloc[0] - 1.0) * 100.0


def change_caption(df: pd.DataFrame) -> str:
    xst_chg = pct_change_since_start(df["Price_XST"])
    xqq_chg = pct_change_since_start(df["Price_XQQ"])
    start = df["Date"].iloc[0].date()
    return f"Change since {start}: XST {xst_chg:+.2f}% | XQQ {xqq_chg:+.2f}%"


def compute_switches(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    holding = "XST"
    events = []
    for _, row in df.iterrows():
        d = row["Delta %"]
        if d >= threshold and holding == "XST":
            events.append((row["Date"], row["Delta %"], "XQQ"))
            holding = "XQQ"
        elif d <= -threshold and holding == "XQQ":
            events.append((row["Date"], row["Delta %"], "XST"))
            holding = "XST"
    return pd.DataFrame(events, columns=["Date", "Delta %", "SwitchTo"])


def plot_switch_signals(df: pd.DataFrame, years: int, out_name: str) -> None:
    sw3 = compute_switches(df, 3.0)
    sw5 = compute_switches(df, 5.0)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df["Date"], df["Delta %"], color="#1f77b4", linewidth=1.4, label="Delta %")
    ax.axhline(0, color="gray", linestyle=":", linewidth=1.0)
    ax.axhline(3, color="#ff9800", linestyle="--", linewidth=1.0, label="+/-3% threshold")
    ax.axhline(-3, color="#ff9800", linestyle="--", linewidth=1.0)
    ax.axhline(5, color="#d32f2f", linestyle="--", linewidth=1.0, label="+/-5% threshold")
    ax.axhline(-5, color="#d32f2f", linestyle="--", linewidth=1.0)

    if not sw3.empty:
        ax.scatter(sw3["Date"], sw3["Delta %"], s=45, c="#ff9800", marker="o", label="3% switches", zorder=4)
    if not sw5.empty:
        ax.scatter(sw5["Date"], sw5["Delta %"], s=70, c="#d32f2f", marker="^", label="5% switches", zorder=5)

    ax.set_title(
        f"XST vs XQQ Switch Signals - Last {years} Years\n"
        f"{change_caption(df)}",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_ylabel("Delta % (symmetric)")
    ax.set_xlabel("Date")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    ax.legend(loc="upper left", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)

    out = SRC / out_name
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}")


def plot_real_switches(years: int, out_name: str) -> None:
    src3 = SRC / f"real_switches_last{years}y_3pct.csv"
    src5 = SRC / f"real_switches_last{years}y_5pct.csv"
    df3 = pd.read_csv(src3, parse_dates=["Date"])
    df5 = pd.read_csv(src5, parse_dates=["Date"])
    hist = windowed(load_merged(), years)

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    for ax, data, label, color in [
        (axes[0], df3, "3% threshold", "#1f77b4"),
        (axes[1], df5, "5% threshold", "#d32f2f"),
    ]:
        x = range(1, len(data) + 1)
        y = pd.to_numeric(data["Signed premium %"], errors="coerce")
        bars = ax.bar(x, y, color=color, alpha=0.85)
        ax.axhline(0, color="gray", linestyle=":", linewidth=1)
        ax.set_ylabel("Signed premium %")
        ax.set_title(f"{label} ({len(data)} real switches)", fontsize=10, fontweight="bold")
        ax.grid(axis="y", linestyle=":", alpha=0.35)
        ax.spines[["top", "right"]].set_visible(False)
        for i, (bar, val) in enumerate(zip(bars, y), start=1):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + (0.15 if val >= 0 else -0.15),
                f"{val:+.2f}%",
                ha="center",
                va="bottom" if val >= 0 else "top",
                fontsize=8,
            )

    axes[1].set_xlabel("Switch #")
    axes[1].set_xticks(range(1, max(len(df3), len(df5)) + 1))

    fig.suptitle(
        f"Real Switch Premiums - Last {years} Years\n"
        f"{change_caption(hist)}",
        fontsize=12,
        fontweight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    out = SRC / out_name
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}")


def plot_delta_last2y(df2y: pd.DataFrame, out_name: str) -> None:
    idx_xst = df2y["Price_XST"] / df2y["Price_XST"].iloc[0] * 100
    idx_xqq = df2y["Price_XQQ"] / df2y["Price_XQQ"].iloc[0] * 100

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df2y["Date"], idx_xst, color="#2E8B57", linewidth=1.8, label="XST (indexed)")
    ax.plot(df2y["Date"], idx_xqq, color="#FF8C00", linewidth=1.8, label="XQQ (indexed)")
    ax.axhline(100, color="gray", linestyle=":", linewidth=1)
    ax.set_ylabel("Indexed value (100=start)")
    ax.set_xlabel("Date")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left")
    ax.set_title(
        "XST vs XQQ - Last 2 Years Indexed Performance\n"
        f"{change_caption(df2y)}",
        fontsize=12,
        fontweight="bold",
    )

    out = SRC / out_name
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}")


def plot_switch_duration() -> None:
    csv = SRC / "real_switches_last5y_3pct.csv"
    out = SRC / "switch_duration_graph.png"
    df = pd.read_csv(csv, parse_dates=["Date"]).sort_values("Date").reset_index(drop=True)
    hist5 = windowed(load_merged(), 5)

    durations = []
    for i in range(len(df) - 1):
        days = (df.loc[i + 1, "Date"] - df.loc[i, "Date"]).days
        label = f"#{df.loc[i,'Switch #']}->#{df.loc[i+1,'Switch #']}\n{df.loc[i,'Date'].strftime('%Y-%m-%d')}"
        durations.append({"label": label, "days": days, "from": df.loc[i, "From"]})

    dur_df = pd.DataFrame(durations)
    avg_days = dur_df["days"].mean()
    avg_xst_days = dur_df.loc[dur_df["from"] == "XST", "days"].mean()
    avg_xqq_days = dur_df.loc[dur_df["from"] == "XQQ", "days"].mean()

    c_xst = "#1f77b4"
    c_xqq = "#ff7f0e"
    colours = [c_xst if row["from"] == "XST" else c_xqq for _, row in dur_df.iterrows()]

    fig, ax = plt.subplots(figsize=(14, 6))
    bars = ax.bar(range(len(dur_df)), dur_df["days"], color=colours, edgecolor="white", linewidth=0.8)

    for bar, days in zip(bars, dur_df["days"]):
        x = bar.get_x() + bar.get_width() / 2
        if days >= 40:
            ax.text(x, days / 2, f"{days}d", ha="center", va="center", fontsize=9, fontweight="bold", color="white")
        else:
            ax.text(x, days + 4, f"{days}d", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#333333")

    ax.axhline(avg_days, color="crimson", linestyle="--", linewidth=1.6, label=f"Overall avg {avg_days:.0f}d")
    if not pd.isna(avg_xst_days):
        ax.axhline(avg_xst_days, color=c_xst, linestyle=":", linewidth=1.3, label=f"XST avg {avg_xst_days:.0f}d")
    if not pd.isna(avg_xqq_days):
        ax.axhline(avg_xqq_days, color=c_xqq, linestyle=":", linewidth=1.3, label=f"XQQ avg {avg_xqq_days:.0f}d")

    ax.set_xticks(range(len(dur_df)))
    ax.set_xticklabels(dur_df["label"], fontsize=8.5)
    ax.set_ylabel("Holding duration (calendar days)")
    ax.set_title(
        "XST vs XQQ - Duration Between Switches (3% threshold, last 5 years)\n"
        f"{change_caption(hist5)}",
        fontsize=12,
        fontweight="bold",
    )
    ax.grid(axis="y", linestyle=":", alpha=0.45)
    ax.spines[["top", "right"]].set_visible(False)

    legend_handles = [
        mpatches.Patch(color=c_xst, label="Holding XST"),
        mpatches.Patch(color=c_xqq, label="Holding XQQ"),
    ]
    ax.legend(handles=legend_handles + [
        plt.Line2D([0], [0], color="crimson", linestyle="--", label=f"Overall avg {avg_days:.0f}d"),
    ], fontsize=9, loc="upper left")

    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}")


def main() -> None:
    merged = load_merged()
    df5 = windowed(merged, 5)
    df2 = windowed(merged, 2)

    plot_switch_signals(df5, 5, "switch_signals_last5y_3pct_5pct.png")
    plot_switch_signals(df2, 2, "switch_signals_last2y_3pct_5pct.png")
    plot_real_switches(5, "real_switches_last5y_3pct_5pct.png")
    plot_real_switches(2, "real_switches_last2y_3pct_5pct.png")
    plot_delta_last2y(df2, "delta_last2y_graph.png")
    plot_switch_duration()


if __name__ == "__main__":
    main()