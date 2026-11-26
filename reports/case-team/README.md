# Case Team monthly report

The source of the Retool workflow **Case Team report**, which builds the Case
Team's monthly Google Slides report from Clerk's database (TEC-2280). Figure
definitions are in the Linear document "Case Team report definitions" on that
issue.

Retool runs the workflow; this folder is where its code is written, reviewed
and kept. Change a file here first, then copy it into Retool.

## What a run does

1. `whoami` and `setup` work out the environment from the database user
   (`clerk_staging_reader` is staging; `clerk_prod_reader` and `clerk_prod`
   are production; anything else stops the run), and read the inputs.
2. `readPrevious` and `readHistory` read last month's saved figures and
   every saved month back to the start of last financial year, and
   `readSettings` reads the settings sheet. `slide4` to
   `slide9` and `renters` read this month's figures from Clerk. `figures`
   turns them into placeholder values, chart data and the sentences.
3. `isSnapshot`: in snapshot mode, `saveSnapshotOnly` saves the month's row
   and the run ends.
4. Otherwise `folders` finds or creates the financial year folder, and
   `alreadyMade` stops the run with the existing report's link unless it is
   forced.
5. `saveSnapshot` saves the month's row, then the run copies the chart
   spreadsheet and deck templates, fills them, and swaps in the charts.

Inputs, as JSON on the start trigger:

| Input | Values | Default |
| --- | --- | --- |
| `month` | `YYYY-MM` or `YYYY-MM-DD` | The month just ended, in Melbourne |
| `mode` | `report` or `snapshot` (saves the figures only, no files) | `report` |
| `force` | `true` makes a new report, or replaces a saved row, even if one exists | `false` |

## Layout

- `blocks/`: one file per workflow block with code, named after the block.
  Clerk queries take `:month`, so they also run in `psql`; the generator turns
  it into `{{ setup.data.month }}`. Retool Database queries use Retool's
  `{{ }}` directly.
- `monthly_report.sql`: the snapshot table in Retool Database. Retool keeps
  separate staging and production databases, and the table exists in both.
- `build/generate.py`: builds the workflow import from an export.
- `templates/`: builders for the Slides template and the chart spreadsheet
  template.
- `test/`: runs `setup` and `figures` against saved query results.

## Changing the workflow

A change to a block's code: edit its file, run the test, and paste the file
into that block in Retool.

A change to the blocks themselves (added, removed or reconnected): update
`build/generate.py`, export the workflow from Retool, and build a new import:

```bash
python3 build/generate.py <export.json> <import.json>
```

The generator keeps the settings that live only in Retool. Import the result
as a new workflow, check it, then delete the old one.

## Testing

```bash
node test/test.js
```

`test/fixtures/` holds the Clerk queries' results for February and September
2026 from the local database. Refresh a month's fixtures after changing a
query, with `just dev` running:

```bash
test/fixtures.sh 2026-02-01
```

## Blocks set up only in Retool

These blocks have no code file. Drive calls pass `supportsAllDrives=true`.

| Block | Resource | Call |
| --- | --- | --- |
| `readSettings` | Reports Sheets | Read `{{ setup.data.settingsSheetId }}`, range `targets!A:B`, first row as headers |
| `findExisting` | Reports Drive | `GET /files`, the month's deck by name in the deck folder |
| `copyChartSheet` | Reports Drive | `POST /files/{id}/copy` of the chart template into `Chart data` |
| `writeChart`, `writeChart6`, `writeChart7` | Reports Sheets | Update the copy's `slide5`, `slide6` and `slide7` tabs, with A1 ranges that name the tab |
| `copyDeck` | Reports Drive | `POST /files/{id}/copy` of the deck template into the year's folder |
| `fillText`, `fillCharts` | Reports Slides | `POST /presentations/{id}:batchUpdate` |
| `findFolder`, `createFolder` | Reports Drive | Workflow functions taking `name` and `parentId`, used by `folders` |

Retool quirks that shape the code:

- A code block can't contain a literal double brace, so placeholders are built
  from single characters.
- Request bodies are sent as per-field rows: `parents` is an array row,
  `[{{ id }}]`.
- A Branch can't rejoin the main path, so the folder lookup calls workflow
  functions from a code block instead of branching.
- Block outputs are hard to find in the editor, so blocks log what matters.

## Google setup

The service account `retool-reports` is a Contributor on the **Case Team
Reports** shared drive, used by the Reports Drive, Reports Slides and Reports
Sheets resources. The drive holds:

```
Case Team Reports/
  Templates/          the deck and chart spreadsheet templates
  FY25-26/            one folder per financial year, made by the run
    Chart data/       that year's chart spreadsheets
  Test/               staging runs, with the same folders inside
```

The **Case Team report settings** sheet in Templates holds each year's target
number of renters helped, set by the board, on its `targets` tab:

| Financial year | Target |
| --- | --- |
| FY26/27 | 425 |

Add each year's row once the board sets it, and keep past years' rows so
re-running an old month uses the target it had. Without a row for the year,
the report uses last year's target and warns; anything but a whole number
stops the run.

`blocks/setup.js` holds the templates' and settings sheet's IDs and the
templates' chart IDs. A copied
spreadsheet keeps its chart IDs, so a template's chart IDs work for every
copy; after replacing a template, update them.

## Templates

```bash
uv run --with python-pptx python templates/build_deck.py <live deck.pptx> <template.pptx>
uv run --with openpyxl python templates/build_chart_template.py <template.xlsx>
```

Upload each to `Templates/` as a Google file (Slides, Sheets).
