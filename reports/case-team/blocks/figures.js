// Retool workflow JavaScript block "figures": turns the slide queries' rows
// into the template's placeholder values, each chart's data and the text
// requests for the deck.

// SQL blocks can return rows or columns depending on context; accept both.
const toRows = (data) =>
  Array.isArray(data)
    ? data
    : Object.keys(data).length
      ? data[Object.keys(data)[0]].map((_, i) =>
          Object.fromEntries(Object.keys(data).map((k) => [k, data[k][i]])),
        )
      : [];
const n = (v) => Number(v || 0);
const pct = (part, whole) => (whole ? Math.round((100 * part) / whole) : 0);
const sumBy = (rows, key) => rows.reduce((t, r) => t + n(r[key]), 0);

// Case types shown on every slide, in order, with Clerk's display names.
const TOPICS = [
  ["REPAIRS", "repairs", "Repairs"],
  ["BONDS", "bonds", "Bonds"],
  ["EVICTION_RETALIATORY", "eviction_retaliatory", "Eviction (Retaliatory)"],
];
const SHOWN = new Set(TOPICS.map(([topic]) => topic));

// Stages in the order slide 6 shows them, with Clerk's display names.
const STAGES = [
  ["UNSTARTED", "unstarted", "Not started"],
  ["CLIENT_AGREEMENT", "client_agreement", "Client agreement"],
  ["ADVICE", "advice", "Drafting advice"],
  ["VCAT_CAV", "vcat_cav", "VCAT/CAV"],
  ["NEGOTIATIONS", "negotiations", "Negotiations"],
  ["FORMAL_LETTER", "formal_letter", "Formal letter sent"],
  ["POST_CASE_INTERVIEW", "post_case_interview", "Post-case interview"],
];

// Totals are the sum of the rows shown, so anything without a row would make
// a table not add up: stop so the template can be changed instead.
const unshown = (rows, label, key = "topic") => {
  const known = key === "topic" ? SHOWN : new Set(STAGES.map(([s]) => s));
  const missing = [
    ...new Set(
      rows
        .filter((r) => !known.has(r[key]) && Object.values(r).some((v) => n(v)))
        .map((r) => r[key]),
    ),
  ];
  if (missing.length) {
    throw new Error(`${label}: no row for ${missing.join(", ")}; add one to the template.`);
  }
};

// Last month's saved figures, when there are any. "Compared to last month"
// uses them so it matches last month's report; without a row it falls back
// to recalculating last month, which can differ.
const previousRows = toRows(readPrevious.data);
console.log(
  `readPrevious (${setup.data.environment}, month before ${setup.data.month}): ` +
    `${previousRows.length} row(s); raw: ${JSON.stringify(readPrevious.data)}`,
);
const previousRow = previousRows[0];
const previous = previousRow
  ? typeof previousRow.figures === "string"
    ? JSON.parse(previousRow.figures)
    : previousRow.figures
  : null;
const fromPrevious = (key, recalculated) =>
  previous && typeof previous[key] === "number" ? previous[key] : recalculated;

const month = setup.data.month; // "YYYY-MM-01"
const date = new Date(`${month}T00:00:00Z`);
const values = {
  month_name: date.toLocaleString("en-AU", { month: "long", timeZone: "UTC" }),
  report_month: date.toLocaleString("en-AU", { month: "long", year: "numeric", timeZone: "UTC" }),
};
const charts = {};

// Slide 4: capacity. Total capacity is the lower of lawyer and paralegal
// capacity, since each case needs both.
const capacity = Object.fromEntries(toRows(slide4.data).map((r) => [r.role, r]));
const cap = (role, key) => n(capacity[role] && capacity[role][key]);
values.s4_lawyers_users = cap("Lawyer", "users");
values.s4_lawyers_capacity = cap("Lawyer", "capacity");
values.s4_paralegals_users = cap("Paralegal", "users");
values.s4_paralegals_capacity = cap("Paralegal", "capacity");
values.s4_total_capacity = Math.min(values.s4_lawyers_capacity, values.s4_paralegals_capacity);

// Slide 5: submissions received.
const s5 = toRows(slide5.data);
unshown(s5, "Slide 5");
const s5By = Object.fromEntries(s5.map((r) => [r.topic, r]));
let s5Received = 0;
let s5Eligible = 0;
let s5Awaiting = 0;
let s5LastMonth = 0;
for (const [topic, key] of TOPICS) {
  const r = s5By[topic] || {};
  values[`s5_${key}_received`] = n(r.received);
  values[`s5_${key}_eligible`] = n(r.eligible);
  values[`s5_${key}_awaiting`] = n(r.awaiting_assignment);
  s5Received += n(r.received);
  s5Eligible += n(r.eligible);
  s5Awaiting += n(r.awaiting_assignment);
  s5LastMonth += n(r.received_last_month);
}
values.s5_total_received = s5Received;
values.s5_total_eligible = s5Eligible;
values.s5_total_awaiting = s5Awaiting;
values.s5_eligible_pct = pct(s5Eligible, s5Received);
s5LastMonth = fromPrevious("s5_total_received", s5LastMonth);
const s5Change = s5LastMonth ? Math.round((100 * (s5Received - s5LastMonth)) / s5LastMonth) : 0;
// The rest of the sentence "This month we received N submissions, ...".
values.s5_received_change =
  s5Change === 0
    ? "the same number as last month"
    : `which is a ${Math.abs(s5Change)}% ${s5Change < 0 ? "decrease" : "increase"} in the number of submissions received compared to last month`;
charts.slide5 = [
  ["Topic", "Received", "Eligible", "Awaiting assignment"],
  ...TOPICS.map(([, key, label]) => [
    label,
    values[`s5_${key}_received`],
    values[`s5_${key}_eligible`],
    values[`s5_${key}_awaiting`],
  ]),
];

// Slide 6: cases open at month end, by stage and topic.
const s6 = toRows(slide6.data);
const s6This = s6.filter((r) => r.which === "this");
const s6Last = s6.filter((r) => r.which === "last");
unshown(s6This, "Slide 6");
unshown(s6This, "Slide 6", "stage");
const s6Cell = (stage, topic) =>
  n((s6This.find((r) => r.stage === stage && r.topic === topic) || {}).open_cases);
let s6Total = 0;
for (const [stage, stageKey] of STAGES) {
  let rowTotal = 0;
  for (const [topic, topicKey] of TOPICS) {
    const v = s6Cell(stage, topic);
    values[`s6_${stageKey}_${topicKey}`] = v;
    rowTotal += v;
  }
  values[`s6_${stageKey}_total`] = rowTotal;
  s6Total += rowTotal;
}
for (const [topic, topicKey] of TOPICS) {
  values[`s6_total_${topicKey}`] = STAGES.reduce((t, [stage]) => t + s6Cell(stage, topic), 0);
}
values.s6_total_total = s6Total;
const s6LastTotal = fromPrevious(
  "s6_total_total",
  sumBy(s6Last.filter((r) => SHOWN.has(r.topic)), "open_cases"),
);
const s6Diff = s6Total - s6LastTotal;
const s6DiffPct = s6LastTotal ? Math.round((100 * Math.abs(s6Diff)) / s6LastTotal) : 0;
values.s6_open_change =
  s6Diff === 0
    ? "There has been no change in the number of cases open compared to last month."
    : `There has been ${s6Diff > 0 ? "an increase" : "a decrease"} of ${Math.abs(s6Diff)} cases open compared to last month, which is a ${s6DiffPct}% ${s6Diff > 0 ? "increase" : "decrease"}.`;
// Cases open at month end against total capacity, including cases still
// awaiting assignment.
const s6Load = values.s4_total_capacity
  ? Math.round((100 * s6Total) / values.s4_total_capacity) - 100
  : 0;
values.s6_capacity_position =
  s6Load === 0 ? "at capacity" : `${Math.abs(s6Load)}% ${s6Load > 0 ? "over" : "under"} capacity`;
charts.slide6 = [
  ["Topic", "Open cases"],
  ...TOPICS.map(([, key, label]) => [label, values[`s6_total_${key}`]]),
];

// Slide 7: cases closed during the month, and how many had legal services
// provided (advice, tasks or representation).
const s7 = toRows(slide7.data);
const s7This = s7.filter((r) => r.which === "this");
const s7Last = s7.filter((r) => r.which === "last");
unshown(s7This, "Slide 7");
const s7By = Object.fromEntries(s7This.map((r) => [r.topic, r]));
let s7Closed = 0;
let s7Services = 0;
for (const [topic, key] of TOPICS) {
  const r = s7By[topic] || {};
  values[`s7_${key}_closed`] = n(r.closed);
  values[`s7_${key}_legal_services`] = n(r.closed_with_legal_services);
  values[`s7_${key}_legal_services_pct`] = pct(n(r.closed_with_legal_services), n(r.closed));
  s7Closed += n(r.closed);
  s7Services += n(r.closed_with_legal_services);
}
values.s7_total_closed = s7Closed;
values.s7_total_legal_services = s7Services;
values.s7_legal_services_pct = pct(s7Services, s7Closed);
const s7LastShown = s7Last.filter((r) => SHOWN.has(r.topic));
const s7LastClosed = fromPrevious("s7_total_closed", sumBy(s7LastShown, "closed"));
const s7LastPct = fromPrevious(
  "s7_legal_services_pct",
  pct(sumBy(s7LastShown, "closed_with_legal_services"), sumBy(s7LastShown, "closed")),
);
const s7Diff = s7Closed - s7LastClosed;
// The rest of the sentence "This month, we closed N cases, ...".
values.s7_closed_change =
  s7Diff === 0
    ? "the same number as the previous month"
    : `${Math.abs(s7Diff)} ${s7Diff > 0 ? "more" : "fewer"} than the previous month`;
values.s7_legal_services_change =
  values.s7_legal_services_pct === s7LastPct
    ? `This is the same as the previous month, in which ${s7LastPct}% of cases were closed with legal services provided.`
    : `This is ${values.s7_legal_services_pct > s7LastPct ? "an increase" : "a decrease"} from the previous month, in which ${s7LastPct}% of cases were closed with legal services provided.`;
charts.slide7 = [
  ["Topic", "Closed cases"],
  ...TOPICS.map(([, key, label]) => [label, values[`s7_${key}_closed`]]),
];

// Renters helped and legal problems this FY, from the "provided legal
// services" tick on cases open during the year. Rows
// without a topic are totals across topics; a renter with cases of two
// types counts once in them, so they can be less than the sum of the rows.
const rentersRows = toRows(renters.data);
const fyMonth = setup.data.fyMonth;
const rentersAt = (fy, k) => rentersRows.filter((r) => r.fy === fy && n(r.fy_month) === k);
const rentersNow = rentersAt("this", fyMonth);
unshown(rentersNow.filter((r) => r.topic), "Renters helped this FY");
const rentersTotal = (fy, k) => rentersAt(fy, k).find((r) => !r.topic) || {};

// Slide 8: case progress, and renters helped this month and this FY.
const s8 = toRows(slide8.data);
const s8Rows = (which) => s8.filter((r) => r.which === which && r.topic);
const s8Total = (which) => s8.find((r) => r.which === which && !r.topic) || {};
unshown(s8Rows("this"), "Slide 8");
const s8This = Object.fromEntries(s8Rows("this").map((r) => [r.topic, r]));
const s8Fy = Object.fromEntries(rentersNow.filter((r) => r.topic).map((r) => [r.topic, r]));
let s8Progressed = 0;
let s8Open = 0;
for (const [topic, key] of TOPICS) {
  const r = s8This[topic] || {};
  values[`s8_${key}_helped`] = n(r.helped_clients);
  values[`s8_${key}_progressed`] = n(r.progressed);
  values[`s8_${key}_helped_fy`] = n((s8Fy[topic] || {}).renters);
  s8Progressed += n(r.progressed);
  s8Open += n(r.open_cases);
}
values.s8_total_helped = n(s8Total("this").helped_clients);
values.s8_total_progressed = s8Progressed;
values.s8_total_helped_fy = n(rentersTotal("this", fyMonth).renters);
values.s8_legal_problems_fy = n(rentersTotal("this", fyMonth).legal_problems);
values.s8_open_cases = s8Open;
values.s8_progression_pct = pct(s8Progressed, s8Open);
const s8LastProgressed = fromPrevious(
  "s8_total_progressed",
  sumBy(s8Rows("last").filter((r) => SHOWN.has(r.topic)), "progressed"),
);
const s8Diff = s8Progressed - s8LastProgressed;
// The rest of the sentence "This month, N cases progressed, ...".
values.s8_progressed_change =
  s8Diff === 0
    ? "the same number as the previous month"
    : `${Math.abs(s8Diff)} ${s8Diff > 0 ? "more" : "fewer"} than the previous month`;

// Slide 9: legal services by financial year quarter, under the CLCA
// counting rules. Quarters still to come show blank.
const s9 = toRows(slide9.data);
const s9Cell = (category, quarter, key) =>
  n((s9.find((r) => r.category === category && n(r.quarter) === quarter) || {})[key]);
const fyQuarter = Math.floor(((date.getUTCMonth() + 6) % 12) / 3) + 1;
const s9Totals = { discrete: 0, ongoing: 0, all: 0, excluding_referrals: 0 };
for (let q = 1; q <= 4; q++) {
  const discrete = s9Cell("DISCRETE", q, "services");
  const ongoing = s9Cell("ONGOING", q, "services");
  const excluding =
    s9Cell("DISCRETE", q, "services_excluding_referrals") +
    s9Cell("ONGOING", q, "services_excluding_referrals");
  const shown = (v) => (q <= fyQuarter ? v : "");
  values[`s9_discrete_q${q}`] = shown(discrete);
  values[`s9_ongoing_q${q}`] = shown(ongoing);
  values[`s9_total_q${q}`] = shown(discrete + ongoing);
  values[`s9_excluding_referrals_q${q}`] = shown(excluding);
  s9Totals.discrete += discrete;
  s9Totals.ongoing += ongoing;
  s9Totals.all += discrete + ongoing;
  s9Totals.excluding_referrals += excluding;
}
values.s9_discrete_total = s9Totals.discrete;
values.s9_ongoing_total = s9Totals.ongoing;
values.s9_total_total = s9Totals.all;
values.s9_excluding_referrals_total = s9Totals.excluding_referrals;
values.s9_ongoing_still_open = s9Cell("STILL_OPEN", 0, "services");

// Slide 10: forecast of renters helped by the end of the financial year.
// Past months come from their saved figures where there are any, so the
// lines match what earlier reports showed; otherwise they are recalculated.
const history = Object.fromEntries(
  toRows(readHistory.data).map((r) => [
    String(r.month).slice(0, 7),
    typeof r.figures === "string" ? JSON.parse(r.figures) : r.figures,
  ]),
);
const fyStartYear = Number(setup.data.lastFyStart.slice(0, 4)) + 1;
const monthKey = (startYear, k) => {
  const m = ((k + 5) % 12) + 1;
  return `${m >= 7 ? startYear : startYear + 1}-${String(m).padStart(2, "0")}`;
};
const helpedBy = (fy, k) => {
  const saved = history[monthKey(fy === "this" ? fyStartYear : fyStartYear - 1, k)];
  return saved && typeof saved.s8_total_helped_fy === "number"
    ? saved.s8_total_helped_fy
    : n(rentersTotal(fy, k).renters);
};
const MONTHS = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"];
const now = values.s8_total_helped_fy;
const actual = MONTHS.map((_, i) => (i + 1 < fyMonth ? helpedBy("this", i + 1) : i + 1 === fyMonth ? now : null));
const lastYear = MONTHS.map((_, i) => helpedBy("last", i + 1));
// Day one: renters whose ticked cases were carried over from the year
// before, so already count when the year starts.
const dayOne = n(rentersTotal("this", 0).renters);
const lastDayOne = n(rentersTotal("last", 0).renters);
// Renters added each month last year.
const lastYearMonthly = lastYear.map((v, i) => v - (i ? lastYear[i - 1] : lastDayOne));
const rates = {
  projected: (lastYear[11] - lastDayOne) / 12,
  ambitious: Math.max(...lastYearMonthly),
  conservative: Math.min(...lastYearMonthly),
  average_progression: (now - dayOne) / fyMonth,
};
const line = (rate) => MONTHS.map((_, i) => (i + 1 >= fyMonth ? Math.round(now + rate * (i + 1 - fyMonth)) : null));
const lines = Object.fromEntries(Object.entries(rates).map(([key, rate]) => [key, line(rate)]));
for (const [key, rate] of Object.entries(rates)) {
  values[`s10_${key}_rate`] = Math.round(rate);
  values[`s10_${key}`] = lines[key][11];
}
values.s10_day_one = dayOne;
values.s10_last_year_total = lastYear[11];

// The target is set by the board each year, in the settings sheet. Without
// one for this year the report uses last year's and says so; with neither
// there is no Target line.
const fyLabel = setup.data.fyFolderName.replace("-", "/");
const lastFyLabel = `FY${setup.data.lastFyStart.slice(2, 4)}/${fyLabel.slice(2, 4)}`;
const normalise = (v) => String(v ?? "").toUpperCase().replace(/[^A-Z0-9]/g, "");
const cell = (row, header) => {
  const key = Object.keys(row).find((k) => normalise(k) === normalise(header));
  return key === undefined ? "" : String(row[key] ?? "").trim();
};
const settingsRows = toRows(readSettings.data);
// Blank is allowed; anything else must be a whole number, so a typo stops
// the run rather than quietly changing the target.
const targetFor = (label) => {
  const row = settingsRows.find((r) => normalise(cell(r, "Financial year")) === normalise(label));
  const v = row ? cell(row, "Target").replace(/,/g, "") : "";
  if (v === "") return null;
  if (!/^\d+$/.test(v)) {
    throw new Error(`Settings sheet, ${label} "Target": "${v}" isn't a whole number.`);
  }
  return Number(v);
};
const warnings = [];
const thisYearTarget = targetFor(fyLabel);
const lastYearTarget = targetFor(lastFyLabel);
const target = thisYearTarget ?? lastYearTarget;
if (thisYearTarget === null) {
  warnings.push(
    lastYearTarget === null
      ? `No target for ${fyLabel} or ${lastFyLabel} in the settings sheet, so the forecast has no Target line.`
      : `No target for ${fyLabel} in the settings sheet, so the forecast uses ${lastFyLabel}'s ${lastYearTarget}.`,
  );
}
values.s10_target = target ?? "";
values.s10_target_basis =
  thisYearTarget !== null
    ? `The board's target is to help ${target} renters this year.`
    : target !== null
      ? `A target hasn't been set for ${fyLabel} yet, so this uses ${lastFyLabel}'s target of ${target} renters.`
      : `A target hasn't been set for ${fyLabel} yet.`;
// The Target line rises evenly from day one to the target in June.
const targetAt = (k) => Math.round(dayOne + ((target - dayOne) * k) / 12);
if (target === null) {
  values.s10_target_position = "";
} else {
  const behind = targetAt(fyMonth) - now;
  values.s10_target_position =
    behind === 0
      ? "We are exactly on our target for this point in the year."
      : `We are ${Math.abs(behind)} renters ${behind > 0 ? "behind" : "ahead of"} our target for this point in the year.`;
}
values.s10_fy_label = fyLabel;
// Rounded down to a multiple of 10, for "on track to help over N renters".
values.s10_on_track = Math.floor(values.s10_projected / 10) * 10;
charts.slide10 = [
  ["Month", "Actual", "Target", "Projected", "Ambitious", "Conservative", "Average progression"],
  ...MONTHS.map((label, i) => [
    label,
    actual[i] ?? "",
    target === null ? "" : targetAt(i + 1),
    lines.projected[i] ?? "",
    lines.ambitious[i] ?? "",
    lines.conservative[i] ?? "",
    lines.average_progression[i] ?? "",
  ]),
];
for (const warning of warnings) console.log(`Warning: ${warning}`);

// One replaceAllText request per placeholder: the name in double braces.
// The braces are built from single characters because Retool's editor reads
// a literal double brace as its own template syntax.
const placeholder = (name) => "{" + "{" + name + "}" + "}";
const textRequests = Object.entries(values).map(([key, value]) => ({
  replaceAllText: {
    containsText: { text: placeholder(key), matchCase: true },
    replaceText: String(value),
  },
}));

// The snapshot row: every number the report shows, by placeholder name.
// Sentences are left out; they are rebuilt from the numbers.
const snapshotFigures = Object.fromEntries(
  Object.entries(values).filter(([, value]) => typeof value === "number"),
);

const deckName = `CT Monthly Report - ${values.report_month}`;
// Workflow logs show only what blocks print.
console.log(`Last month's figures from: ${previous ? "the saved row" : "recalculating"}`);
console.log(JSON.stringify(values, null, 2));
return {
  values,
  snapshot: {
    figures: snapshotFigures,
    // "current": today's capacity saved for a past month, to be replaced
    // with the month's own figure.
    capacitySource: setup.data.isLatestMonth ? "calculated" : "current",
  },
  lastMonthFrom: previous ? "snapshot" : "recalculated",
  // Problems someone should fix, for the run's Slack post.
  warnings,
  charts,
  textRequests,
  deckName,
  chartSheetName: `${deckName} - chart data`,
};
