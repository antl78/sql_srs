SELECT department,
    SUM(wage) AS payroll
FROM wages
GROUP BY department
HAVING SUM(wage) > 300000
