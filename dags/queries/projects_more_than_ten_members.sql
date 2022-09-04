SELECT repo_id, COUNT(DISTINCT actor_id) AS count_distinct_actors FROM github_data.archive_events
WHERE type = 'PushEvent'
GROUP BY repo_id
HAVING count_distinct_actors > 10;