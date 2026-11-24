-- Case Team report, slide 7 (Cases Closed), for one month.
-- Parameter: the month as a date on its first day, e.g. '2026-09-01'.
-- Counts cases closed during this month ("this") and last month ("last"),
-- by topic, and how many of them had legal services provided. A case closed
-- more than once in a month counts once. Month boundaries are midnight in
-- Melbourne.
WITH bounds AS (
    SELECT
        ((CAST(:month AS date) - interval '1 month')::timestamp AT TIME ZONE 'Australia/Melbourne') AS prev_start_at,
        (CAST(:month AS date)::timestamp AT TIME ZONE 'Australia/Melbourne') AS start_at,
        ((CAST(:month AS date) + interval '1 month')::timestamp AT TIME ZONE 'Australia/Melbourne') AS end_at
),
closed AS (
    SELECT DISTINCT
        CASE WHEN e.created_at >= b.start_at THEN 'this' ELSE 'last' END AS which,
        i.id,
        i.topic,
        i.provided_legal_services
    FROM core_issueevent e
    JOIN core_issue i ON i.id = e.issue_id
    CROSS JOIN bounds b
    WHERE e.next_is_open = false
      AND e.created_at >= b.prev_start_at
      AND e.created_at < b.end_at
)
SELECT
    which,
    topic,
    count(*) AS closed,
    count(*) FILTER (WHERE provided_legal_services) AS closed_with_legal_advice
FROM closed
GROUP BY which, topic
ORDER BY which, topic;
