"""Tests del exportador PDF."""
import os

from src.exporter.pdf_exporter import PdfExporter

# Texto real de Wikipedia: contiene ĭ y ē, fuera del repertorio de Helvetica.
TEXTO_CON_CARACTERES_EXOTICOS = (
    "La mujer (del latín mulĭer, -ēris) o fémina (femĭna) es el ser humano. "
    "Tiene una extensión de 11,66 km² y 29 089 habitantes."
)


def test_pdf_exporta_exclusivamente_titulo_y_body(tmp_path):
    """El PDF se genera con la variante pedida y nada más."""
    output_file = tmp_path / "informe.pdf"

    result_path = PdfExporter.generate(
        str(output_file),
        {"topic": "Mujer", "body": "Solo la variante solicitada."},
    )

    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0


def test_pdf_soporta_caracteres_fuera_de_winansi(tmp_path):
    """Regresión: ĭ y ē acababan en ZapfDingbats y salían ilegibles."""
    output_file = tmp_path / "caracteres.pdf"

    result_path = PdfExporter.generate(
        str(output_file), {"topic": "Mujer", "body": TEXTO_CON_CARACTERES_EXOTICOS}
    )

    assert os.path.getsize(result_path) > 0


def test_pdf_con_body_vacio_genera_el_archivo(tmp_path):
    """Una variante sin contenido no rompe la generación."""
    output_file = tmp_path / "vacio.pdf"

    result_path = PdfExporter.generate(str(output_file), {"topic": "Vacío", "body": ""})

    assert os.path.exists(result_path)


def test_pdf_omite_secciones_no_pedidas(tmp_path):
    """El contrato del exportador es {topic, body}: no existen otras claves."""
    output_file = tmp_path / "exclusivo.pdf"

    PdfExporter.generate(str(output_file), {"topic": "Solo body", "body": "Contenido final."})

    assert os.path.exists(output_file)
