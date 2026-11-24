"""Build the report's Slides template from a copy of the live deck.

Keeps slides 4 to 7, swaps each figure for a placeholder such as
{{s5_total_received}} and each chart for a box holding {{chart_s5}}.
Upload the result to the shared drive's Templates folder as a Google Slides
file.

Usage: build_deck.py <live deck.pptx> <out.pptx>
"""
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Emu, Inches, Pt

src, out = sys.argv[1], sys.argv[2]
prs = Presentation(src)

# Keep slides 4 to 7 (indexes 3 to 6).
KEEP = {3, 4, 5, 6}
sld_ids = prs.slides._sldIdLst
for i, sld_id in reversed(list(enumerate(list(sld_ids)))):
    if i not in KEEP:
        prs.part.drop_rel(sld_id.rId)
        sld_ids.remove(sld_id)
s4, s5, s6, s7 = prs.slides


def set_text(paragraph, text):
    """Put text in the paragraph's first run, keeping its formatting, and drop the other runs."""
    runs = paragraph.runs
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def set_cell(table, row, col, text):
    set_text(table.cell(row, col).text_frame.paragraphs[0], text)


def ph(name):
    return "{{%s}}" % name


def shape(slide, shape_id):
    return next(sh for sh in slide.shapes if sh.shape_id == shape_id)


def drop_rows(table, rows):
    trs = table._tbl.tr_lst
    for r in sorted(rows, reverse=True):
        table._tbl.remove(trs[r])


def drop_column(table, col):
    grid = table._tbl.tblGrid
    grid.remove(grid.gridCol_lst[col])
    for tr in table._tbl.tr_lst:
        tr.remove(tr.tc_lst[col])


def replace_paragraphs(text_shape, mapping):
    for p in text_shape.text_frame.paragraphs:
        for start, text in mapping.items():
            if p.text.startswith(start):
                set_text(p, text)


def chart_box(slide, name, left, top, width, height):
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    box.fill.background()
    box.line.color.rgb = RGBColor(0x88, 0x87, 0x80)
    box.line.width = Pt(0.75)
    box.text_frame.text = ph(name)
    run = box.text_frame.paragraphs[0].runs[0]
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x5F, 0x5E, 0x5A)


def swap_picture_for_box(slide, picture_id, name):
    pic = shape(slide, picture_id)
    left, top, width, height = pic.left, pic.top, pic.width, pic.height
    pic._element.getparent().remove(pic._element)
    chart_box(slide, name, left, top, width, height)


TOPICS = [("repairs", "Repairs"), ("bonds", "Bonds"), ("eviction_retaliatory", "Eviction (Retaliatory)")]

# Slide 4: capacity.
t4 = shape(s4, 150).table
set_cell(t4, 1, 1, ph("s4_lawyers_users"))
set_cell(t4, 1, 2, ph("s4_lawyers_capacity"))
set_cell(t4, 2, 1, ph("s4_paralegals_users"))
set_cell(t4, 2, 2, ph("s4_paralegals_capacity"))
set_cell(t4, 3, 2, ph("s4_total_capacity"))

# Slide 5: submissions. Rows: header, Repairs, Eviction_Arrears, Bonds,
# Eviction_Retaliatory, Total; Arrears goes.
t5 = shape(s5, 160).table
drop_rows(t5, [2])
for r, (key, label) in enumerate(TOPICS + [("total", "Total")], start=1):
    set_cell(t5, r, 0, label)
    for c, col in enumerate(["received", "eligible", "awaiting"], start=1):
        set_cell(t5, r, c, ph("s5_%s_%s" % (key, col)))
replace_paragraphs(shape(s5, 162), {
    "This month we received": "This month we received %s submissions, %s" % (ph("s5_total_received"), ph("s5_received_change")),
    "80% were": "%s%% were eligible upon submission" % ph("s5_eligible_pct"),
    "7 matters were": "%s matters were awaiting assignment at the end of %s." % (ph("s5_total_awaiting"), ph("month_name")),
})
# The chart sits in the left column below the table, clear of the bullets.
pic5 = shape(s5, 161)
pic5._element.getparent().remove(pic5._element)
chart_box(s5, "chart_s5", Emu(366600), Inches(2.4), Inches(4.6), Inches(2.85))

# Slide 6: cases open. Columns: label, Repairs, Bonds, Eviction_retaliatory,
# Health_Check, Total; Health_Check goes. Rows: header, Total, then stages.
t6 = shape(s6, 171).table
drop_column(t6, 4)
for c, (key, label) in enumerate(TOPICS, start=1):
    set_cell(t6, 0, c, label)
STAGES = [
    ("UNSTARTED", "unstarted", "Not started"),
    ("CLIENT_AGREEMENT", "client_agreement", "Client agreement"),
    ("ADVICE", "advice", "Drafting advice"),
    ("VCAT_CAV", "vcat_cav", "VCAT/CAV"),
    ("NEGOTIATIONS", "negotiations", "Negotiations"),
    ("FORMAL_LETTER", "formal_letter", "Formal letter sent"),
    ("POST_CASE_INTERVIEW", "post_case_interview", "Post-case interview"),
]
rows6 = [("total", "Total")] + [(key, label) for _, key, label in STAGES]
for r, (stage_key, label) in enumerate(rows6, start=1):
    set_cell(t6, r, 0, label)
    for c, (topic_key, _) in enumerate(TOPICS + [("total", "Total")], start=1):
        set_cell(t6, r, c, ph("s6_%s_%s" % (stage_key, topic_key)))
replace_paragraphs(shape(s6, 173), {
    "There has been": ph("s6_open_change"),
    "As at the end of": "As at the end of %s we were operating %s (see slide 4 for the capacity limit)." % (ph("month_name"), ph("s6_capacity_position")),
})
swap_picture_for_box(s6, 172, "chart_s6")

# Slide 7: cases closed. Rows: header, Repairs, Bonds, Eviction,
# Health_Check, Eviction_Retaliatory, Rent_Reduction, Other, Total.
t7 = shape(s7, 183).table
drop_rows(t7, [3, 4, 6, 7])
for r, (key, label) in enumerate(TOPICS + [("total", "Total")], start=1):
    set_cell(t7, r, 0, label)
    set_cell(t7, r, 1, ph("s7_%s_closed" % key))
    set_cell(t7, r, 2, ph("s7_%s_legal_advice" % key))
replace_paragraphs(shape(s7, 185), {
    "This month, we closed": "This month, we closed %s cases, %s." % (ph("s7_total_closed"), ph("s7_closed_change")),
    "59% cases closed": "%s%% of cases were closed with legal advice:" % ph("s7_legal_advice_pct"),
    "67% in Repairs": "%s%% of Repairs cases" % ph("s7_repairs_legal_advice_pct"),
    "67% in Bonds": "%s%% of Bonds cases" % ph("s7_bonds_legal_advice_pct"),
    "39% in Evictions": "%s%% of Eviction (Retaliatory) cases" % ph("s7_eviction_retaliatory_legal_advice_pct"),
    "This is an increase": ph("s7_legal_advice_change"),
})
# Same arrangement as slide 5: table at the top left, chart below it, and
# the commentary on the right starting level with the table.
table7 = shape(s7, 183)
table7.left, table7.top = Emu(366600), Emu(821700)
shape(s7, 185).top = Emu(821700)
pic7 = shape(s7, 184)
pic7._element.getparent().remove(pic7._element)
chart_box(s7, "chart_s7", Emu(366600), Inches(2.4), Inches(4.6), Inches(2.85))

prs.save(out)
