import os
import pytest
from src.exporter.document_exporter import DocumentExporter


def test_document_exporter_initialization(tmp_path):
    """Prueba que se cree el directorio de salida si no existe."""
    target_dir = tmp_path / "new_output_dir"
    exporter = DocumentExporter(output_dir=str(target_dir))
    assert os.path.exists(target_dir)


def test_export_content_txt_success(tmp_path):
    """Prueba flujo completo exitoso para TXT."""
    exporter = DocumentExporter(output_dir=str(tmp_path))
    sample_data = {
        "topic": "Integración",
        "raw_text": "Original",
        "enriched_text": "Enriquecido",
        "translated_text": "Traducido"
    }

    is_success, file_path = exporter.export_content("informe_test", "txt", sample_data)
    assert is_success is True
    assert file_path.endswith("informe_test.txt")
    assert os.path.exists(file_path)


def test_export_content_pdf_success(tmp_path):
    """Prueba flujo completo exitoso para PDF."""
    exporter = DocumentExporter(output_dir=str(tmp_path))
    sample_data = {
        "topic": "Integración PDF",
        "raw_text": "Original PDF",
        "enriched_text": "Enriquecido PDF",
        "translated_text": "Traducido PDF"
    }

    is_success, file_path = exporter.export_content("informe_test", "pdf", sample_data)
    assert is_success is True
    assert file_path.endswith("informe_test.pdf")
    assert os.path.exists(file_path)


def test_export_content_validation_failure(tmp_path):
    """Prueba que no se cree ningún archivo si falla la validación temprana."""
    exporter = DocumentExporter(output_dir=str(tmp_path))

    # Intento con formato inválido
    is_success, error_msg = exporter.export_content("informe_fallido", "doc", {})
    assert is_success is False
    assert "Error de Validación" in error_msg