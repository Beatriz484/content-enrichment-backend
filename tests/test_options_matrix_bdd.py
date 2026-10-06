"""Escenarios Gherkin de la matriz de control (sin red ni IA real).

Cubren las 6 variaciones del documento de requisitos y sus rechazos:
se ejecutan con el ``pytest`` ordinario porque no pegan a servicios externos.
"""
from unittest.mock import MagicMock

from pytest_bdd import given, parsers, scenarios, then, when

from src.options import ContentMode, OutputOptions, Variant, validar
from src.pipeline import ContentPipeline

scenarios("features/options_matrix.feature")

TEXTO_ORIGINAL = "Texto extraído de Wikipedia."
ENRIQUECIDO = "Contenido ampliado por IA."
RESUMEN = "Resumen del contenido."
TRADUCIDO = "Contenido traducido al idioma solicitado."


def _pipeline(contexto):
    """Monta la pipeline con los servicios que el contexto declara disponibles."""
    enricher = None
    if contexto["ia_disponible"]:
        enricher = MagicMock()
        enricher.enrich_content.return_value = ENRIQUECIDO
        enricher.summarize_content.return_value = RESUMEN

    translator = None
    if contexto["traductor_disponible"]:
        translator = MagicMock()
        translator.translate.return_value = TRADUCIDO

    return ContentPipeline(enricher=enricher, translator=translator)


# --- Dado --------------------------------------------------------------------

@given(parsers.parse('que investigué el tema "{tema}"'), target_fixture="contexto")
def investigue(tema):
    return {
        "tema": tema,
        "investigacion": {"titulo": tema.strip() or "sin tema", "texto": TEXTO_ORIGINAL},
        "ia_disponible": True,
        "traductor_disponible": False,
        "opciones": None,
        "errores": [],
        "resultado": None,
    }


@given("que no hay credenciales de IA")
def sin_credenciales(contexto):
    contexto["ia_disponible"] = False


@given("que el traductor está disponible")
def traductor_disponible(contexto):
    contexto["traductor_disponible"] = True


# --- Cuando ------------------------------------------------------------------

@when(parsers.parse('elijo modo "{modo}", resumen "{resumen}" e idioma "{idioma}"'))
def elegir_opciones(contexto, modo, resumen, idioma):
    contexto["opciones"] = OutputOptions(
        tema=contexto["tema"],
        content_mode=ContentMode.desde(modo),
        resumir=resumen == "sí",
        idioma=None if idioma == "ninguno" else idioma,
    )


@when("valido las opciones seleccionadas")
def validar_opciones(contexto):
    contexto["errores"] = validar(
        contexto["opciones"],
        ia_disponible=contexto["ia_disponible"],
        traductor_disponible=contexto["traductor_disponible"],
    )


@when("aplico la matriz de control")
def aplicar_matriz(contexto):
    if not contexto["errores"]:
        contexto["resultado"] = _pipeline(contexto).procesar(
            contexto["investigacion"], contexto["opciones"]
        )


# --- Entonces -----------------------------------------------------------------

@then(parsers.parse('la variante resuelta es "{variante}"'))
def variante_resuelta(contexto, variante):
    """La comparación se hace sobre el rótulo legible, no sobre el código crudo."""
    resuelta = Variant(contexto["resultado"].variante)
    assert resuelta.titulo == variante


@then(parsers.parse('el cuerpo del informe es "{esperado}"'))
def cuerpo_esperado(contexto, esperado):
    assert contexto["resultado"].body == esperado
    assert contexto["resultado"].informe["body"] == esperado


@then(parsers.parse('el informe no contiene "{texto}"'))
def informe_no_contiene(contexto, texto):
    assert texto not in contexto["resultado"].body


@then(parsers.parse('el sistema informa que "{mensaje}"'))
def sistema_informa(contexto, mensaje):
    assert any(mensaje in error for error in contexto["errores"]), contexto["errores"]


@then("no se genera ningún informe")
def no_se_genera_informe(contexto):
    assert contexto["errores"], "La validación debió rechazar las opciones"
    assert contexto["resultado"] is None
