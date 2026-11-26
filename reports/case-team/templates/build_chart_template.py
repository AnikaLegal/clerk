"""Build the chart spreadsheet template: one tab per chart, named after its
slide, holding sample figures for the chart to draw from.

Each run writes the month's figures over the sample ones in a copy, so the
tab names and ranges here must match the writeChart blocks. Upload the
result to the shared drive's Templates folder as a Google Sheets file.

Usage: build_chart_template.py <out.xlsx>
"""
import sys

from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList

out = sys.argv[1]
wb = Workbook()

def sheet(title, rows, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    for r in rows:
        ws.append(r)
    ws.column_dimensions["A"].width = 24
    for col in "BCD":
        ws.column_dimensions[col].width = 20
    return ws

s5 = sheet("slide5", [
    ["Topic", "Received", "Eligible", "Awaiting assignment"],
    ["Repairs", 18, 17, 3],
    ["Bonds", 20, 18, 1],
    ["Eviction (Retaliatory)", 23, 13, 2],
], first=True)
bar = BarChart()
bar.type = "col"
bar.title = "Submissions received"
bar.y_axis.title = "Cases"
bar.add_data(Reference(s5, min_col=2, max_col=4, min_row=1, max_row=4), titles_from_data=True)
bar.set_categories(Reference(s5, min_col=1, min_row=2, max_row=4))
bar.width, bar.height = 18, 9
s5.add_chart(bar, "F2")

def pie_sheet(title, header, rows, chart_title):
    ws = sheet(title, [["Topic", header]] + rows)
    pie = PieChart()
    pie.title = chart_title
    pie.add_data(Reference(ws, min_col=2, min_row=1, max_row=4), titles_from_data=True)
    pie.set_categories(Reference(ws, min_col=1, min_row=2, max_row=4))
    pie.dataLabels = DataLabelList()
    pie.dataLabels.showPercent = True
    pie.width, pie.height = 14, 9
    ws.add_chart(pie, "D2")

pie_sheet("slide6", "Open cases", [["Repairs", 51], ["Bonds", 53], ["Eviction (Retaliatory)", 15]], "Cases open by type")
pie_sheet("slide7", "Closed cases", [["Repairs", 34], ["Bonds", 25], ["Eviction (Retaliatory)", 23]], "Cases closed by type")
wb.save(out)
