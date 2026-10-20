WITH order_revenue AS (
    SELECT product_id,
        CASE
            WHEN discount_code = 'DISCOUNT10' THEN quantity * price_per_unit * 0.9
            WHEN discount_code = 'DISCOUNT20' THEN quantity * price_per_unit * 0.8
            ELSE quantity * price_per_unit
        END AS net_revenue
    FROM orders_discounts
)
SELECT product_id,
    SUM(net_revenue) AS net_revenue
FROM order_revenue
GROUP BY product_id
