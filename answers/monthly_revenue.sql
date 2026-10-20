SELECT DATE_TRUNC('month', sale_date) AS sale_month,
    COUNT(*) AS sales_count,
    SUM(amount) AS revenue
FROM sales
GROUP BY DATE_TRUNC('month', sale_date)
