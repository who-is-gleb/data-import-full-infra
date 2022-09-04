SELECT actor_id, count() AS repo_created_count
FROM (
         SELECT *
         FROM github_data.archive_events
         WHERE type = 'CreateEvent'
           AND ref_type = 'repository'
         )
GROUP BY actor_id
HAVING repo_created_count > 1;