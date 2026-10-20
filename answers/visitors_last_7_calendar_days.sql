-- RANGE travaille sur les valeurs de visit_date (7 jours calendaires),
-- ROWS sur le nombre de lignes : avec les dimanches manquants,
-- ROWS BETWEEN 6 PRECEDING couvrirait 8 jours.
SELECT visit_date,
    visitor_count,
    SUM(visitor_count) OVER (
        ORDER BY visit_date
        RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW
    ) AS visitors_last_7_days
FROM sensor_visits
