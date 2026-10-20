SELECT name,
    department,
    wage,
    ROUND(AVG(wage) OVER (PARTITION BY department), 2) AS department_average,
    ROUND(wage - AVG(wage) OVER (PARTITION BY department), 2) AS gap_to_average
FROM wages
