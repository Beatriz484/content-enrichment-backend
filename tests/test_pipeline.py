"""Tests unitarios del orquestador ContentPipeline (sin red ni IA real)."""
from unittest.mock import MagicMock, patch

from src.pipeline import ContentPipeline


def _pipeline_con_ia():
    enricher = MagicMock()
    enricher.enrich_content.return_value = "Contenido enriquecido por IA"
    enricher.summarize_content.return_value = "Resumen ejecutivo"
    return ContentPipeline(enricher=enricher), enricher


@patch("src.pipeline.WikipediaScraper")
def test_investigar_devuelve_titulo_parrafos_y_texto(mock_scraper):
    """La investigación normaliza la salida del scraper en un único diccionario."""
    mock_scraper.return_value.extraer_contenido.return_value = {
        "titulo": "Python",
        "parrafos": ["Párrafo uno.", "Párrafo dos."],
    }

    resultado = ContentPipeline().investigar("python")

    mock_scraper.assert_called_once_with("python")
    assert resultado["titulo"] == "Python"
    assert resultado["parrafos"] == ["Párrafo uno.", "Párrafo dos."]
    assert resultado["texto"] == "Párrafo uno.\n\nPárrafo dos."


@patch("src.pipeline.WikipediaScraper")
def test_investigar_propaga_el_error_del_scraper(mock_scraper):
    """Los errores del scraper (artículo inexistente) suben hasta la CLI."""
    mock_scraper.return_value.extraer_contenido.side_effect = ValueError("no existe")

    try:
        ContentPipeline().investigar("tema")
    except ValueError:
        pass
    else:
        raise AssertionError("Se esperaba un ValueError")


def test_enriquecer_con_ia_delega_en_el_enricher():
    """Con IA disponible se llama a enrich_content."""
    pipeline, enricher = _pipeline_con_ia()

    assert pipeline.enriquecer("texto base") == "Contenido enriquecido por IA"
    enricher.enrich_content.assert_called_once_with("texto base")


def test_enriquecer_sin_ia_conserva_el_original():
    """Sin API key el flujo no se rompe: devuelve el texto original."""
    pipeline = ContentPipeline(enricher=None)

    assert pipeline.enriquecer("texto base") == "texto base"


def test_resumir_con_ia_delega_en_el_enricher():
    """Con IA disponible se llama a summarize_content."""
    pipeline, enricher = _pipeline_con_ia()

    assert pipeline.resumir("texto largo") == "Resumen ejecutivo"
    enricher.summarize_content.assert_called_once_with("texto largo")


def test_resumir_sin_ia_devuelve_vacio():
    """Sin IA no hay resumen y la sección del informe se omitirá."""
    assert ContentPipeline().resumir("texto largo") == ""


def test_traducir_sin_traductor_devuelve_vacio():
    """Mientras src/translator.py está en desarrollo, la traducción queda vacía."""
    pipeline = ContentPipeline()

    assert pipeline.traducir("texto", "en") == ""


def test_traducir_con_traductor_delega_en_el_modulo():
    """Cuando el compañero entregue su módulo, la pipeline lo usa sin cambios."""
    translator = MagicMock()
    translator.translate.return_value = "Translated text"
    pipeline = ContentPipeline(translator=translator)

    assert pipeline.traducir("texto", "en") == "Translated text"
    translator.translate.assert_called_once_with("texto", "en")


def test_traducir_fallo_de_traductor_no_rompe_el_flujo():
    """Un error del traductor degrada a cadena vacía en lugar de abortar."""
    translator = MagicMock()
    translator.translate.side_effect = RuntimeError("API caída")
    pipeline = ContentPipeline(translator=translator)

    assert pipeline.traducir("texto", "en") == ""


def test_construir_content_data_cumple_el_contrato_del_exportador():
    """El diccionario contiene todas las claves obligatorias del exportador."""
    content_data = ContentPipeline.construir_content_data(
        titulo="Python",
        texto_original="Original",
        texto_enriquecido="Enriquecido",
        texto_traducido="Traducido",
        resumen="Resumen",
    )

    assert content_data == {
        "topic": "Python",
        "raw_text": "Original",
        "enriched_text": "Enriquecido",
        "translated_text": "Traducido",
        "summary": "Resumen",
    }


def test_construir_content_data_sin_resumen_y_sin_traduccion():
    """Sin traductor ni resumen, las claves opcionales vienen vacías."""
    content_data = ContentPipeline.construir_content_data(
        titulo="Python",
        texto_original="Original",
        texto_enriquecido="Enriquecido",
    )

    assert content_data["translated_text"] == ""
    assert content_data["summary"] == ""
