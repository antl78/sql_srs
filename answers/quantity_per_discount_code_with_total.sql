SELECT
    CASE
        WHEN GROUPING(discount_code) = 1 THEN 'TOTAL'
        WHEN discount_code IS NULL THEN 'NO_CODE'
        ELSE discount_code
    END AS discount_code_label,
    SUM(quantity) AS total_quantity
FROM orders_discounts
GROUP BY ROLLUP (discount_code)
