SELECT customers.customer_id,
customer_name,
order_id,
product_id,
quantity
FROM customers
INNER JOIN detailed_order
on customers.customer_id = detailed_order.customer_id
