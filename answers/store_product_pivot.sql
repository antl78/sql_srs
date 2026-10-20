SELECT store_id,
    SUM(CASE WHEN product_name = 'redbull' THEN amount ELSE 0 END) AS redbull,
    SUM(CASE WHEN product_name = 'chips' THEN amount ELSE 0 END) AS chips,
    SUM(CASE WHEN product_name = 'wine' THEN amount ELSE 0 END) AS wine,
    SUM(CASE WHEN product_name = 'icecream' THEN amount ELSE 0 END) AS icecream
FROM store_sales
GROUP BY store_id
