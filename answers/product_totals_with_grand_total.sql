SELECT product_name,
    SUM(amount) AS total_amount
FROM store_sales
GROUP BY GROUPING SETS ((product_name), ())
