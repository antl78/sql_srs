SELECT * FROM orders
INNER JOIN order_details
USING (order_id)
