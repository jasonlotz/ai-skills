"""
Cleartelligence Word Document helpers.
Import these in any build script:
    from scripts.ct_helpers import set_cell_bg, add_callout, make_footer
"""

from docx.shared import Pt, RGBColor, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── Brand colors ───────────────────────────────────────────────────
NAVY    = "182D4F"   # Primary — table headers, H1
BLUE    = "3364AC"   # Secondary — H2, sub-headers
LT_BLUE = "3D8EC8"   # Accent — callout borders, H4
ORANGE  = "EC8E2E"   # Highlight accent
WHITE   = "FFFFFF"
LT_GRAY = "F4F5F7"   # Alternating table rows
DARK    = "110B18"   # Body text


def set_cell_bg(cell, hex_color):
    """Set background fill color on a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_callout(doc, label, text, border_color=BLUE):
    """Add a left-bordered callout paragraph."""
    p = doc.add_paragraph(style="Normal")
    p.paragraph_format.left_indent = Twips(360)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "12")
    left.set(qn("w:space"), "12")
    left.set(qn("w:color"), border_color)
    pBdr.append(left)
    pPr.append(pBdr)
    run_label = p.add_run(label + "  ")
    run_label.bold = True
    p.add_run(text)
    return p


def make_footer(doc, title):
    """Add a centered gray italic footer: Working draft | <title> | Cleartelligence"""
    section = doc.sections[0]
    footer = section.footer
    footer_para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    footer_para.clear()
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer_para.add_run(f"Working draft  |  {title}  |  Cleartelligence")
    run.italic = True
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)


def add_subtitle(doc, text):
    """Add a gray italic subtitle / date line."""
    p = doc.add_paragraph(style="Normal")
    run = p.add_run(text)
    run.italic = True
    run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    return p


def make_table(doc, headers, rows):
    """
    Create a branded table with navy header row and alternating gray rows.
    headers: list of str
    rows: list of lists of str
    """
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    hdr_cells = table.rows[0].cells
    for cell, text in zip(hdr_cells, headers):
        set_cell_bg(cell, NAVY)
        run = cell.paragraphs[0].add_run(text)
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for i, row_data in enumerate(rows):
        row_cells = table.add_row().cells
        bg = LT_GRAY if i % 2 == 0 else WHITE
        for cell, text in zip(row_cells, row_data):
            set_cell_bg(cell, bg)
            cell.paragraphs[0].add_run(text)
    return table
