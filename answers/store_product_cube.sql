SELECT store_id,
    product_name,
    SUM(amount) AS total_amount
FROM store_sales
GROUP BY CUBE (store_id, product_name)
