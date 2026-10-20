WITH visits_with_average AS (
    SELECT visit_date,
        visitor_count,
        AVG(visitor_count) OVER () AS monthly_average
    FROM sensor_visits
)
SELECT visit_date,
    visitor_count,
    ROUND(monthly_average, 2) AS monthly_average
FROM visits_with_average
WHERE visitor_count < 0.9 * monthly_average
