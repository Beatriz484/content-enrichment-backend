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


def test_pdf_exporter_sin_ia_genera_archivo(tmp_path):
    """El PDF también se genera cuando la IA no actuó (título honesto)."""
    output_file = tmp_path / "test_report_no_ai.pdf"
    texto_original = "Texto original sin tocar."
    sample_data = {
        "topic": "Sin IA",
        "raw_text": texto_original,
        "enriched_text": texto_original,
        "translated_text": "",
    }

    result_path = PdfExporter.generate(str(output_file), sample_data)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0


def test_pdf_exporter_con_resumen_genera_archivo(tmp_path):
    """El PDF se genera correctamente cuando existe la sección 4 (resumen)."""
    output_file = tmp_path / "test_report_summary.pdf"
    sample_data = {
        "topic": "ReportLab Test",
        "raw_text": "Texto original para PDF.",
        "enriched_text": "Resumen para PDF.",
        "translated_text": "Translated PDF content.",
        "summary": "Resumen ejecutivo generado por IA.",
    }

    result_path = PdfExporter.generate(str(output_file), sample_data)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0


def test_pdf_exporter_sin_resumen_genera_archivo(tmp_path):
    """El PDF también se genera sin resumen (la sección 4 se omite)."""
    output_file = tmp_path / "test_report_no_summary.pdf"
    sample_data = {
        "topic": "ReportLab Test",
        "raw_text": "Texto original para PDF.",
        "enriched_text": "Resumen para PDF.",
        "translated_text": "Translated PDF content.",
        "summary": "",
    }

    result_path = PdfExporter.generate(str(output_file), sample_data)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0