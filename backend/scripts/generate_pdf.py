"""
generate_pdf.py
Generates a professional, beautifully formatted PDF document:
IT_Simple_Questions_Answers.pdf

Features:
- Organized cleanly by the 21 IT categories
- Includes 525 questions with exactly 3 distinct answers each (Short, Simple, Detailed)
- Professional styling with colored headers, card-style borders, and running page numbers
"""

import os
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "it_questions.json")
OUTPUT_PDF_ROOT = os.path.join(ROOT_DIR, "IT_Simple_Questions_Answers.pdf")
OUTPUT_PDF_BACKEND = os.path.join(BASE_DIR, "reports", "IT_Simple_Questions_Answers.pdf")

# Custom Canvas for dynamic 'Page X of Y' page numbering and running headers
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
            # Skip header/footer on cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Running Header
        self.drawString(54, 11 * 72 - 36, "IT Technical Interview Q&A Repository  |  AI Interview Assessment System")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

        # Running Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 30, page_text)
        self.drawString(54, 30, "Confidential - Mid-West University Graduate School of Engineering")
        self.line(54, 42, 8.5 * 72 - 54, 42)

        self.restoreState()


def build_pdf(json_path=DATASET_PATH, output_path=OUTPUT_PDF_ROOT):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Dataset not found at {json_path}. Run generate_dataset.py first.")

    with open(json_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    # Ensure output directories exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_PDF_BACKEND), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Define custom typography styles
    cover_title_style = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#1A365D"),
        alignment=1,
        spaceAfter=12
    )

    cover_subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
        spaceAfter=20
    )

    category_title_style = ParagraphStyle(
        "CategoryTitle",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.white,
        spaceBefore=0,
        spaceAfter=0
    )

    q_num_style = ParagraphStyle(
        "QuestionNumber",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=4,
        spaceAfter=4
    )

    a1_style = ParagraphStyle(
        "Answer1",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
        spaceBefore=1,
        spaceAfter=2
    )

    a2_style = ParagraphStyle(
        "Answer2",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
        spaceBefore=1,
        spaceAfter=2
    )

    a3_style = ParagraphStyle(
        "Answer3",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
        spaceBefore=1,
        spaceAfter=4
    )

    story = []

    # -------------------------------------------------------------
    # 1. Cover Page
    # -------------------------------------------------------------
    story.append(Spacer(1, 40))
    story.append(Paragraph("AI-POWERED INTERVIEW SYSTEM", ParagraphStyle("Badge", fontName="Helvetica-Bold", fontSize=10, textColor=colors.HexColor("#3182CE"), alignment=1, spaceAfter=8)))
    story.append(Paragraph("IT Interview Questions & Answers", cover_title_style))
    story.append(Paragraph("500+ Beginner-Level Technical Questions with Multi-Depth Answers", cover_subtitle_style))
    story.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor("#3182CE"), spaceAfter=25, spaceBefore=5))

    # Meta Overview Box
    categories = []
    category_map = {}
    for q in questions:
        cat = q["category"]
        if cat not in category_map:
            category_map[cat] = []
            categories.append(cat)
        category_map[cat].append(q)

    summary_data = [
        [
            Paragraph("<b>Total Questions:</b>", styles["Normal"]),
            Paragraph(f"<b>{len(questions)}</b>", styles["Normal"]),
            Paragraph("<b>Total Categories:</b>", styles["Normal"]),
            Paragraph(f"<b>{len(categories)}</b>", styles["Normal"])
        ],
        [
            Paragraph("<b>Answers per Question:</b>", styles["Normal"]),
            Paragraph("3 (Short, Standard, Detailed)", styles["Normal"]),
            Paragraph("<b>Difficulty:</b>", styles["Normal"]),
            Paragraph("Beginner / Junior IT", styles["Normal"])
        ],
        [
            Paragraph("<b>Target Audience:</b>", styles["Normal"]),
            Paragraph("Undergraduate / Entry IT Roles", styles["Normal"]),
            Paragraph("<b>System Integration:</b>", styles["Normal"]),
            Paragraph("AI Interview Pipeline + FastAPI", styles["Normal"])
        ]
    ]

    summary_table = Table(summary_data, colWidths=[120, 130, 120, 130])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EDF2F7")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 25))

    # Table of Categories
    story.append(Paragraph("<b>Table of Covered IT Categories</b>", ParagraphStyle("TOCHeader", fontName="Helvetica-Bold", fontSize=12, textColor=colors.HexColor("#2D3748"), spaceAfter=10)))

    half = (len(categories) + 1) // 2
    toc_data = []
    for i in range(half):
        cat1 = f"<b>{i+1}. {categories[i]}</b> ({len(category_map[categories[i]])} Qs)"
        if i + half < len(categories):
            cat2 = f"<b>{i+half+1}. {categories[i+half]}</b> ({len(category_map[categories[i+half]])} Qs)"
        else:
            cat2 = ""
        toc_data.append([Paragraph(cat1, styles["Normal"]), Paragraph(cat2, styles["Normal"])])

    toc_table = Table(toc_data, colWidths=[250, 250])
    toc_table.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
    ]))
    story.append(toc_table)

    story.append(Spacer(1, 30))
    story.append(Paragraph("<i>Note: Every question is structured with three semantic answer tiers: Answer 1 (Direct/Short), Answer 2 (Standard Explanation), and Answer 3 (Comprehensive/Detailed Context).</i>", ParagraphStyle("Notice", fontName="Helvetica-Oblique", fontSize=8.5, textColor=colors.HexColor("#718096"), alignment=1)))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 2. Categorized Question Content
    # -------------------------------------------------------------
    cat_idx = 1
    for cat_name in categories:
        q_list = category_map[cat_name]

        # Category Banner Table
        cat_banner = Table([[
            Paragraph(f"Category {cat_idx}: {cat_name.upper()} ({len(q_list)} Questions)", category_title_style)
        ]], colWidths=[504])
        cat_banner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2B6CB0")),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(cat_banner)
        story.append(Spacer(1, 10))

        for q in q_list:
            q_flowables = []
            q_num_text = f"<b>Question {q['id']}:</b> {q['question']}"
            q_flowables.append(Paragraph(q_num_text, q_num_style))

            a1_text = f"<b>Answer 1:</b> {q['answer_1']}"
            q_flowables.append(Paragraph(a1_text, a1_style))

            a2_text = f"<b>Answer 2:</b> {q['answer_2']}"
            q_flowables.append(Paragraph(a2_text, a2_style))

            a3_text = f"<b>Answer 3:</b> {q['answer_3']}"
            q_flowables.append(Paragraph(a3_text, a3_style))

            # Put into a card-style bordered table
            card_table = Table([[q_flowables]], colWidths=[504])
            card_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#E2E8F0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))

            story.append(KeepTogether([card_table, Spacer(1, 8)]))

        story.append(Spacer(1, 10))
        cat_idx += 1

    # Build document
    print(f"[PDF] Compiling document with {len(questions)} questions...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Successfully built PDF: {output_path}")

    # Also copy / generate to backend/reports/
    if output_path != OUTPUT_PDF_BACKEND:
        import shutil
        shutil.copyfile(output_path, OUTPUT_PDF_BACKEND)
        print(f"[OK] Copied backup to: {OUTPUT_PDF_BACKEND}")


if __name__ == "__main__":
    build_pdf()
