SELECT * 
FROM stores_and_products
FULL OUTER JOIN product_catalog
USING (product_id)