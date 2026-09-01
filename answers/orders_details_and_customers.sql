WITH orders_with_details AS (
    SELECT
        o.order_id,
        o.customer_id,
        od.product_id,
        od.quantity
    FROM orders o
    INNER JOIN order_details od
        ON o.order_id = od.order_id
)
SELECT
    owd.order_id,
    c.customer_name,
    owd.product_id,
    owd.quantity
FROM orders_with_details owd
INNER JOIN customers c
    ON owd.customer_id = c.customer_id
