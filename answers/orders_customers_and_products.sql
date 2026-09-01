SELECT * FROM order_client
INNER JOIN df_products
USING (product_id)
