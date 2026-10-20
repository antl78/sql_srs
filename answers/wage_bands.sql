SELECT name,
    wage,
    CASE
        WHEN wage < 70000 THEN 'Junior'
        WHEN wage < 90000 THEN 'Confirmed'
        ELSE 'Senior'
    END AS wage_band
FROM wages
