SELECT store_id,
    COUNT(*) AS nb_lines,
    COUNT(DISTINCT product_name) AS nb_distinct_products
FROM store_sales
GROUP BY store_id
