-- Case Team report, slide 5 (Submissions received), for one month.
-- Parameter: the month as a date on its first day, e.g. '2026-09-01'.
-- Month boundaries are midnight in Melbourne.
WITH bounds AS (
    SELECT
        (CAST(:month AS date)::timestamp AT TIME ZONE 'Australia/Melbourne') AS start_at,
        ((CAST(:month AS date) + interval '1 month')::timestamp AT TIME ZONE 'Australia/Melbourne') AS end_at,
        ((CAST(:month AS date) - interval '1 month')::timestamp AT TIME ZONE 'Australia/Melbourne') AS prev_start_at
),
received AS (
    SELECT i.id, i.topic
    FROM core_issue i, bounds b
    WHERE i.created_at >= b.start_at AND i.created_at < b.end_at
),
-- Eligible: the case's latest eligibility note at month end is a success.
-- Checks made after month end are left out, so a re-run gives the same answer.
eligible AS (
    SELECT r.id
    FROM received r, bounds b
    JOIN LATERAL (
        SELECT n.note_type
        FROM core_issuenote n
        WHERE n.issue_id = r.id
          AND n.note_type IN ('ELIGIBILITY_CHECK_SUCCESS', 'ELIGIBILITY_CHECK_FAILURE')
          AND n.created_at < b.end_at
        ORDER BY n.created_at DESC
        LIMIT 1
    ) latest ON latest.note_type = 'ELIGIBILITY_CHECK_SUCCESS'
),
-- Each case's open state and paralegal at month end, replayed from events:
-- the last change before month end, else the value before the first change
-- after it, else the current value.
at_month_end AS (
    SELECT
        i.id,
        i.topic,
        COALESCE(
            (SELECT e.next_is_open FROM core_issueevent e
             WHERE e.issue_id = i.id AND e.next_is_open IS NOT NULL AND e.created_at < b.end_at
             ORDER BY e.created_at DESC LIMIT 1),
            (SELECT e.prev_is_open FROM core_issueevent e
             WHERE e.issue_id = i.id AND e.prev_is_open IS NOT NULL AND e.created_at >= b.end_at
             ORDER BY e.created_at ASC LIMIT 1),
            i.is_open
        ) AS is_open,
        CASE
            WHEN EXISTS (SELECT 1 FROM core_issueevent e
                         WHERE e.issue_id = i.id AND e.event_type LIKE '%PARALEGAL%' AND e.created_at < b.end_at)
            THEN (SELECT e.next_user_id FROM core_issueevent e
                  WHERE e.issue_id = i.id AND e.event_type LIKE '%PARALEGAL%' AND e.created_at < b.end_at
                  ORDER BY e.created_at DESC LIMIT 1)
            WHEN EXISTS (SELECT 1 FROM core_issueevent e
                         WHERE e.issue_id = i.id AND e.event_type LIKE '%PARALEGAL%' AND e.created_at >= b.end_at)
            THEN (SELECT e.prev_user_id FROM core_issueevent e
                  WHERE e.issue_id = i.id AND e.event_type LIKE '%PARALEGAL%' AND e.created_at >= b.end_at
                  ORDER BY e.created_at ASC LIMIT 1)
            ELSE i.paralegal_id
        END AS paralegal_id
    FROM core_issue i, bounds b
    WHERE i.created_at < b.end_at
),
awaiting AS (
    SELECT id, topic FROM at_month_end WHERE is_open AND paralegal_id IS NULL
),
received_last_month AS (
    SELECT i.topic
    FROM core_issue i, bounds b
    WHERE i.created_at >= b.prev_start_at AND i.created_at < b.start_at
),
topics AS (
    SELECT topic FROM received
    UNION SELECT topic FROM awaiting
    UNION SELECT topic FROM received_last_month
)
SELECT
    t.topic,
    (SELECT count(*) FROM received r WHERE r.topic = t.topic) AS received,
    (SELECT count(*) FROM received r JOIN eligible e USING (id) WHERE r.topic = t.topic) AS eligible,
    (SELECT count(*) FROM awaiting a WHERE a.topic = t.topic) AS awaiting_assignment,
    (SELECT count(*) FROM received_last_month l WHERE l.topic = t.topic) AS received_last_month
FROM topics t
ORDER BY t.topic;
