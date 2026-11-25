-- Case Team report, slide 4 (Current Case Team Capacity).
-- Capacity isn't recorded over time, so this is always the current figure;
-- the month-end snapshot is what keeps past months' capacity.
-- Users count when they're active and have a case capacity above zero.
SELECT
    g.name AS role,
    count(*) FILTER (WHERE u.case_capacity > 0) AS users,
    coalesce(sum(u.case_capacity), 0) AS capacity
FROM auth_group g
JOIN auth_user_groups ug ON ug.group_id = g.id
JOIN auth_user u ON u.id = ug.user_id AND u.is_active
WHERE g.name IN ('Lawyer', 'Paralegal')
GROUP BY g.name
ORDER BY g.name;
