WITH customers_without_orders AS (
    SELECT customers.customer_id
    FROM customers
    LEFT JOIN orders ON customers.customer_id = orders.customer_id
    WHERE orders.order_id IS NULL
)
DELETE FROM customers
WHERE customer_id IN (SELECT customer_id FROM customers_without_orders)
