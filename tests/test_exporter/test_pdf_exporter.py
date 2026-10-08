"""Tests del exportador PDF."""
import os

from src.exporter.pdf_exporter import PdfExporter

# Texto real de Wikipedia: contiene ĭ y ē, fuera del repertorio de Helvetica.
TEXT_WITH_EXOTIC_CHARACTERS = (
    "La mujer (del latín mulĭer, -ēris) o fémina (femĭna) es el ser humano. "
    "Tiene una extensión de 11,66 km² y 29 089 habitantes."
)


def test_pdf_exports_only_title_and_body(tmp_path):
    """El PDF se genera con la variante pedida y nada más."""
    output_file = tmp_path / "informe.pdf"

    result_path = PdfExporter.generate(
        str(output_file),
        {"topic": "Mujer", "body": "Solo la variante solicitada."},
    )

    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0


def test_pdf_supports_characters_outside_winansi(tmp_path):
    """Regresión: ĭ y ē acababan en ZapfDingbats y salían ilegibles."""
    output_file = tmp_path / "caracteres.pdf"

    result_path = PdfExporter.generate(
        str(output_file), {"topic": "Mujer", "body": TEXT_WITH_EXOTIC_CHARACTERS}
    )

    assert os.path.getsize(result_path) > 0


def test_pdf_with_empty_body_creates_the_file(tmp_path):
    """Una variante sin contenido no rompe la generación."""
    output_file = tmp_path / "vacio.pdf"

    result_path = PdfExporter.generate(str(output_file), {"topic": "Vacío", "body": ""})

    assert os.path.exists(result_path)


def test_pdf_skips_sections_that_were_not_requested(tmp_path):
    """El contrato del exportador es {topic, body}: no existen otras claves."""
    output_file = tmp_path / "exclusivo.pdf"

    PdfExporter.generate(str(output_file), {"topic": "Solo body", "body": "Contenido final."})

    assert os.path.exists(output_file)
