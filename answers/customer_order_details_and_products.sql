SELECT * FROM customer_order_details
LEFT JOIN df_products
USING (product_id)