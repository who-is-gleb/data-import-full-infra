SELECT toDate(created_at) AS events_date, actor_id, sum(commit_amount) AS daily_commits FROM github_data.archive_events
WHERE type = 'PushEvent'
GROUP BY toDate(created_at), actor_id
HAVING daily_commits > 1
ORDER BY actor_id, daily_commits;