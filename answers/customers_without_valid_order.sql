WITH valid_orders AS (
    SELECT orders.order_id,
        orders.customer_id
    FROM orders
    INNER JOIN order_details ON orders.order_id = order_details.order_id
    INNER JOIN products ON order_details.product_id = products.product_id
)
SELECT customers.customer_name
FROM customers
LEFT JOIN valid_orders ON customers.customer_id = valid_orders.customer_id
WHERE valid_orders.order_id IS NULL
