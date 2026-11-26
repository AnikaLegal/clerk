-- The saved figures for the month before the report month, if any.
SELECT figures, capacity_source, generated_at
FROM monthly_report
WHERE month = (CAST({{ setup.data.month }} AS date) - interval '1 month')::date
  AND environment = {{ setup.data.environment }};
