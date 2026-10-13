r"""Feature: Validation of the data handed to the exporter

  As a Content Enricher user
  I want an export rejected with a clear message when something is missing or not allowed
  So that no half-written file is ever left on disk
"""

from src.exporter.validators import ExportValidator

REPORT = {"topic": "IA", "body": "Contenido final."}


def test_sanitize_filename_valid():
    r"""@successful

    Scenario: Keep a valid file name unchanged
        Given the file name "informe_2026"
        When I sanitise the file name
        Then I get the file name "informe_2026"
    """
    assert ExportValidator.sanitize_filename("informe_2026") == "informe_2026"


def test_sanitize_filename_invalid_chars():
    r"""@successful

    Scenario: Drop the characters a file name cannot contain
        Given the file name "informe/final?2026:v1*<>"
        When I sanitise the file name
        Then I get the file name "informefinal2026v1"
    """
    filename_with_bad_chars = "informe/final?2026:v1*<>"
    assert ExportValidator.sanitize_filename(filename_with_bad_chars) == "informefinal2026v1"


def test_sanitize_filename_empty_returns_default():
    r"""@successful

    Scenario: Fall back to the default name when nothing usable is left
        Given the file names "   " and "???"
        When I sanitise both file names
        Then I get the file name "informe_investigacion" for each of them
    """
    assert ExportValidator.sanitize_filename("   ") == "informe_investigacion"
    assert ExportValidator.sanitize_filename("???") == "informe_investigacion"


def test_validate_inputs_success():
    r"""@successful

    Scenario: Accept a complete report in a supported format
        Given a report titled "IA" with a body
        When I validate the file name "reporte" and the format "pdf"
        Then the validation succeeds
        And the validation returns no error message
    """
    is_valid, error_msg = ExportValidator.validate_inputs("reporte", "pdf", REPORT)
    assert is_valid is True
    assert error_msg == ""


def test_validate_inputs_empty_filename():
    r"""@failure

    Scenario: Reject an empty file name
        Given a report titled "IA" with a body
        When I validate the file name "" and the format "txt"
        Then the validation fails
        And the error message says that the file name cannot be empty
    """
    is_valid, error_msg = ExportValidator.validate_inputs("", "txt", REPORT)
    assert is_valid is False
    assert "no puede estar vacío" in error_msg


def test_validate_inputs_unsupported_format():
    r"""@failure

    Scenario: Reject a format that is not supported
        Given a report titled "IA" with a body
        When I validate the file name "doc" and the format "docx"
        Then the validation fails
        And the error message says that the format is not allowed
    """
    is_valid, error_msg = ExportValidator.validate_inputs("doc", "docx", REPORT)
    assert is_valid is False
    assert "no permitido" in error_msg


def test_validate_inputs_missing_keys():
    r"""@failure

    Scenario: Reject a report that has no body
        Given a report titled "IA" without a body
        When I validate the file name "reporte" and the format "txt"
        Then the validation fails
        And the error message says that mandatory data is missing
    """
    is_valid, error_msg = ExportValidator.validate_inputs("reporte", "txt", {"topic": "IA"})
    assert is_valid is False
    assert "Faltan datos obligatorios" in error_msg


def test_validate_inputs_content_is_not_a_dictionary():
    r"""@failure

    Scenario: Reject content that is not a dictionary
        Given a report whose content is the plain string "texto suelto"
        When I validate the file name "reporte" and the format "txt"
        Then the validation fails
        And the error message says that the content is not a valid dictionary
    """
    is_valid, error_msg = ExportValidator.validate_inputs("reporte", "txt", "texto suelto")
    assert is_valid is False
    assert "diccionario válido" in error_msg
