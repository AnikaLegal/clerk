-- Case Team report, slide 8 (Case Progress), for one month.
-- Parameter: the month as a date on its first day, e.g. '2026-09-01'.
-- For this month ("this") and last month ("last"), by topic, of the cases
-- open at some point in the month:
--   open_cases: all of them;
--   progressed: those closed or moved to another stage during the month;
--   helped: those with legal services provided, and helped_clients their
--   renters.
-- A row with no topic is the total, so a renter with cases of two topics
-- counts once in it. Open means not yet closed for the last time: a case
-- reopened later counts as open in between. Month boundaries are midnight
-- in Melbourne.
WITH bounds AS (
    SELECT
        ((CAST(:month AS date) - interval '1 month')::timestamp AT TIME ZONE 'Australia/Melbourne') AS prev_start_at,
        (CAST(:month AS date)::timestamp AT TIME ZONE 'Australia/Melbourne') AS start_at,
        ((CAST(:month AS date) + interval '1 month')::timestamp AT TIME ZONE 'Australia/Melbourne') AS end_at
),
periods AS (
    SELECT 'this' AS which, start_at AS from_at, end_at AS to_at FROM bounds
    UNION ALL
    SELECT 'last', prev_start_at, start_at FROM bounds
),
cases AS (
    SELECT
        i.id,
        i.client_id,
        i.topic,
        i.provided_legal_services,
        i.created_at,
        CASE WHEN i.is_open THEN NULL ELSE COALESCE(
            (SELECT max(e.created_at) FROM core_issueevent e
             WHERE e.issue_id = i.id AND e.next_is_open = false),
            '-infinity'
        ) END AS closed_at
    FROM core_issue i
),
open_in_period AS (
    SELECT
        p.which,
        c.*,
        EXISTS (
            SELECT 1 FROM core_issueevent e
            WHERE e.issue_id = c.id
              AND (e.next_is_open = false OR e.event_type = 'STAGE')
              AND e.created_at >= p.from_at AND e.created_at < p.to_at
        ) AS progressed
    FROM cases c
    JOIN periods p ON c.created_at < p.to_at AND (c.closed_at IS NULL OR c.closed_at >= p.from_at)
)
SELECT
    which,
    topic,
    count(*) AS open_cases,
    count(*) FILTER (WHERE progressed) AS progressed,
    count(*) FILTER (WHERE provided_legal_services) AS helped,
    count(DISTINCT client_id) FILTER (WHERE provided_legal_services) AS helped_clients
FROM open_in_period
GROUP BY GROUPING SETS ((which, topic), (which))
ORDER BY which, topic NULLS LAST;
