SELECT * FROM order_client
INNER JOIN products
USING (product_id)
