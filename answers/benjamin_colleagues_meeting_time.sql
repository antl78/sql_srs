WITH benjamin_meetings AS (
    SELECT meeting_id
    FROM merged_df
    WHERE person_name = 'Benjamin'
)
SELECT merged_df.person_name,
    COUNT(*) AS meetings_with_benjamin,
    SUM(merged_df.duration_minutes) AS total_minutes
FROM merged_df
INNER JOIN benjamin_meetings ON merged_df.meeting_id = benjamin_meetings.meeting_id
WHERE merged_df.person_name <> 'Benjamin'
GROUP BY merged_df.person_name
