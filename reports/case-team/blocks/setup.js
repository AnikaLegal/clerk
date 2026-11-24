// Retool workflow JavaScript block "setup": the run's inputs, which
// environment it's in, and where files come from and go.

// IDs from the Drive and Sheets URLs (see the README).
const TEMPLATE_DECK_ID = "1x1Z7Zzm7uz6qkNB_9b-AvIEPg7Rv2ad3Qu-LTJHM3g4";
const TEMPLATE_CHART_SHEET_ID = "12Sbhp5_NR3EGKN2HCKrAtwGDYGOc0ZahWONhTOO7UUw";
const SHARED_DRIVE_ID = "0ALSw4lHqZw42Uk9PVA";
const TEST_FOLDER_ID = "159_Q-NQdHAcDNyWaWzt5xN0jpr4aYVyB";

// The chart IDs inside the chart template, one per chart placeholder.
// Copies of the spreadsheet are expected to keep the same IDs.
const CHART_IDS = { chart_s5: 314671364, chart_s6: 1304035995, chart_s7: 168968951 };

// The environment comes from the database user that actually ran the
// queries, so a production run can never quietly save to Test.
const DB_USERS = {
  clerk_staging_reader: "staging",
  clerk_prod_reader: "production",
  clerk_prod: "production",
};
// SQL blocks can return rows or columns depending on context; accept both.
const dbUser = Array.isArray(whoami.data)
  ? whoami.data[0].current_user
  : whoami.data.current_user[0];
const environment = DB_USERS[dbUser];
if (!environment) {
  throw new Error(`Unexpected database user "${dbUser}"; stopping.`);
}
const isProduction = environment === "production";

// Inputs: month (defaults to the month just ended in Melbourne), mode and
// force.
const input = startTrigger.data || {};
const parts = new Intl.DateTimeFormat("en-CA", {
  timeZone: "Australia/Melbourne",
  year: "numeric",
  month: "2-digit",
}).formatToParts(new Date());
const thisYear = Number(parts.find((p) => p.type === "year").value);
const thisMonth = Number(parts.find((p) => p.type === "month").value);
const lastMonth =
  thisMonth === 1 ? `${thisYear - 1}-12-01` : `${thisYear}-${String(thisMonth - 1).padStart(2, "0")}-01`;

const month = input.month ? `${String(input.month).slice(0, 7)}-01` : lastMonth;
if (!/^\d{4}-(0[1-9]|1[0-2])-01$/.test(month)) {
  throw new Error(`month "${input.month}" isn't a month; use YYYY-MM.`);
}
// A month that hasn't ended would save figures that are still changing.
if (month > lastMonth) {
  throw new Error(`${month.slice(0, 7)} hasn't ended yet; the latest month to report on is ${lastMonth.slice(0, 7)}.`);
}

// report: everything; snapshot: save the month's figures only, no files.
const mode = input.mode || "report";
if (mode !== "report" && mode !== "snapshot") {
  throw new Error(`mode "${mode}" isn't report or snapshot.`);
}

// Reports are filed by the financial year (July to June) of the report
// month, not of the run date: the June report runs in July.
const [monthYear, monthNumber] = month.split("-").map(Number);
const fyStart = monthNumber >= 7 ? monthYear : monthYear - 1;
const yy = (y) => String(y % 100).padStart(2, "0");

return {
  month,
  mode,
  force: input.force === true,
  // Capacity only has a current value, so it is the month's own only when
  // the month has just ended.
  isLatestMonth: month === lastMonth,
  environment,
  templateDeckId: TEMPLATE_DECK_ID,
  templateChartSheetId: TEMPLATE_CHART_SHEET_ID,
  sharedDriveId: SHARED_DRIVE_ID,
  chartIds: CHART_IDS,
  fyFolderName: `FY${yy(fyStart)}-${yy(fyStart + 1)}`,
  // Staging builds the same folders inside Test, so the folder steps run
  // there too.
  rootFolderId: isProduction ? SHARED_DRIVE_ID : TEST_FOLDER_ID,
};
