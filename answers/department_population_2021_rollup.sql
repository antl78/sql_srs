SELECT region,
    department,
    SUM(population) AS population
FROM department_population
WHERE year = 2021
GROUP BY ROLLUP (region, department)
