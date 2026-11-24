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
const figuresBlock = block("figures", "setup", "readPrevious", "slide4", "slide5", "slide6", "slide7");
const whoami = { data: [{ current_user: "clerk_staging_reader" }] };

const run = (month, previousFigures) => {
  const setup = { data: setupBlock(whoami, { data: { month } }) };
  const readPrevious = { data: previousFigures ? [{ figures: previousFigures }] : [] };
  const [s4, s5, s6, s7] = [4, 5, 6, 7].map((n) => ({ data: fixture(n, setup.data.month) }));
  const log = console.log;
  console.log = () => {};
  try {
    return figuresBlock(setup, readPrevious, s4, s5, s6, s7);
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
assert.equal(f.s7_total_legal_advice, 19);
assert.equal(f.s7_closed_change, "6 fewer than the previous month");

// September 2026.
const s = run("2026-09-01").values;
assert.equal(s.s5_total_received, 61);
assert.equal(s.s5_total_eligible, 48);
assert.equal(s.s5_total_awaiting, 6);

// Last month's saved row wins over recalculating.
const saved = run("2026-02-01", { s5_total_received: 56, s6_total_total: 115, s7_total_closed: 42, s7_legal_advice_pct: 45 });
assert.equal(saved.lastMonthFrom, "snapshot");
assert.equal(saved.values.s5_received_change, "the same number as last month");
assert.equal(saved.values.s7_closed_change, "the same number as the previous month");

// The snapshot row holds numbers only.
assert.ok(Object.values(saved.snapshot.figures).every((v) => typeof v === "number"));

console.log("ok");
