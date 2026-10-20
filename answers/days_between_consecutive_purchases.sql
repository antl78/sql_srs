SELECT client_name,
    sale_date,
    LAG(sale_date) OVER (PARTITION BY client_name ORDER BY sale_date) AS previous_sale_date,
    sale_date - LAG(sale_date) OVER (PARTITION BY client_name ORDER BY sale_date) AS days_since_previous
FROM sales
