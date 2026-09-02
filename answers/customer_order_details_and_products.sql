SELECT * FROM customer_order_details
LEFT JOIN products
USING (product_id)