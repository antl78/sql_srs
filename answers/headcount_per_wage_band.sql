WITH banded_wages AS (
    SELECT wage,
        CASE
            WHEN wage < 70000 THEN 'Junior'
            WHEN wage < 90000 THEN 'Confirmed'
            ELSE 'Senior'
        END AS wage_band
    FROM wages
)
SELECT wage_band,
    COUNT(*) AS headcount,
    SUM(wage) AS payroll
FROM banded_wages
GROUP BY wage_band
