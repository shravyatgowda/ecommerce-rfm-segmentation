-- Build one row per customer with Recency, Frequency and Monetary values.
-- SQLite-compatible. :snapshot is the analysis date.
WITH order_stats AS (
    SELECT
        o.customer_id,
        MAX(o.order_date)           AS last_order_date,
        COUNT(o.order_id)           AS frequency,
        ROUND(SUM(o.order_value),2) AS monetary
    FROM orders o
    GROUP BY o.customer_id
)
SELECT
    c.customer_id,
    c.country,
    c.email_opt_in,
    s.last_order_date,
    CAST(julianday(:snapshot) - julianday(s.last_order_date) AS INTEGER) AS recency_days,
    s.frequency,
    s.monetary
FROM customers c
JOIN order_stats s ON s.customer_id = c.customer_id;
