SELECT client_name,
    MIN(sale_date) AS first_sale,
    MAX(sale_date) AS last_sale,
    MAX(sale_date) - MIN(sale_date) AS days_between
FROM sales
GROUP BY client_name
HAVING MAX(sale_date) - MIN(sale_date) >= 60
