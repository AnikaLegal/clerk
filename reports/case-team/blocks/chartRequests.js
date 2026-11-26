// Retool workflow JavaScript block "chartRequests": swaps each chart
// placeholder box (e.g. chart_s5 in double braces) for that chart from this month's copy
// of the chart sheet, linked so it stays editable. Sent separately from the
// text so neither update runs long.
// Braces built from single characters: Retool's editor reads a literal
// double brace as its own template syntax.
const placeholder = (name) => "{" + "{" + name + "}" + "}";

return {
  requests: Object.entries(setup.data.chartIds).map(([name, chartId]) => ({
    replaceAllShapesWithSheetsChart: {
      containsText: { text: placeholder(name), matchCase: true },
      spreadsheetId: copyChartSheet.data.id,
      chartId,
      linkingMode: "LINKED",
    },
  })),
};
