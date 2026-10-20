SELECT department,
    COUNT(*) AS headcount,
    AVG(wage) AS avg_wage
FROM wages
WHERE wage >= 65000
GROUP BY department
HAVING COUNT(*) >= 4
