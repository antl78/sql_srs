WITH ranked_wages AS (
    SELECT department,
        name,
        wage,
        DENSE_RANK() OVER (PARTITION BY department ORDER BY wage DESC) AS wage_rank
    FROM wages
)
SELECT department,
    name,
    wage
FROM ranked_wages
WHERE wage_rank = 2
