SELECT client_name,
    SUM(amount) AS total_sales
FROM sales
GROUP BY client_name
