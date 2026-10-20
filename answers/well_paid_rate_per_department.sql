SELECT department,
    COUNT(*) AS headcount,
    ROUND(100.0 * AVG(CASE WHEN wage >= 70000 THEN 1 ELSE 0 END), 2) AS well_paid_pct
FROM wages
GROUP BY department
