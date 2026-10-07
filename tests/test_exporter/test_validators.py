"""Tests de validación de entradas del exportador."""
from src.exporter.validators import ExportValidator

INFORME = {"topic": "IA", "body": "Contenido final."}


def test_sanitize_filename_valid():
    """Un nombre válido no sufre modificaciones."""
    assert ExportValidator.sanitize_filename("informe_2026") == "informe_2026"


def test_sanitize_filename_invalid_chars():
    """Se eliminan los caracteres prohibidos por el SO."""
    filename_with_bad_chars = "informe/final?2026:v1*<>"
    assert ExportValidator.sanitize_filename(filename_with_bad_chars) == "informefinal2026v1"


def test_sanitize_filename_empty_returns_default():
    """Un nombre vacío o de puros símbolos retorna el nombre por defecto."""
    assert ExportValidator.sanitize_filename("   ") == "informe_investigacion"
    assert ExportValidator.sanitize_filename("???") == "informe_investigacion"


def test_validate_inputs_success():
    """Una entrada correcta con el contrato {topic, body} se aprueba."""
    is_valid, error_msg = ExportValidator.validate_inputs("reporte", "pdf", INFORME)
    assert is_valid is True
    assert error_msg == ""


def test_validate_inputs_empty_filename():
    """Rechazo por nombre vacío."""
    is_valid, error_msg = ExportValidator.validate_inputs("", "txt", INFORME)
    assert is_valid is False
    assert "no puede estar vacío" in error_msg


def test_validate_inputs_unsupported_format():
    """Rechazo por formato no permitido."""
    is_valid, error_msg = ExportValidator.validate_inputs("doc", "docx", INFORME)
    assert is_valid is False
    assert "no permitido" in error_msg


def test_validate_inputs_missing_keys():
    """Rechazo cuando faltan claves obligatorias."""
    is_valid, error_msg = ExportValidator.validate_inputs("reporte", "txt", {"topic": "IA"})
    assert is_valid is False
    assert "Faltan datos obligatorios" in error_msg


def test_validate_inputs_content_no_es_diccionario():
    """El contenido debe llegar como diccionario."""
    is_valid, error_msg = ExportValidator.validate_inputs("reporte", "txt", "texto suelto")
    assert is_valid is False
    assert "diccionario válido" in error_msg
