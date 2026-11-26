-- Case Team report: renters helped and legal problems, for slides 8 to 10.
-- Parameter: the month as a date on its first day, e.g. '2026-09-01'.
-- For each month end of this financial year up to the report month
-- ("this") and of the last financial year ("last"): renters (clients) and
-- legal problems (cases) with "provided legal services" ticked on a case
-- open at some point in the financial year so far. fy_month 1 is July;
-- fy_month 0 is the year's first day, counting cases carried over from the
-- year before. Rows have a topic per case type, and a row with no topic is
-- the total, in which a renter with cases of two types counts once. Open
-- means not yet closed for the last time: a case reopened later counts as
-- open in between. Month boundaries are midnight in Melbourne.
WITH bounds AS (
    SELECT
        (CAST(:month AS date) + interval '1 month')::date AS end_on,
        make_date(extract(year FROM CAST(:month AS date) - interval '6 months')::int, 7, 1) AS fy_start_on
),
points AS (
    SELECT 'this' AS fy, k AS fy_month, b.fy_start_on AS from_on,
        (b.fy_start_on + make_interval(months => k))::date AS to_on
    FROM bounds b, generate_series(0, 12) k
    WHERE b.fy_start_on + make_interval(months => k) <= b.end_on
    UNION ALL
    SELECT 'last', k, (b.fy_start_on - interval '1 year')::date,
        (b.fy_start_on - interval '1 year' + make_interval(months => k))::date
    FROM bounds b, generate_series(0, 12) k
),
cases AS (
    SELECT
        i.id,
        i.client_id,
        i.topic,
        i.created_at,
        CASE WHEN i.is_open THEN NULL ELSE COALESCE(
            (SELECT max(e.created_at) FROM core_issueevent e
             WHERE e.issue_id = i.id AND e.next_is_open = false),
            '-infinity'
        ) END AS closed_at
    FROM core_issue i
    WHERE i.provided_legal_services
)
SELECT
    p.fy,
    p.fy_month,
    c.topic,
    count(DISTINCT c.client_id) AS renters,
    count(DISTINCT c.id) AS legal_problems
FROM points p
JOIN cases c
  ON c.created_at < (p.to_on::timestamp AT TIME ZONE 'Australia/Melbourne')
 AND (c.closed_at IS NULL OR c.closed_at >= (p.from_on::timestamp AT TIME ZONE 'Australia/Melbourne'))
GROUP BY GROUPING SETS ((p.fy, p.fy_month, c.topic), (p.fy, p.fy_month))
ORDER BY p.fy, p.fy_month, c.topic NULLS LAST;
