SELECT * FROM store_customers
LEFT JOIN stores
USING (customer_id)