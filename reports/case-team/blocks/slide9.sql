-- Case Team report, slide 9 (CLCA Legal Services Provided), for one month.
-- Parameter: the month as a date on its first day, e.g. '2026-09-01'.
-- Legal services counted in the financial year up to this month's end, by
-- quarter and category, following the CLCA counting rules: a discrete
-- service counts on the day it was given, an ongoing one on the day it
-- finished. A service's count is how many it stands for. Referrals are
-- simple and facilitated referrals. A row with category STILL_OPEN is the
-- ongoing services started but not finished by the month's end.
WITH bounds AS (
    SELECT
        (CAST(:month AS date) + interval '1 month')::date AS end_on,
        make_date(extract(year FROM CAST(:month AS date) - interval '6 months')::int, 7, 1) AS fy_start_on
),
services AS (
    SELECT
        s.category,
        s.type,
        s.count,
        s.started_at,
        s.finished_at,
        CASE WHEN s.category = 'DISCRETE' THEN s.started_at ELSE s.finished_at END AS counted_on
    FROM core_service s
    WHERE NOT s.is_deleted
)
SELECT
    s.category,
    -- July to September is quarter 1.
    (extract(month FROM s.counted_on)::int + 5) % 12 / 3 + 1 AS quarter,
    sum(s.count) AS services,
    coalesce(sum(s.count) FILTER (
        WHERE s.type NOT IN ('GENERAL_REFERRAL_SIMPLE', 'GENERAL_REFERRAL_FACILITATED')
    ), 0) AS services_excluding_referrals
FROM services s
CROSS JOIN bounds b
WHERE s.counted_on >= b.fy_start_on AND s.counted_on < b.end_on
GROUP BY 1, 2
UNION ALL
SELECT 'STILL_OPEN', NULL, coalesce(sum(s.count), 0), NULL
FROM services s
CROSS JOIN bounds b
WHERE s.category = 'ONGOING'
  AND s.started_at < b.end_on
  AND (s.finished_at IS NULL OR s.finished_at >= b.end_on)
ORDER BY 1, 2;
