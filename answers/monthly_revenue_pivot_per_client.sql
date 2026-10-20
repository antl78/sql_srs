SELECT client_name,
    SUM(CASE WHEN EXTRACT(MONTH FROM sale_date) = 1 THEN amount ELSE 0 END) AS january,
    SUM(CASE WHEN EXTRACT(MONTH FROM sale_date) = 2 THEN amount ELSE 0 END) AS february,
    SUM(CASE WHEN EXTRACT(MONTH FROM sale_date) = 3 THEN amount ELSE 0 END) AS march
FROM sales
GROUP BY client_name
