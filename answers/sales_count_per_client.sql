SELECT client_name,
    COUNT(*) AS nb_sales
FROM sales
GROUP BY client_name
