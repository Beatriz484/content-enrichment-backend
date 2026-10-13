import os

from src.exporter.txt_exporter import TxtExporter


def _read_file(path):
    with open(path, "r", encoding="utf-8-sig") as file:
        return file.read()


def test_txt_exports_only_title_and_body(tmp_path):
    r"""@successful

    Scenario: Save only the requested variant to TXT
        Given a report with title "Python Testing" and body "Únicamente la variante solicitada."
        When I export the report in "txt" format
        Then the file is created successfully
        And the file contains the title "Python Testing"
        And the file contains the requested body
        And the file contains no section that was not requested
    """
    output_file = tmp_path / "informe.txt"
    content = {
        "topic": "Python Testing",
        "body": "Únicamente la variante solicitada.",
    }

    result_path = TxtExporter.generate(str(output_file), content)

    text = _read_file(result_path)
    assert "TÍTULO: Python Testing" in text
    assert "Únicamente la variante solicitada." in text
    assert "CONTENIDO ORIGINAL" not in text
    assert "CONTENIDO ENRIQUECIDO" not in text
    assert "CONTENIDO TRADUCIDO" not in text
    assert "Resumen" not in text
    assert "generado exitosamente" not in text


def test_txt_contains_only_the_summary_when_that_is_the_requested_variant(tmp_path):
    r"""@successful

    Scenario: Keep only the summary when that is the variant requested
        Given a report with title "Camas" and body "Resumen ejecutivo de Camas."
        When I export the report in "txt" format
        Then the file contains the requested summary
        And the file does not contain the original Wikipedia text
    """
    output_file = tmp_path / "resumen.txt"

    result_path = TxtExporter.generate(
        str(output_file),
        {"topic": "Camas", "body": "Resumen ejecutivo de Camas."},
    )

    text = _read_file(result_path)
    assert "Resumen ejecutivo de Camas." in text
    assert "municipio y ciudad" not in text


def test_txt_is_utf8_with_bom_so_windows_recognizes_it(tmp_path):
    r"""@successful

    Scenario: Store the TXT in UTF-8 recognised by Windows
        Given a report with title "Título" and body "Contenido"
        When I export the report in "txt" format
        Then the file starts with the UTF-8 byte order mark
        And the file exists on disk
    """
    output_file = tmp_path / "encoding.txt"

    result_path = TxtExporter.generate(str(output_file), {"topic": "Título", "body": "Contenido"})

    with open(result_path, "rb") as file:
        header = file.read(3)

    assert header == b"\xef\xbb\xbf"
    assert os.path.exists(result_path)


def test_txt_preserves_the_body_line_breaks(tmp_path):
    r"""@successful

    Scenario: Preserve the line breaks of the body
        Given a report with title "Tema" and body "Párrafo uno.\n\nPárrafo dos."
        When I export the report in "txt" format
        Then the file keeps the empty line between both paragraphs
    """
    output_file = tmp_path / "saltos.txt"

    result_path = TxtExporter.generate(
        str(output_file), {"topic": "Tema", "body": "Párrafo uno.\n\nPárrafo dos."}
    )

    text = _read_file(result_path)
    assert "Párrafo uno.\n\nPárrafo dos." in text
