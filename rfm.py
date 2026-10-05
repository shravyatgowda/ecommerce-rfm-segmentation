"""RFM analysis and customer segmentation, with an at-risk high-value list."""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

OUT = Path("output")
OUT.mkdir(exist_ok=True)
SNAPSHOT = "2025-10-15"

con = sqlite3.connect("data/ecommerce.db")
rfm = pd.read_sql(Path("sql/rfm_extract.sql").read_text(), con, params={"snapshot": SNAPSHOT})

# RFM scores 1-5 (5 = best)
rfm["R"] = pd.qcut(rfm.recency_days, 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["F"] = pd.qcut(rfm.frequency.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M"] = pd.qcut(rfm.monetary, 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["rfm_score"] = rfm.R + rfm.F + rfm.M

# K-Means on log-scaled features for behavioural segments
feat = StandardScaler().fit_transform(
    np.log1p(rfm[["recency_days", "frequency", "monetary"]].astype(float))
)
rfm["cluster"] = KMeans(n_clusters=4, n_init=10, random_state=3).fit_predict(feat)

# At-risk high value: top-quartile spenders with no purchase in 90+ days
top_spend = rfm.monetary >= rfm.monetary.quantile(0.75)
rfm["at_risk_high_value"] = (top_spend & (rfm.recency_days > 90)).astype(int)
at_risk = rfm[rfm.at_risk_high_value == 1].sort_values("monetary", ascending=False)

rfm.to_csv(OUT / "rfm_customers_for_powerbi.csv", index=False)
at_risk.to_csv(OUT / "at_risk_high_value_customers.csv", index=False)

print(rfm.groupby("cluster")[["recency_days", "frequency", "monetary"]].mean().round(1))
print(f"\nCustomers: {len(rfm):,} | at-risk high-value: {len(at_risk):,} "
      f"({len(at_risk)/len(rfm):.1%}) holding {at_risk.monetary.sum():,.0f} lifetime spend")

ax = rfm.groupby("cluster").size().plot(kind="bar", rot=0, figsize=(6, 4))
ax.set_title("Customers per segment (synthetic data)")
ax.set_ylabel("Customers")
plt.tight_layout()
plt.savefig(OUT / "segments.png", dpi=150)
