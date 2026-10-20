WITH labeled_orders AS (
    SELECT quantity * price_per_unit AS gross_revenue,
        CASE
            WHEN discount_code IS NULL THEN 'no_code'
            WHEN discount_code IN ('DISCOUNT10', 'DISCOUNT20') THEN 'valid_code'
            ELSE 'invalid_code'
        END AS discount_status
    FROM orders_discounts
)
SELECT discount_status,
    COUNT(*) AS nb_orders,
    SUM(gross_revenue) AS gross_revenue
FROM labeled_orders
GROUP BY discount_status
