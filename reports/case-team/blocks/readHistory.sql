-- The saved figures for every month from the start of the last financial
-- year to the month before the report month.
SELECT month, figures
FROM monthly_report
WHERE month >= CAST({{ setup.data.lastFyStart }} AS date)
  AND month < CAST({{ setup.data.month }} AS date)
  AND environment = {{ setup.data.environment }}
ORDER BY month;
