from io import BytesIO

from reportlab.graphics.barcode.code128 import Code128
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.models.book import Book
from app.models.label_template import LabelTemplate


def generate_labels_pdf(books: list[Book], template: LabelTemplate) -> bytes:
    buf = BytesIO()
    width = template.width_mm * mm
    height = template.height_mm * mm
    c = canvas.Canvas(buf, pagesize=(width, height))
    font_size = template.font_size
    margin = 2 * mm

    for book in books:
        y = height - margin

        if template.show_dewey and book.dewey_code:
            c.setFont("Helvetica-Bold", font_size + 2)
            c.drawString(margin, y, book.dewey_code)
            y -= (font_size + 4) * 1.2

        if template.show_title:
            c.setFont("Helvetica", font_size)
            title_lines = _wrap_text(book.title, width - 2 * margin, c, font_size)
            for line in title_lines[:3]:
                c.drawString(margin, y, line)
                y -= font_size * 1.2
            if title_lines:
                y -= font_size * 0.3

        if template.show_barcode and book.isbn_13:
            try:
                barcode = Code128(book.isbn_13, barWidth=0.4 * mm, barHeight=8 * mm)
                barcode.drawOn(c, margin, y - 8 * mm)
            except Exception:
                pass

        c.showPage()

    c.save()
    return buf.getvalue()


def _wrap_text(text: str, max_width: float, c: canvas.Canvas, font_size: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if c.stringWidth(candidate, "Helvetica", font_size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines if lines else [text]
