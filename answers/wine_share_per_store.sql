SELECT store_id,
    SUM(CASE WHEN product_name = 'wine' THEN amount ELSE 0 END) AS wine_amount,
    SUM(amount) AS total_amount,
    ROUND(100.0 * SUM(CASE WHEN product_name = 'wine' THEN amount ELSE 0 END) / SUM(amount), 2) AS wine_share_pct
FROM store_sales
GROUP BY store_id
