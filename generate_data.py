"""Generate a synthetic e-commerce database (SYNTHETIC data, ~100k+ records)."""
import sqlite3
import numpy as np
import pandas as pd

rng = np.random.default_rng(11)
N_CUST, N_ORD = 15_000, 90_000

customers = pd.DataFrame({
    "customer_id": np.arange(1, N_CUST + 1),
    "signup_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 600, N_CUST), unit="D"),
    "country": rng.choice(["India", "UK", "USA", "Germany", "UAE"], N_CUST),
    "email_opt_in": rng.choice([0, 1], N_CUST, p=[.25, .75]),
})
# Heavy-tailed activity so some customers are clearly high value
weights = rng.pareto(2.0, N_CUST) + 0.2
cust_for_order = rng.choice(customers.customer_id, N_ORD, p=weights / weights.sum())
orders = pd.DataFrame({
    "order_id": np.arange(1, N_ORD + 1),
    "customer_id": cust_for_order,
    "order_date": pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0, 640, N_ORD), unit="D"),
    "order_value": np.round(rng.lognormal(3.6, 0.7, N_ORD), 2),
})
marketing = pd.DataFrame({
    "campaign_id": np.arange(1, 9),
    "channel": ["Email", "Email", "Social", "Social", "Search", "Search", "Display", "Referral"],
})

con = sqlite3.connect("data/ecommerce.db")
customers.to_sql("customers", con, if_exists="replace", index=False)
orders.to_sql("orders", con, if_exists="replace", index=False)
marketing.to_sql("marketing", con, if_exists="replace", index=False)
print(f"customers={len(customers):,} orders={len(orders):,} total records={len(customers)+len(orders)+len(marketing):,}")
