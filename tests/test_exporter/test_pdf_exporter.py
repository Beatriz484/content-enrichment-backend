import os
from src.exporter.pdf_exporter import PdfExporter

def test_pdf_exporter_generate_success(tmp_path):
    """Prueba que ReportLab cree físicamente el archivo PDF sin lanzar excepciones."""
    output_file = tmp_path / "test_report.pdf"
    sample_data = {
        "topic": "ReportLab Test",
        "raw_text": "Texto original para PDF.",
        "enriched_text": "Resumen para PDF.",
        "translated_text": "Translated PDF content."
    }

    result_path = PdfExporter.generate(str(output_file), sample_data)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0