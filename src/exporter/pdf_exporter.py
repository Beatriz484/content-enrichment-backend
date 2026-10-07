<<<<<<< HEAD
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
=======
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
>>>>>>> dev


class PdfExporter:
    @staticmethod
    def generate(file_path: str, content_data: Dict[str, Any]) -> str:
<<<<<<< HEAD
        document = SimpleDocTemplate(
=======
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
>>>>>>> dev
            file_path,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
<<<<<<< HEAD
            bottomMargin=0.75 * inch
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'PdfTitle',
            parent=styles['Heading1'],
            fontSize=16,
            leading=20,
            spaceAfter=12
        )

        section_style = ParagraphStyle(
            'PdfSectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            spaceBefore=10,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'PdfBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            spaceAfter=10
        )

        story = []

        # Título principal
        topic = content_data.get('topic')
        story.append(Paragraph(f"<b>Informe de Investigación:</b> {topic}", title_style))
        story.append(Spacer(1, 10))

        # Sección 1: Contenido Original
        story.append(Paragraph("1. Contenido Original (Extraído)", section_style))
        raw_text = str(content_data.get('raw_text', '')).replace('\n', '<br/>')
        story.append(Paragraph(raw_text, body_style))

        # Sección 2: IA
        story.append(Paragraph("2. Contenido Enriquecido y Resumido (IA)", section_style))
        enriched_text = str(content_data.get('enriched_text', '')).replace('\n', '<br/>')
        story.append(Paragraph(enriched_text, body_style))

        # Sección 3: Traducción
        story.append(Paragraph("3. Contenido Traducido", section_style))
        translated_text = str(content_data.get('translated_text', '')).replace('\n', '<br/>')
        story.append(Paragraph(translated_text, body_style))

        document.build(story)
        return file_path
=======
            bottomMargin=0.75 * inch,
        ).build(story)

        return file_path
>>>>>>> dev
