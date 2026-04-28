"""
switch_duration_graph.py — Bar chart of calendar days between each switch,
with a dashed overall average and per-direction (XST/XQQ) average lines.

Data source: real_switches_last2y_3pct.csv  (10 switches, 9 durations)
Output    : switch_duration_graph.png
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

SRC = Path(__file__).parent
CSV = SRC / "real_switches_last5y_3pct.csv"
OUT = SRC / "switch_duration_graph.png"

# ── Load & compute durations ──────────────────────────────────────────────────
df = pd.read_csv(CSV, parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)

# Duration of "holding period N" = days from switch N to switch N+1
n = len(df)
durations = []
for i in range(n - 1):
    days = (df.loc[i + 1, "Date"] - df.loc[i, "Date"]).days
    label = (
        f"#{df.loc[i,'Switch #']}→#{df.loc[i+1,'Switch #']}\n"
        f"{df.loc[i,'Date'].strftime('%Y-%m-%d')}"
    )
    direction = f"{df.loc[i,'From']}→{df.loc[i+1,'From']}"
    durations.append({
        "label": label,
        "days": days,
        "from": df.loc[i, "From"],
    })

dur_df = pd.DataFrame(durations)
avg_days     = dur_df["days"].mean()
avg_xst_days = dur_df.loc[dur_df["from"] == "XST", "days"].mean()
avg_xqq_days = dur_df.loc[dur_df["from"] == "XQQ", "days"].mean()

# ── Colours: XST holding period = blue, XQQ holding = orange ─────────────────
COLOUR_XST = "#1f77b4"   # holding XST, waiting for sell-XST signal
COLOUR_XQQ = "#ff7f0e"   # holding XQQ, waiting for sell-XQQ signal
colours = [COLOUR_XST if row["from"] == "XST" else COLOUR_XQQ
           for _, row in dur_df.iterrows()]

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))

bars = ax.bar(range(len(dur_df)), dur_df["days"], color=colours, edgecolor="white",
              linewidth=0.8, zorder=3)

# Value labels: inside bar if tall enough, above bar otherwise
MIN_INSIDE = 40  # px threshold in data units
for bar, days in zip(bars, dur_df["days"]):
    x = bar.get_x() + bar.get_width() / 2
    if days >= MIN_INSIDE:
        ax.text(x, days / 2, f"{days}d",
                ha="center", va="center",
                fontsize=9, fontweight="bold", color="white", zorder=5)
    else:
        ax.text(x, days + 4, f"{days}d",
                ha="center", va="bottom",
                fontsize=9, fontweight="bold", color="#333333", zorder=5)

y_max = dur_df["days"].max() * 1.25

# Stagger the three average-line labels on the right so they never overlap.
# Sort by value and assign vertical offsets to keep them apart.
avg_lines = [
    (avg_xqq_days, COLOUR_XQQ, ":",  f"XQQ avg {avg_xqq_days:.0f}d"),
    (avg_days,     "crimson",  "--", f"Overall avg {avg_days:.0f}d"),
    (avg_xst_days, COLOUR_XST, ":",  f"XST avg {avg_xst_days:.0f}d"),
]
MIN_GAP = y_max * 0.05   # minimum vertical gap between labels
sorted_lines = sorted(avg_lines, key=lambda t: t[0])
adjusted = []
for i, (val, col, ls, lbl) in enumerate(sorted_lines):
    y = val
    if i > 0 and (y - adjusted[-1]) < MIN_GAP:
        y = adjusted[-1] + MIN_GAP
    adjusted.append(y)

for (val, col, ls, lbl), y_label in zip(sorted_lines, adjusted):
    ax.axhline(val, color=col, linestyle=ls, linewidth=1.6, zorder=4)
    ax.text(len(dur_df) - 0.1, y_label + 3, lbl,
            color=col, fontsize=8.5, va="bottom", ha="right",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.7),
            zorder=5)

# Axes formatting
ax.set_xticks(range(len(dur_df)))
ax.set_xticklabels(dur_df["label"], fontsize=8.5)
ax.set_ylabel("Holding duration (calendar days)", fontsize=10)
ax.set_title("XST vs XQQ — Duration of each holding period between switches\n"
             "(3 % threshold, last 5 years)", fontsize=12, fontweight="bold")
ax.set_ylim(0, y_max)
ax.grid(axis="y", linestyle=":", alpha=0.5, zorder=0)
ax.spines[["top", "right"]].set_visible(False)

avg_xst_label = f"{avg_xst_days:.0f}d avg" if not pd.isna(avg_xst_days) else ""
avg_xqq_label = f"{avg_xqq_days:.0f}d avg" if not pd.isna(avg_xqq_days) else ""
legend_handles = [
    mpatches.Patch(color=COLOUR_XST, label=f"Holding XST — waiting for sell-XST signal ({avg_xst_label})"),
    mpatches.Patch(color=COLOUR_XQQ, label=f"Holding XQQ — waiting for sell-XQQ signal ({avg_xqq_label})"),
    plt.Line2D([0], [0], color="crimson", linestyle="--", linewidth=1.4,
               label=f"Overall avg {avg_days:.0f}d"),
]
ax.legend(handles=legend_handles, fontsize=9, loc="upper left")

plt.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved {OUT}")
