SELECT
    o.order_id,
    o.customer_id,
    od.product_id,
    od.quantity
FROM orders o
INNER JOIN order_details od
    ON o.order_id = od.order_id
