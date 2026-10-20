WITH ranked_sales AS (
    SELECT client_name,
        sale_date,
        amount,
        ROW_NUMBER() OVER (
            PARTITION BY client_name
            ORDER BY amount DESC, sale_date
        ) AS sale_rank
    FROM sales
)
SELECT client_name,
    sale_date,
    amount
FROM ranked_sales
WHERE sale_rank <= 2
