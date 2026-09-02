SELECT * FROM df_customers
LEFT JOIN df_orders
USING (customer_id)
LEFT JOIN df_order_details
USING (order_id)