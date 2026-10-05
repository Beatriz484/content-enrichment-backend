import pytest
from src.exporter.validators import ExportValidator

def test_sanitize_filename_valid():
    """Prueba que un nombre válido no sufra modificaciones."""
    assert ExportValidator.sanitize_filename("informe_2026") == "informe_2026"

def test_sanitize_filename_invalid_chars():
    """Prueba que se eliminen los caracteres prohibidos por el SO."""
    filename_with_bad_chars = "informe/final?2026:v1*<>"
    sanitized = ExportValidator.sanitize_filename(filename_with_bad_chars)
    assert sanitized == "informefinal2026v1"

def test_sanitize_filename_empty_returns_default():
    """Prueba que un nombre vacío o de puros símbolos retorne el nombre por defecto."""
    assert ExportValidator.sanitize_filename("   ") == "informe_investigacion"
    assert ExportValidator.sanitize_filename("???") == "informe_investigacion"

def test_validate_inputs_success():
    """Prueba que el validador apruebe una entrada completamente correcta."""
    sample_data = {
        "topic": "IA",
        "raw_text": "Texto",
        "enriched_text": "Resumen",
        "translated_text": "Summary"
    }
    is_valid, error_msg = ExportValidator.validate_inputs("reporte", "pdf", sample_data)
    assert is_valid is True
    assert error_msg == ""

def test_validate_inputs_empty_filename():
    """Prueba rechazo por nombre vacío."""
    is_valid, error_msg = ExportValidator.validate_inputs("", "txt", {})
    assert is_valid is False
    assert "no puede estar vacío" in error_msg

def test_validate_inputs_unsupported_format():
    """Prueba rechazo por formato no permitido."""
    sample_data = {"topic": "A", "raw_text": "B", "enriched_text": "C", "translated_text": "D"}
    is_valid, error_msg = ExportValidator.validate_inputs("doc", "docx", sample_data)
    assert is_valid is False
    assert "no permitido" in error_msg

def test_validate_inputs_missing_keys():
    """Prueba rechazo cuando faltan claves obligatorias en el diccionario."""
    incomplete_data = {"topic": "IA"}  # Faltan las demás claves
    is_valid, error_msg = ExportValidator.validate_inputs("reporte", "txt", incomplete_data)
    assert is_valid is False
    assert "Faltan datos obligatorios" in error_msg