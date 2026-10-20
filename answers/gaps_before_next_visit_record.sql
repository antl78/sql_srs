WITH visits_with_next AS (
    SELECT visit_date,
        LEAD(visit_date) OVER (ORDER BY visit_date) AS next_visit_date
    FROM sensor_visits
)
SELECT visit_date,
    next_visit_date,
    next_visit_date - visit_date AS days_until_next
FROM visits_with_next
WHERE next_visit_date - visit_date > 1
