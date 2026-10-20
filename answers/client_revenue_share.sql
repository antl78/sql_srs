WITH client_revenue AS (
    SELECT client_name,
        SUM(amount) AS total_revenue
    FROM sales
    GROUP BY client_name
),
overall_revenue AS (
    SELECT SUM(total_revenue) AS grand_total
    FROM client_revenue
)
SELECT client_revenue.client_name,
    client_revenue.total_revenue,
    ROUND(100.0 * client_revenue.total_revenue / overall_revenue.grand_total, 2) AS revenue_share_pct
FROM client_revenue
CROSS JOIN overall_revenue
