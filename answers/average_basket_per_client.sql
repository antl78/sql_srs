SELECT client_name,
    AVG(amount) AS avg_basket
FROM sales
GROUP BY client_name
