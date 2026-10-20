-- ORDER BY seul = RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW :
-- les ventes d'une même date sont cumulées ensemble.
SELECT sale_date,
    client_name,
    amount,
    SUM(amount) OVER (ORDER BY sale_date) AS cumulative_revenue
FROM sales
