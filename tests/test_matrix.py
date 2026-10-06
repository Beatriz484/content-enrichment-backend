"""Matriz de control: las 8 combinaciones de la salida (eje A × eje B × traducción).

Cada caso verifica que ``informe["body"]`` sea **exactamente** la variante
pedida, sin colar el texto original ni ninguna nota adicional.
"""
from unittest.mock import MagicMock

import pytest

from src.options import ContentMode, OutputOptions
from src.pipeline import ContentPipeline

ORIGINAL = "TEXTO ORIGINAL DE WIKIPEDIA"
ENRIQUECIDO = "TEXTO ENRIQUECIDO POR IA"
RESUMEN = "RESUMEN SINTETICO"
TRADUCIDO = "TEXTO TRADUCIDO"

INVESTIGACION = {"titulo": "Python", "parrafos": [ORIGINAL], "texto": ORIGINAL}


def _pipeline():
    enricher = MagicMock()
    enricher.enrich_content.return_value = ENRIQUECIDO
    enricher.summarize_content.return_value = RESUMEN
    translator = MagicMock()
    translator.translate.return_value = TRADUCIDO
    return ContentPipeline(enricher=enricher, translator=translator), enricher, translator


CASOS = [
    # (id, modo, resumen, idioma, body esperado, argumento de resumir, argumento de traducir)
    ("original", ContentMode.ORIGINAL, False, None, ORIGINAL, None, None),
    ("original_traducido", ContentMode.ORIGINAL, False, "en", TRADUCIDO, None, ORIGINAL),
    ("resumen", ContentMode.ORIGINAL, True, None, RESUMEN, ORIGINAL, None),
    ("resumen_traducido", ContentMode.ORIGINAL, True, "en", TRADUCIDO, ORIGINAL, RESUMEN),
    ("enriquecido", ContentMode.ENRICHED, False, None, ENRIQUECIDO, None, None),
    ("enriquecido_traducido", ContentMode.ENRICHED, False, "en", TRADUCIDO, None, ENRIQUECIDO),
    ("enriquecido_resumen", ContentMode.ENRICHED, True, None, RESUMEN, ENRIQUECIDO, None),
    (
        "enriquecido_resumen_traducido",
        ContentMode.ENRICHED,
        True,
        "fr",
        TRADUCIDO,
        ENRIQUECIDO,
        RESUMEN,
    ),
]


@pytest.mark.parametrize(
    "modo,resumir,idioma,esperado,origen_resumen,origen_traduccion",
    [caso[1:] for caso in CASOS],
    ids=[caso[0] for caso in CASOS],
)
def test_variante_produce_un_body_exclusivo(
    modo, resumir, idioma, esperado, origen_resumen, origen_traduccion
):
    """El informe contiene solo la variante pedida, en el orden correcto."""
    pipeline, enricher, translator = _pipeline()
    opciones = OutputOptions(tema="python", content_mode=modo, resumir=resumir, idioma=idioma)

    resultado = pipeline.procesar(INVESTIGACION, opciones)

    assert resultado.informe == {"topic": "Python", "body": esperado}
    assert set(resultado.informe) == {"topic", "body"}

    if origen_resumen is None:
        enricher.summarize_content.assert_not_called()
    else:
        enricher.summarize_content.assert_called_once_with(origen_resumen)

    if origen_traduccion is None:
        translator.translate.assert_not_called()
    else:
        translator.translate.assert_called_once_with(origen_traduccion, idioma)


@pytest.mark.parametrize(
    "modo,resumir,idioma",
    [caso[1:4] for caso in CASOS],
    ids=[caso[0] for caso in CASOS],
)
def test_variante_sin_original_cuando_no_se_pidio(modo, resumir, idioma):
    """La regla de exportación: si no se pidió el original, no aparece."""
    pipeline, _, _ = _pipeline()
    opciones = OutputOptions(tema="python", content_mode=modo, resumir=resumir, idioma=idioma)

    body = pipeline.procesar(INVESTIGACION, opciones).body

    pidio_original = modo is ContentMode.ORIGINAL and not resumir and idioma is None
    if pidio_original:
        assert ORIGINAL in body
    else:
        assert ORIGINAL not in body
        assert "WIKIPEDIA" not in body
