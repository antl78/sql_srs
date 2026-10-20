SELECT EXTRACT(DOW FROM sale_date) AS weekday,
    COUNT(*) AS sales_count,
    SUM(amount) AS revenue
FROM sales
GROUP BY EXTRACT(DOW FROM sale_date)
