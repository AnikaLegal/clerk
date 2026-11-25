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
const fixture = (slide, month) =>
  JSON.parse(fs.readFileSync(path.join(here, "fixtures", `slide${slide}-${month}.json`), "utf8"));

const setupBlock = block("setup", "whoami", "startTrigger");
const figuresBlock = block("figures", "setup", "readPrevious", "slide4", "slide5", "slide6", "slide7", "slide8", "slide9");
const whoami = { data: [{ current_user: "clerk_staging_reader" }] };

const run = (month, previousFigures) => {
  const setup = { data: setupBlock(whoami, { data: { month } }) };
  const readPrevious = { data: previousFigures ? [{ figures: previousFigures }] : [] };
  const [s4, s5, s6, s7, s8, s9] = [4, 5, 6, 7, 8, 9].map((n) => ({ data: fixture(n, setup.data.month) }));
  const log = console.log;
  console.log = () => {};
  try {
    return figuresBlock(setup, readPrevious, s4, s5, s6, s7, s8, s9);
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

// Last month's saved row wins over recalculating.
const saved = run("2026-02-01", { s5_total_received: 56, s6_total_total: 115, s7_total_closed: 42, s7_legal_services_pct: 45, s8_total_progressed: 78 });
assert.equal(saved.lastMonthFrom, "snapshot");
assert.equal(saved.values.s5_received_change, "the same number as last month");
assert.equal(saved.values.s7_closed_change, "the same number as the previous month");
assert.equal(saved.values.s8_progressed_change, "the same number as the previous month");

// The snapshot row holds numbers only.
assert.ok(Object.values(saved.snapshot.figures).every((v) => typeof v === "number"));

console.log("ok");
