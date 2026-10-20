SELECT e.employee_name,
    mm.employee_name AS manager_n2
FROM employees e
INNER JOIN employees m ON e.manager_id = m.employee_id
INNER JOIN employees mm ON m.manager_id = mm.employee_id
