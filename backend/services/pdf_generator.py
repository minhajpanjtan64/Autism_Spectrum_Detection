from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_pdf_report(report_data: dict, output_path: str) -> str:
    """Generate a simple PDF report and return its file path."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    pdf = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    pdf.setTitle("Autism Screening Report")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, height - 50, "AI-Based Autism Screening & Early Detection Report")

    pdf.setFont("Helvetica", 11)
    y = height - 90
    for key, value in report_data.items():
        pdf.drawString(40, y, f"{key}: {value}")
        y -= 18
        if y < 60:
            pdf.showPage()
            pdf.setFont("Helvetica", 11)
            y = height - 50

    pdf.save()
    return str(path)
