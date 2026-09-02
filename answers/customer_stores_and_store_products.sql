SELECT * FROM customer_stores
LEFT JOIN store_products
USING (store_id)