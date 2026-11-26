-- Retool Database: one row per report month and environment.
-- figures holds every number the report shows, keyed by placeholder name.
-- capacity_source says where the s4_* capacity figures came from:
-- calculated (at the month's end), spreadsheet (copied from CT Monthly Dash)
-- or current (today's value saved for a past month, to be replaced).
CREATE TABLE monthly_report (
    month date NOT NULL CHECK (extract(day FROM month) = 1),
    environment text NOT NULL CHECK (environment IN ('staging', 'production')),
    figures jsonb NOT NULL,
    capacity_source text NOT NULL CHECK (capacity_source IN ('calculated', 'spreadsheet', 'current')),
    generated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (month, environment)
);
