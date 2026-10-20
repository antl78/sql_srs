WITH sales_with_previous AS (
    SELECT sale_date,
        daily_sales,
        LAG(daily_sales) OVER (ORDER BY sale_date) AS previous_day_sales
    FROM daily_sales
)
SELECT sale_date,
    daily_sales,
    previous_day_sales,
    daily_sales - previous_day_sales AS change,
    ROUND((daily_sales - previous_day_sales) * 100.0 / previous_day_sales, 2) AS change_pct
FROM sales_with_previous
