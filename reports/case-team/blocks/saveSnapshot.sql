-- Report mode: save the month's figures, replacing any earlier row. This
-- only runs when no report exists for the month or the run is forced, so the
-- row always matches the report about to be made.
INSERT INTO monthly_report (month, environment, figures, capacity_source, generated_at)
VALUES (
    CAST({{ setup.data.month }} AS date),
    {{ setup.data.environment }},
    CAST({{ JSON.stringify(figures.data.snapshot.figures) }} AS jsonb),
    {{ figures.data.snapshot.capacitySource }},
    now()
)
ON CONFLICT (month, environment) DO UPDATE
SET figures = EXCLUDED.figures,
    capacity_source = EXCLUDED.capacity_source,
    generated_at = EXCLUDED.generated_at
RETURNING month, environment, capacity_source, generated_at;
