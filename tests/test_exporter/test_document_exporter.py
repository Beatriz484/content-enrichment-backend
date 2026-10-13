import os

from src.exporter.document_exporter import DocumentExporter

REPORT = {"topic": "Integración", "body": "Contenido de la variante pedida."}


def test_document_exporter_initialization(tmp_path):
    r"""@successful

    Scenario: Create the output directory on initialisation
        Given an output directory that does not exist yet
        When I create the document exporter
        Then the output directory exists on disk
    """
    target_dir = tmp_path / "new_output_dir"
    DocumentExporter(output_dir=str(target_dir))
    assert os.path.exists(target_dir)


def test_export_content_txt_success(tmp_path):
    r"""@successful

    Scenario: Export a report to TXT
        Given a report with title "Integración" and a body
        When I export it with the file name "informe_test" in "txt" format
        Then the export succeeds
        And the returned path ends with "informe_test.txt"
        And the file exists on disk
    """
    exporter = DocumentExporter(output_dir=str(tmp_path))

    is_success, file_path = exporter.export_content("informe_test", "txt", REPORT)

    assert is_success is True
    assert file_path.endswith("informe_test.txt")
    assert os.path.exists(file_path)


def test_export_content_pdf_success(tmp_path):
    r"""@successful

    Scenario: Export a report to PDF
        Given a report with title "Integración" and a body
        When I export it with the file name "informe_test" in "pdf" format
        Then the export succeeds
        And the returned path ends with "informe_test.pdf"
        And the file exists on disk
    """
    exporter = DocumentExporter(output_dir=str(tmp_path))

    is_success, file_path = exporter.export_content("informe_test", "pdf", REPORT)

    assert is_success is True
    assert file_path.endswith("informe_test.pdf")
    assert os.path.exists(file_path)


def test_export_content_does_not_duplicate_the_extension(tmp_path):
    r"""@successful

    Scenario: Keep an extension the user already typed
        Given a report with title "Integración" and a body
        When I export it with the file name "informe.txt" in "txt" format
        Then the export succeeds
        And the returned path ends with "informe.txt"
    """
    exporter = DocumentExporter(output_dir=str(tmp_path))

    is_success, file_path = exporter.export_content("informe.txt", "txt", REPORT)

    assert is_success is True
    assert file_path.endswith(os.path.join("informe.txt"))


def test_export_content_validation_failure(tmp_path):
    r"""@failure

    Scenario: Report a rejected export without leaving a file behind
        Given an empty report
        When I export it with the file name "informe_fallido" in "doc" format
        Then the export fails
        And the error message reports a validation error
        And no file is created
    """
    exporter = DocumentExporter(output_dir=str(tmp_path))

    is_success, error_msg = exporter.export_content("informe_fallido", "doc", {})

    assert is_success is False
    assert "Error de Validación" in error_msg
    assert os.listdir(tmp_path) == []


def _permission_denied(*args, **kwargs):
    raise PermissionError()


def _disk_full(*args, **kwargs):
    raise RuntimeError("disco lleno")


def test_export_content_reports_insufficient_permissions(tmp_path, monkeypatch):
    r"""@failure

    Scenario: Report a file the process is not allowed to write
        Given a report with title "Integración" and a body
        And a TXT writer that raises a permission error
        When I export it with the file name "bloqueado" in "txt" format
        Then the export fails
        And the error message reports insufficient permissions
    """
    from src.exporter import document_exporter

    monkeypatch.setattr(document_exporter.TxtExporter, "generate", _permission_denied)

    is_success, error_msg = DocumentExporter(output_dir=str(tmp_path)).export_content(
        "bloqueado", "txt", REPORT
    )

    assert is_success is False
    assert "Permisos insuficientes" in error_msg


def test_export_content_reports_an_unexpected_error(tmp_path, monkeypatch):
    r"""@failure

    Scenario: Report an unexpected writer failure
        Given a report with title "Integración" and a body
        And a TXT writer that raises an unexpected error
        When I export it with the file name "fallo" in "txt" format
        Then the export fails
        And the error message contains the original reason
    """
    from src.exporter import document_exporter

    monkeypatch.setattr(document_exporter.TxtExporter, "generate", _disk_full)

    is_success, error_msg = DocumentExporter(output_dir=str(tmp_path)).export_content(
        "fallo", "txt", REPORT
    )

    assert is_success is False
    assert "disco lleno" in error_msg
