from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from .titles import NOTA_TRADUCCION_PENDIENTE, hay_traduccion, titulos_del_informe


class PdfExporter:
    @staticmethod
    def generate(file_path: str, content_data: Dict[str, Any]) -> str:
        document = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
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
        titulos = titulos_del_informe(content_data)

        # Título principal
        topic = content_data.get('topic')
        story.append(Paragraph(f"<b>Informe de Investigación:</b> {topic}", title_style))
        story.append(Spacer(1, 10))

        # Sección 1: Contenido Original
        story.append(Paragraph(titulos["original"], section_style))
        raw_text = str(content_data.get('raw_text', '')).replace('\n', '<br/>')
        story.append(Paragraph(raw_text, body_style))

        # Sección 2: IA (el rótulo refleja si la IA llegó a actuar)
        story.append(Paragraph(titulos["enriquecimiento"], section_style))
        enriched_text = str(content_data.get('enriched_text', '')).replace('\n', '<br/>')
        story.append(Paragraph(enriched_text, body_style))

        # Sección 3: Traducción (con aviso si el módulo sigue pendiente)
        story.append(Paragraph(titulos["traduccion"], section_style))
        if hay_traduccion(content_data):
            translated_text = str(content_data.get('translated_text', '')).replace('\n', '<br/>')
            story.append(Paragraph(translated_text, body_style))
        else:
            story.append(Paragraph(NOTA_TRADUCCION_PENDIENTE, body_style))

        # Sección 4: Resumen ejecutivo (solo si la IA lo generó)
        summary = str(content_data.get('summary') or '').strip()
        if summary:
            story.append(Paragraph(titulos["resumen"], section_style))
            story.append(Paragraph(summary.replace('\n', '<br/>'), body_style))

        document.build(story)
        return file_path