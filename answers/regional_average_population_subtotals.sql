SELECT region,
    year,
    AVG(population) AS avg_population
FROM regional_population
GROUP BY GROUPING SETS ((region, year), (region))
