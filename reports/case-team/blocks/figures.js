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

// Slide 7: cases closed during the month, and how many had legal advice.
const s7 = toRows(slide7.data);
const s7This = s7.filter((r) => r.which === "this");
const s7Last = s7.filter((r) => r.which === "last");
unshown(s7This, "Slide 7");
const s7By = Object.fromEntries(s7This.map((r) => [r.topic, r]));
let s7Closed = 0;
let s7Advice = 0;
for (const [topic, key] of TOPICS) {
  const r = s7By[topic] || {};
  values[`s7_${key}_closed`] = n(r.closed);
  values[`s7_${key}_legal_advice`] = n(r.closed_with_legal_advice);
  values[`s7_${key}_legal_advice_pct`] = pct(n(r.closed_with_legal_advice), n(r.closed));
  s7Closed += n(r.closed);
  s7Advice += n(r.closed_with_legal_advice);
}
values.s7_total_closed = s7Closed;
values.s7_total_legal_advice = s7Advice;
values.s7_legal_advice_pct = pct(s7Advice, s7Closed);
const s7LastShown = s7Last.filter((r) => SHOWN.has(r.topic));
const s7LastClosed = fromPrevious("s7_total_closed", sumBy(s7LastShown, "closed"));
const s7LastPct = fromPrevious(
  "s7_legal_advice_pct",
  pct(sumBy(s7LastShown, "closed_with_legal_advice"), sumBy(s7LastShown, "closed")),
);
const s7Diff = s7Closed - s7LastClosed;
// The rest of the sentence "This month, we closed N cases, ...".
values.s7_closed_change =
  s7Diff === 0
    ? "the same number as the previous month"
    : `${Math.abs(s7Diff)} ${s7Diff > 0 ? "more" : "fewer"} than the previous month`;
values.s7_legal_advice_change =
  values.s7_legal_advice_pct === s7LastPct
    ? `This is the same as the previous month, in which ${s7LastPct}% of cases were closed with legal advice.`
    : `This is ${values.s7_legal_advice_pct > s7LastPct ? "an increase" : "a decrease"} from the previous month, in which ${s7LastPct}% of cases were closed with legal advice.`;
charts.slide7 = [
  ["Topic", "Closed cases"],
  ...TOPICS.map(([, key, label]) => [label, values[`s7_${key}_closed`]]),
];

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
  charts,
  textRequests,
  deckName,
  chartSheetName: `${deckName} - chart data`,
};
