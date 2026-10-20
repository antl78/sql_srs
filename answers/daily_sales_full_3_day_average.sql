SELECT sale_date,
    daily_sales,
    CASE
        WHEN COUNT(*) OVER (ORDER BY sale_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) = 3
        THEN ROUND(AVG(daily_sales) OVER (ORDER BY sale_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2)
    END AS moving_average_3_days
FROM daily_sales
