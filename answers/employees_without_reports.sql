SELECT e.employee_name
FROM employees e
LEFT JOIN employees r ON r.manager_id = e.employee_id
WHERE r.employee_id IS NULL
