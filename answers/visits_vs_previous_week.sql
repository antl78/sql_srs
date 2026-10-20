SELECT cur.visit_date,
    cur.visitor_count,
    prev.visitor_count AS previous_week_count,
    cur.visitor_count - prev.visitor_count AS difference
FROM sensor_visits cur
LEFT JOIN sensor_visits prev
    ON prev.sensor_id = cur.sensor_id
    AND prev.visit_date = cur.visit_date - INTERVAL '7 days'
