SELECT client_name,
    MIN(amount) AS min_sale,
    MAX(amount) AS max_sale,
    STDDEV(amount) AS stddev_sale
FROM sales
GROUP BY client_name
