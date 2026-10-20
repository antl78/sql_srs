INSERT INTO sales_archive (client_name, amount)
SELECT client_name,
    amount
FROM sales
WHERE amount >= 60
