-- Snapshot mode: save the month's figures. An existing row is kept unless
-- the run is forced, since a report may already show it.
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
WHERE {{ setup.data.force ? "yes" : "no" }} = 'yes'
RETURNING month, environment, capacity_source, generated_at;
