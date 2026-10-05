"""Create a static summary dashboard image from rfm.py outputs.

This is a Python (matplotlib) visual, NOT a Power BI report. Run rfm.py first.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("output/rfm_customers_for_powerbi.csv")
Path("images").mkdir(exist_ok=True)
risk = df[df.at_risk_high_value == 1]

fig = plt.figure(figsize=(13, 8))
fig.suptitle("E-Commerce Customer Segmentation: Summary Dashboard (synthetic data, Python-generated)",
             fontsize=14, fontweight="bold")
gs = fig.add_gridspec(3, 3, height_ratios=[0.6, 1.5, 1.5], hspace=0.7, wspace=0.35)

kpis = [("Customers", f"{len(df):,}"),
        ("At-risk high-value", f"{len(risk):,}"),
        ("At-risk lifetime spend", f"{risk.monetary.sum():,.0f}")]
for i, (label, val) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i]); ax.axis("off")
    ax.text(.5, .62, val, ha="center", fontsize=24, fontweight="bold", color="#1f4e79")
    ax.text(.5, .12, label, ha="center", fontsize=11, color="#555")

ax = fig.add_subplot(gs[1, 0])
df.groupby("cluster").size().plot(kind="bar", ax=ax, rot=0, color="#4f81bd")
ax.set_title("Customers per segment"); ax.set_xlabel("cluster")

ax = fig.add_subplot(gs[1, 1])
df.groupby("cluster").monetary.mean().plot(kind="bar", ax=ax, rot=0, color="#9bbb59")
ax.set_title("Average spend per segment"); ax.set_xlabel("cluster")

ax = fig.add_subplot(gs[1, 2])
df.groupby("cluster").recency_days.mean().plot(kind="bar", ax=ax, rot=0, color="#c0504d")
ax.set_title("Average recency (days)"); ax.set_xlabel("cluster")

ax = fig.add_subplot(gs[2, :2])
s = df.sample(4000, random_state=1)
ax.scatter(s.recency_days, s.monetary, s=6, alpha=.35, c="#7f7f7f", label="Other customers")
r = s[s.at_risk_high_value == 1]
ax.scatter(r.recency_days, r.monetary, s=10, c="#c0504d", label="At-risk high-value")
ax.set_yscale("log"); ax.set_xlabel("Recency (days since last order)"); ax.set_ylabel("Spend (log)")
ax.set_title("Recency vs spend"); ax.legend()

ax = fig.add_subplot(gs[2, 2])
risk.groupby("country").size().sort_values().plot(kind="barh", ax=ax, color="#c0504d")
ax.set_title("At-risk customers by country")

plt.savefig("images/dashboard_summary.png", dpi=130, bbox_inches="tight")
print("Saved images/dashboard_summary.png")
