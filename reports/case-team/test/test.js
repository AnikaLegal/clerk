// Runs the setup and figures blocks outside Retool against saved query
// results (fixtures/, from a local database) and checks the figures
// verified against the February and September 2026 reports.
// Usage: node test/test.js
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const here = __dirname;
const block = (name, ...scope) =>
  new Function(...scope, fs.readFileSync(path.join(here, "..", "blocks", `${name}.js`), "utf8"));
const fixture = (query, month) => {
  const name = typeof query === "number" ? `slide${query}` : query;
  return JSON.parse(fs.readFileSync(path.join(here, "fixtures", `${name}-${month}.json`), "utf8"));
};

const setupBlock = block("setup", "whoami", "startTrigger");
const figuresBlock = block("figures", "setup", "readPrevious", "readHistory", "readSettings", "slide4", "slide5", "slide6", "slide7", "slide8", "slide9", "renters");
const whoami = { data: [{ current_user: "clerk_staging_reader" }] };

const run = (month, previousFigures, history = [], settings = []) => {
  const setup = { data: setupBlock(whoami, { data: { month } }) };
  const readPrevious = { data: previousFigures ? [{ figures: previousFigures }] : [] };
  const readHistory = { data: history };
  const readSettings = { data: settings };
  const [s4, s5, s6, s7, s8, s9, renters] = [4, 5, 6, 7, 8, 9, "renters"].map((n) => ({ data: fixture(n, setup.data.month) }));
  const log = console.log;
  console.log = () => {};
  try {
    return figuresBlock(setup, readPrevious, readHistory, readSettings, s4, s5, s6, s7, s8, s9, renters);
  } finally {
    console.log = log;
  }
};

// setup
const feb = setupBlock(whoami, { data: { month: "2026-02" } });
assert.equal(feb.month, "2026-02-01");
assert.equal(feb.fyFolderName, "FY25-26");
assert.equal(setupBlock(whoami, { data: { month: "2026-07" } }).fyFolderName, "FY26-27");
assert.equal(feb.mode, "report");
assert.throws(() => setupBlock(whoami, { data: { month: "2026-02", mode: "snap" } }), /isn't report or snapshot/);
assert.throws(() => setupBlock(whoami, { data: { month: "2999-01" } }), /hasn't ended yet/);
assert.throws(() => setupBlock({ data: [{ current_user: "someone" }] }, { data: {} }), /Unexpected database user/);

// February 2026, last month recalculated.
const f = run("2026-02-01").values;
assert.equal(f.s5_total_received, 56);
assert.equal(f.s5_total_eligible, 45);
assert.equal(f.s5_total_awaiting, 23);
assert.equal(f.s6_total_total, 115);
assert.equal(f.s7_total_closed, 42);
assert.equal(f.s7_total_legal_services, 19);
assert.equal(f.s7_closed_change, "6 fewer than the previous month");
assert.equal(f.s8_total_progressed, 78);
assert.equal(f.s8_open_cases, 161);
assert.equal(f.s8_progression_pct, 48);
assert.equal(f.s8_progressed_change, "6 fewer than the previous month");
// Renters with cases of more than one type count once in the totals.
assert.equal(f.s8_repairs_helped + f.s8_bonds_helped + f.s8_eviction_retaliatory_helped, 122);
assert.equal(f.s8_total_helped, 121);
assert.equal(f.s8_repairs_helped_fy + f.s8_bonds_helped_fy + f.s8_eviction_retaliatory_helped_fy, 314);
assert.equal(f.s8_total_helped_fy, 306);
assert.equal(f.s8_legal_problems_fy, 314);
assert.equal(f.s9_discrete_q2, 79);
assert.equal(f.s9_total_q3, 85);
assert.equal(f.s9_excluding_referrals_q1, 133);
assert.equal(f.s9_total_q4, "");
assert.equal(f.s9_total_total, 409);
assert.equal(f.s9_excluding_referrals_total, 330);
assert.equal(f.s9_ongoing_still_open, 82);

// September 2026.
const s = run("2026-09-01").values;
assert.equal(s.s5_total_received, 61);
assert.equal(s.s5_total_eligible, 48);
assert.equal(s.s5_total_awaiting, 6);
assert.equal(s.s8_repairs_progressed, 53);
assert.equal(s.s8_bonds_progressed, 48);
assert.equal(s.s8_eviction_retaliatory_progressed, 28);
// Only July to September: services after the month's end don't count.
assert.equal(s.s9_total_q1, 330);
assert.equal(s.s9_total_q2, "");
assert.equal(s.s9_total_total, 330);

// September's forecast: 207 renters helped by month 3, 101 of them on day
// one. Last year went from 81 to 438, 21 to 38 a month.
const targets = (...rows) => rows.map(([fy, target]) => ({ "Financial year": fy, Target: target }));
const sf = run("2026-09-01", null, [], targets(["FY25/26", "400"], ["FY26/27", "425"]));
assert.equal(sf.values.s8_total_helped_fy, 207);
assert.equal(sf.values.s10_day_one, 101);
assert.equal(sf.values.s10_projected, 475);
assert.equal(sf.values.s10_ambitious, 549);
assert.equal(sf.values.s10_conservative, 396);
assert.equal(sf.values.s10_average_progression, 525);
assert.equal(sf.values.s10_on_track, 470);
// The Target line rises from day one's 101 to 425, 182 by September.
assert.equal(sf.values.s10_target, 425);
assert.equal(sf.values.s10_target_basis, "The board's target is to help 425 renters this year.");
assert.equal(sf.values.s10_target_position, "We are 25 renters ahead of our target for this point in the year.");
assert.deepEqual(sf.warnings, []);
assert.deepEqual(sf.charts.slide10[1], ["Jul", 143, 128, "", "", "", ""]);
assert.deepEqual(sf.charts.slide10[3], ["Sep", 207, 182, 207, 207, 207, 207]);
assert.deepEqual(sf.charts.slide10[12], ["Jun", "", 425, 475, 549, 396, 525]);
// No target for this year: last year's, with a warning.
const fallback = run("2026-09-01", null, [], targets(["FY25/26", "400"]));
assert.equal(fallback.values.s10_target, 400);
assert.equal(fallback.values.s10_target_basis, "A target hasn't been set for FY26/27 yet, so this uses FY25/26's target of 400 renters.");
assert.equal(fallback.warnings.length, 1);
// Neither: no Target line.
const none = run("2026-09-01");
assert.equal(none.values.s10_target, "");
assert.equal(none.charts.slide10[12][2], "");
assert.equal(none.warnings.length, 1);
assert.equal(run("2026-09-01", null, [], targets(["FY26/27", "1,200"])).values.s10_target, 1200);
assert.throws(() => run("2026-09-01", null, [], targets(["FY26/27", "about 400"])), /"about 400" isn't a whole number/);
// Saved months win over recalculating.
const sh = run("2026-09-01", null, [{ month: "2026-07-01", figures: { s8_total_helped_fy: 58 } }]);
assert.equal(sh.charts.slide10[1][1], 58);

// Last month's saved row wins over recalculating.
const saved = run("2026-02-01", { s5_total_received: 56, s6_total_total: 115, s7_total_closed: 42, s7_legal_services_pct: 45, s8_total_progressed: 78 });
assert.equal(saved.lastMonthFrom, "snapshot");
assert.equal(saved.values.s5_received_change, "the same number as last month");
assert.equal(saved.values.s7_closed_change, "the same number as the previous month");
assert.equal(saved.values.s8_progressed_change, "the same number as the previous month");

// The snapshot row holds numbers only.
assert.ok(Object.values(saved.snapshot.figures).every((v) => typeof v === "number"));

console.log("ok");
