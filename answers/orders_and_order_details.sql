SELECT * FROM df_orders
INNER JOIN df_order_details
USING (order_id)
