SELECT SUM(CASE WHEN department = 'IT' THEN wage ELSE 0 END) AS it_payroll,
    SUM(CASE WHEN department <> 'IT' THEN wage ELSE 0 END) AS other_payroll,
    ROUND(100.0 * SUM(CASE WHEN department = 'IT' THEN wage ELSE 0 END) / SUM(wage), 2) AS it_share_pct
FROM wages
