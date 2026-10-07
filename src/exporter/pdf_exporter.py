"""Generación del archivo PDF con la variante exacta solicitada.

El texto pasa por ``pdf_fonts.prepare_text`` para que los caracteres fuera de
Helvetica no salgan corruptos y para que las secuencias ``<...>`` del texto de
Wikipedia no se interpreten como etiquetas de marcado.
"""
from typing import Any, Dict

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from .pdf_fonts import prepare_text, unicode_font

SEPARATOR = "=" * 60


def _build_styles(font: str):
    """Construye los estilos del informe sobre la fuente resuelta."""
    base = getSampleStyleSheet()
    return (
        ParagraphStyle(
            "PdfTitle",
            parent=base["Heading1"],
            fontName=font,
            bulletFontName=font,
            fontSize=16,
            leading=20,
            spaceAfter=12,
        ),
        ParagraphStyle(
            "PdfBody",
            parent=base["Normal"],
            fontName=font,
            bulletFontName=font,
            fontSize=10,
            leading=14,
            spaceAfter=10,
        ),
    )


class PdfExporter:
    @staticmethod
    def generate(file_path: str, content_data: Dict[str, Any]) -> str:
        """Escribe título y cuerpo de la variante pedida. Nada más."""
        font = unicode_font() or "Helvetica"
        title_style, body_style = _build_styles(font)

        story = [
            Paragraph(prepare_text(f"{SEPARATOR}"), body_style),
            Paragraph(prepare_text(f"TÍTULO: {content_data['topic']}"), title_style),
            Paragraph(prepare_text(f"{SEPARATOR}"), body_style),
            Spacer(1, 12),
            Paragraph(prepare_text(str(content_data["body"])), body_style),
        ]

        SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        ).build(story)

        return file_path
