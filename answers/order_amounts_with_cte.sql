WITH priced_order_lines AS (
    SELECT order_details.order_id,
        order_details.quantity * products.product_price AS order_amount
    FROM order_details
    INNER JOIN products ON order_details.product_id = products.product_id
)
SELECT orders.order_id,
    customers.customer_name,
    priced_order_lines.order_amount
FROM priced_order_lines
INNER JOIN orders ON priced_order_lines.order_id = orders.order_id
INNER JOIN customers ON orders.customer_id = customers.customer_id
