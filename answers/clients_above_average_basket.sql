WITH client_avg AS (
    SELECT client_name,
        AVG(amount) AS avg_basket
    FROM sales
    GROUP BY client_name
),
overall_avg AS (
    SELECT AVG(avg_basket) AS overall_avg_basket
    FROM client_avg
)
SELECT client_avg.client_name,
    client_avg.avg_basket
FROM client_avg, overall_avg
WHERE client_avg.avg_basket > overall_avg.overall_avg_basket
