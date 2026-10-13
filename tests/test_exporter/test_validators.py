from src.exporter.validators import ExportValidator

INFORME = {"topic": "IA", "body": "Contenido final."}


def test_sanitize_filename_valid():
    assert ExportValidator.sanitize_filename("informe_2026") == "informe_2026"


def test_sanitize_filename_invalid_chars():
    filename_with_bad_chars = "informe/final?2026:v1*<>"
    assert ExportValidator.sanitize_filename(filename_with_bad_chars) == "informefinal2026v1"


def test_sanitize_filename_empty_returns_default():
    assert ExportValidator.sanitize_filename("   ") == "informe_investigacion"
    assert ExportValidator.sanitize_filename("???") == "informe_investigacion"


def test_validate_inputs_success():
    is_valid, error_msg = ExportValidator.validate_inputs("reporte", "pdf", INFORME)
    assert is_valid is True
    assert error_msg == ""


def test_validate_inputs_empty_filename():
    is_valid, error_msg = ExportValidator.validate_inputs("", "txt", INFORME)
    assert is_valid is False
    assert "no puede estar vacío" in error_msg


def test_validate_inputs_unsupported_format():
    is_valid, error_msg = ExportValidator.validate_inputs("doc", "docx", INFORME)
    assert is_valid is False
    assert "no permitido" in error_msg


def test_validate_inputs_missing_keys():
    is_valid, error_msg = ExportValidator.validate_inputs("reporte", "txt", {"topic": "IA"})
    assert is_valid is False
    assert "Faltan datos obligatorios" in error_msg


def test_validate_inputs_content_no_es_diccionario():
    is_valid, error_msg = ExportValidator.validate_inputs("reporte", "txt", "texto suelto")
    assert is_valid is False
    assert "diccionario válido" in error_msg
