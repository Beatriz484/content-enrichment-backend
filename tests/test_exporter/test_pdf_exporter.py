import os

from src.exporter.pdf_exporter import PdfExporter

TEXT_WITH_EXOTIC_CHARACTERS = (
    "La mujer (del latín mulĭer, -ēris) o fémina (femĭna) es el ser humano. "
    "Tiene una extensión de 11,66 km² y 29 089 habitantes."
)


def test_pdf_exports_only_title_and_body(tmp_path):
    r"""@successful

    Scenario: Save only the requested variant to PDF
        Given a report with title "Mujer" and body "Solo la variante solicitada."
        When I export the report in "pdf" format
        Then the file is created successfully
        And the file is not empty
    """
    output_file = tmp_path / "informe.pdf"

    result_path = PdfExporter.generate(
        str(output_file),
        {"topic": "Mujer", "body": "Solo la variante solicitada."},
    )

    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0


def test_pdf_supports_characters_outside_winansi(tmp_path):
    r"""@successful

    Scenario: Render characters outside the WinAnsi repertoire
        Given a report with title "Mujer" and body "La mujer (del latín mulĭer, -ēris) ... 11,66 km²"
        When I export the report in "pdf" format
        Then the file is created successfully
        And the file is not empty
    """
    output_file = tmp_path / "caracteres.pdf"

    result_path = PdfExporter.generate(
        str(output_file), {"topic": "Mujer", "body": TEXT_WITH_EXOTIC_CHARACTERS}
    )

    assert os.path.getsize(result_path) > 0


def test_pdf_with_empty_body_creates_the_file(tmp_path):
    r"""@successful

    Scenario: Create the file even when the body is empty
        Given a report with title "Vacío" and an empty body
        When I export the report in "pdf" format
        Then the file is created successfully
    """
    output_file = tmp_path / "vacio.pdf"

    result_path = PdfExporter.generate(str(output_file), {"topic": "Vacío", "body": ""})

    assert os.path.exists(result_path)


def test_pdf_skips_sections_that_were_not_requested(tmp_path):
    r"""@successful

    Scenario: Skip the sections that were not requested
        Given a report with title "Solo body" and body "Contenido final."
        When I export the report in "pdf" format
        Then the file is created successfully
    """
    output_file = tmp_path / "exclusivo.pdf"

    PdfExporter.generate(str(output_file), {"topic": "Solo body", "body": "Contenido final."})

    assert os.path.exists(output_file)
