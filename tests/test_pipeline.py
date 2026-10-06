"""Tests unitarios del orquestador ContentPipeline (sin red ni IA real)."""
from unittest.mock import MagicMock, patch

import pytest

from src.errors import ServicioNoDisponibleError
from src.options import ContentMode, OutputOptions
from src.pipeline import ContentPipeline

INVESTIGACION = {
    "titulo": "Python",
    "parrafos": ["Párrafo uno.", "Párrafo dos."],
    "texto": "Párrafo uno.\n\nPárrafo dos.",
}


def _pipeline_con_ia():
    enricher = MagicMock()
    enricher.enrich_content.return_value = "Contenido enriquecido por IA"
    enricher.summarize_content.return_value = "Resumen ejecutivo"
    return ContentPipeline(enricher=enricher), enricher


def _pipeline_completa():
    pipeline, enricher = _pipeline_con_ia()
    translator = MagicMock()
    translator.translate.return_value = "Translated text"
    return ContentPipeline(enricher=enricher, translator=translator), enricher, translator


def _opciones(**cambios):
    base = {"tema": "python", "content_mode": ContentMode.ORIGINAL}
    base.update(cambios)
    return OutputOptions(**base)


# --- Investigación ---------------------------------------------------------

@patch("src.pipeline.WikipediaScraper")
def test_investigar_devuelve_titulo_parrafos_y_texto(mock_scraper):
    """La investigación normaliza la salida del scraper en un único diccionario."""
    mock_scraper.return_value.extract_content.return_value = {
        "title": "Python",
        "paragraphs": ["Párrafo uno.", "Párrafo dos."],
    }

    resultado = ContentPipeline().investigar("python")

    mock_scraper.assert_called_once_with("python")
    assert resultado == dict(INVESTIGACION, titulo="Python")


@patch("src.pipeline.WikipediaScraper")
def test_investigar_propaga_el_error_del_scraper(mock_scraper):
    """Los errores del scraper (artículo inexistente) suben hasta la CLI."""
    mock_scraper.return_value.extract_content.side_effect = ValueError("no existe")

    with pytest.raises(ValueError, match="no existe"):
        ContentPipeline().investigar("tema")


# --- Servicios no disponibles ---------------------------------------------

def test_enriquecer_sin_ia_lanza_error_controlado():
    """Sin IA no se devuelve el original haciéndose pasar por enriquecido."""
    with pytest.raises(ServicioNoDisponibleError, match="servicio de IA no está disponible"):
        ContentPipeline(enricher=None).enriquecer("texto base")


def test_resumir_sin_ia_lanza_error_controlado():
    """Sin IA no hay resumen silencioso: el error sube hasta la CLI."""
    with pytest.raises(ServicioNoDisponibleError, match="servicio de IA no está disponible"):
        ContentPipeline(enricher=None).resumir("texto largo")


def test_traducir_sin_traductor_lanza_error_controlado():
    """Mientras src/translator.py no esté integrado, traducir informa del motivo."""
    with pytest.raises(ServicioNoDisponibleError, match="traducción no está disponible"):
        ContentPipeline().traducir("texto", "en")


# --- Delegación en los servicios -------------------------------------------

def test_enriquecer_con_ia_delega_en_el_enricher():
    """Con IA disponible se llama a enrich_content."""
    pipeline, enricher = _pipeline_con_ia()

    assert pipeline.enriquecer("texto base") == "Contenido enriquecido por IA"
    enricher.enrich_content.assert_called_once_with("texto base")


def test_resumir_con_ia_delega_en_el_enricher():
    """Con IA disponible se llama a summarize_content."""
    pipeline, enricher = _pipeline_con_ia()

    assert pipeline.resumir("texto largo") == "Resumen ejecutivo"
    enricher.summarize_content.assert_called_once_with("texto largo")


def test_traducir_con_traductor_delega_en_el_modulo():
    """Cuando el compañero entregue su módulo, la pipeline lo usa sin cambios."""
    pipeline, _, translator = _pipeline_completa()

    assert pipeline.traducir("texto", "en") == "Translated text"
    translator.translate.assert_called_once_with("texto", "en")


def test_traducir_fallo_de_traductor_no_rompe_el_flujo():
    """Un error del traductor sube como excepción controlada, nunca como cadena vacía."""
    pipeline, _, translator = _pipeline_completa()
    translator.translate.side_effect = RuntimeError("API caída")

    with pytest.raises(RuntimeError, match="API caída"):
        pipeline.traducir("texto", "en")


# --- Matriz de control ------------------------------------------------------

def test_procesar_texto_original_sin_transformaciones():
    """Variante 1/2: solo el texto extraído de Wikipedia."""
    pipeline = ContentPipeline()

    resultado = pipeline.procesar(INVESTIGACION, _opciones())

    assert resultado.body == INVESTIGACION["texto"]
    assert resultado.variante == "original"
    assert resultado.informe == {"topic": "Python", "body": INVESTIGACION["texto"]}


def test_procesar_solo_contenido_enriquecido():
    """Variante 3: el cuerpo es el texto ampliado por IA."""
    pipeline, _ = _pipeline_con_ia()
    opciones = _opciones(content_mode=ContentMode.ENRICHED)

    resultado = pipeline.procesar(INVESTIGACION, opciones)

    assert resultado.body == "Contenido enriquecido por IA"
    assert resultado.variante == "enriched"
    assert resultado.enriquecido == "Contenido enriquecido por IA"


def test_procesar_solo_resumen_del_original():
    """Variante 4: el cuerpo es únicamente la síntesis."""
    pipeline, enricher = _pipeline_con_ia()
    opciones = _opciones(resumir=True)

    resultado = pipeline.procesar(INVESTIGACION, opciones)

    assert resultado.body == "Resumen ejecutivo"
    assert resultado.variante == "original_summary"
    # El resumen se calcula sobre el texto del modo elegido, no sobre el enriquecido
    enricher.summarize_content.assert_called_once_with(INVESTIGACION["texto"])


def test_procesar_enriquecido_mas_resumen():
    """Variante 5: enriquecer y después resumir el resultado."""
    pipeline, enricher, _ = _pipeline_completa()
    opciones = _opciones(content_mode=ContentMode.ENRICHED, resumir=True)

    resultado = pipeline.procesar(INVESTIGACION, opciones)

    assert resultado.body == "Resumen ejecutivo"
    assert resultado.variante == "enriched_summary"
    enricher.summarize_content.assert_called_once_with("Contenido enriquecido por IA")


def test_procesar_con_traduccion_sobre_el_resumen():
    """Variante 6: la traducción es el último paso y transforma la variante."""
    pipeline, _, translator = _pipeline_completa()
    opciones = _opciones(content_mode=ContentMode.ENRICHED, resumir=True, idioma="fr")

    resultado = pipeline.procesar(INVESTIGACION, opciones)

    assert resultado.body == "Translated text"
    assert resultado.traducido == "Translated text"
    translator.translate.assert_called_once_with("Resumen ejecutivo", "fr")


def test_procesar_traduce_el_texto_original_cuando_no_se_resume():
    """La traducción se aplica sobre la base, aunque no haya síntesis."""
    pipeline, _, translator = _pipeline_completa()

    resultado = pipeline.procesar(INVESTIGACION, _opciones(idioma="en"))

    assert resultado.body == "Translated text"
    translator.translate.assert_called_once_with(INVESTIGACION["texto"], "en")


def test_procesar_sin_ia_en_modo_enriquecido_aborta():
    """La validación previa debe evitarlo, pero la seguridad no depende de ella."""
    with pytest.raises(ServicioNoDisponibleError):
        ContentPipeline().procesar(
            INVESTIGACION, _opciones(content_mode=ContentMode.ENRICHED)
        )


# --- Contrato del exportador -------------------------------------------------

def test_informe_contiene_exclusivamente_titulo_y_body():
    """El exportador solo recibe título y variante: no puede colar secciones."""
    pipeline, _, translator = _pipeline_completa()
    opciones = _opciones(content_mode=ContentMode.ENRICHED, resumir=True, idioma="fr")

    resultado = pipeline.procesar(INVESTIGACION, opciones)

    assert set(resultado.informe) == {"topic", "body"}
    assert resultado.informe["body"] == "Translated text"


def test_pasos_refleja_los_pasos_realmente_ejecutados():
    """La terminal muestra solo lo que la variante llegó a producir."""
    pipeline, _, translator = _pipeline_completa()
    opciones = _opciones(content_mode=ContentMode.ENRICHED, resumir=True, idioma="fr")

    resultado = pipeline.procesar(INVESTIGACION, opciones)

    assert [rotulo for rotulo, _ in resultado.pasos] == [
        "CONTENIDO ORIGINAL",
        "CONTENIDO ENRIQUECIDO (IA)",
        "RESUMEN (IA)",
        "CONTENIDO TRADUCIDO",
    ]


def test_pasos_solo_muestra_el_original_en_variante_simple():
    """En la variante original no aparecen rótulos de pasos que no ocurrieron."""
    resultado = ContentPipeline().procesar(INVESTIGACION, _opciones())

    assert [rotulo for rotulo, _ in resultado.pasos] == ["CONTENIDO ORIGINAL"]
