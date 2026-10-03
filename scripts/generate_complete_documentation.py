"""
generate_complete_documentation.py
Builds professional, complete, and publication-quality documentation for the
AI-Powered Intelligent Video Interview Assessment System.

Outputs:
1. AI_Interview_System_Project_Documentation.pdf
2. AI_Interview_System_Project_Documentation.docx
"""

import os
import sys
import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image as RLImage
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = BASE_DIR
OUTPUT_PDF = os.path.join(ROOT_DIR, "AI_Interview_System_Project_Documentation.pdf")
OUTPUT_DOCX = os.path.join(ROOT_DIR, "AI_Interview_System_Project_Documentation.docx")
IMG_ADAPTIVE = os.path.join(ROOT_DIR, "frontend", "assets", "images", "adaptive_interview_ui.jpg")
IMG_PROCTORING = os.path.join(ROOT_DIR, "frontend", "assets", "images", "proctoring_alert_ui.jpg")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Running Header
        header_text = "AI-Powered Video Interview Assessment System  |  Comprehensive Project Documentation"
        self.drawString(45, 11 * 72 - 32, header_text)
        self.drawRightString(8.5 * 72 - 45, 11 * 72 - 32, "Computer Engineering Final Year Project")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(45, 11 * 72 - 36, 8.5 * 72 - 45, 11 * 72 - 36)

        # Running Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(45, 42, 8.5 * 72 - 45, 42)
        self.drawString(45, 30, "Confidential & Academic Reference Manual  -  Mid-West University")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 45, 30, page_str)

        self.restoreState()


# Helper to build styled callout boxes in ReportLab
def make_callout(text, style, bg_hex="#EFF6FF", border_hex="#3B82F6", title="NOTE"):
    p_title = Paragraph(f"<b>{title}:</b> {text}", style)
    t = Table([[p_title]], colWidths=[522])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_hex)),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(border_hex)),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return t


def make_table(headers, data, col_widths, hdr_style, cell_style, bg_header="#1E3A8A"):
    table_data = []
    hdr_row = [Paragraph(f"<b>{h}</b>", hdr_style) for h in headers]
    table_data.append(hdr_row)
    for row in data:
        row_cells = []
        for c in row:
            if isinstance(c, Paragraph):
                row_cells.append(c)
            else:
                row_cells.append(Paragraph(str(c), cell_style))
        table_data.append(row_cells)

    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(bg_header)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    return t
