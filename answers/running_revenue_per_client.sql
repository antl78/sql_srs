SELECT client_name,
    sale_date,
    amount,
    SUM(amount) OVER (PARTITION BY client_name ORDER BY sale_date) AS running_revenue
FROM sales
