SELECT client_name,
    sale_date,
    amount,
    ROW_NUMBER() OVER (ORDER BY amount DESC, sale_date) AS row_number,
    RANK() OVER (ORDER BY amount DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY amount DESC) AS dense_rank
FROM sales
