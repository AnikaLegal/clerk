-- Case Team report, slide 6 (Cases Open), for one month.
-- Parameter: the month as a date on its first day, e.g. '2026-09-01'.
-- Counts open cases by stage and topic at this month's end ("this") and at
-- last month's end ("last"). Month boundaries are midnight in Melbourne.
WITH bounds AS (
    SELECT
        (CAST(:month AS date)::timestamp AT TIME ZONE 'Australia/Melbourne') AS start_at,
        ((CAST(:month AS date) + interval '1 month')::timestamp AT TIME ZONE 'Australia/Melbourne') AS end_at
),
moments AS (
    SELECT 'this' AS which, end_at AS at FROM bounds
    UNION ALL
    SELECT 'last', start_at FROM bounds
),
-- Each case's open state and stage at each moment, replayed from events:
-- the last change before it, else the value before the first change after
-- it, else the current value.
state AS (
    SELECT
        m.which,
        i.topic,
        COALESCE(
            (SELECT e.next_is_open FROM core_issueevent e
             WHERE e.issue_id = i.id AND e.next_is_open IS NOT NULL AND e.created_at < m.at
             ORDER BY e.created_at DESC LIMIT 1),
            (SELECT e.prev_is_open FROM core_issueevent e
             WHERE e.issue_id = i.id AND e.prev_is_open IS NOT NULL AND e.created_at >= m.at
             ORDER BY e.created_at ASC LIMIT 1),
            i.is_open
        ) AS is_open,
        COALESCE(
            (SELECT e.next_stage FROM core_issueevent e
             WHERE e.issue_id = i.id AND e.next_stage IS NOT NULL AND e.created_at < m.at
             ORDER BY e.created_at DESC LIMIT 1),
            (SELECT e.prev_stage FROM core_issueevent e
             WHERE e.issue_id = i.id AND e.prev_stage IS NOT NULL AND e.created_at >= m.at
             ORDER BY e.created_at ASC LIMIT 1),
            i.stage
        ) AS stage
    FROM core_issue i
    CROSS JOIN moments m
    WHERE i.created_at < m.at
)
SELECT which, stage, topic, count(*) AS open_cases
FROM state
WHERE is_open
GROUP BY which, stage, topic
ORDER BY which, stage, topic;
