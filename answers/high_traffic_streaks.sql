-- Gaps and islands : sur des jours consécutifs, visit_date et ROW_NUMBER
-- avancent ensemble, donc leur différence est constante sur une série.
WITH high_traffic_days AS (
    SELECT visit_date
    FROM sensor_visits
    WHERE visitor_count >= 5000
),
streaks AS (
    SELECT visit_date,
        visit_date - ROW_NUMBER() OVER (ORDER BY visit_date) * INTERVAL '1 day' AS streak_key
    FROM high_traffic_days
)
SELECT MIN(visit_date) AS streak_start,
    MAX(visit_date) AS streak_end,
    COUNT(*) AS nb_days
FROM streaks
GROUP BY streak_key
HAVING COUNT(*) >= 2
