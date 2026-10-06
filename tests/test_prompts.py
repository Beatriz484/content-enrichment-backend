"""Tests del formulario de opciones de respuesta (capa de diálogo con el usuario)."""
from unittest.mock import patch

from src.options import ContentMode
from src.prompts import (
    confirmar,
    pedir_exportacion,
    pedir_formato,
    pedir_idioma,
    pedir_modo,
    pedir_opciones,
    preguntar_texto,
)


def _con_input(respuestas, funcion, *args, **kwargs):
    with patch("builtins.input", side_effect=respuestas), patch("builtins.print"):
        return funcion(*args, **kwargs)


# --- Primitivas de diálogo ---------------------------------------------------

def test_preguntar_texto_repite_hasta_recibir_valor():
    assert _con_input(["", "   ", "tema final"], preguntar_texto, "➤ Tema: ") == "tema final"


def test_confirmar_acepta_respuestas_validas():
    assert _con_input(["xyz", "no"], confirmar, "¿Continuar?") is False
    assert _con_input(["sí"], confirmar, "¿Continuar?") is True


def test_confirmar_enter_conserva_el_valor_por_defecto():
    assert _con_input([""], confirmar, "¿Continuar?", True) is True
    assert _con_input([""], confirmar, "¿Continuar?", False) is False


def test_pedir_formato_valida_entradas():
    assert _con_input(["docx", "TXT"], pedir_formato) == "txt"


def test_pedir_modo_acepta_1_y_2():
    assert _con_input(["x", "1"], pedir_modo) is ContentMode.ORIGINAL
    assert _con_input(["2"], pedir_modo) is ContentMode.ENRICHED


def test_pedir_idioma_devuelve_none_cuando_se_mantiene_el_original():
    assert _con_input(["EN"], pedir_idioma) == "en"
    assert _con_input([""], pedir_idioma) is None


# --- Formulario completo -----------------------------------------------------

def test_pedir_opciones_recorre_el_formulario_completo():
    opciones = _con_input(
        ["Python", "2", "sí", "fr"],
        pedir_opciones,
    )

    assert opciones.tema == "Python"
    assert opciones.content_mode is ContentMode.ENRICHED
    assert opciones.resumir is True
    assert opciones.idioma == "fr"
    assert opciones.variante.value == "enriched_summary"


def test_pedir_opciones_con_valores_por_defecto():
    opciones = _con_input(["Camas", "1", "", ""], pedir_opciones)

    assert opciones.resumir is False
    assert opciones.idioma is None
    assert opciones.variante.value == "original"


def test_pedir_exportacion_anade_formato_y_nombre():
    opciones_originales = _con_input(["Camas", "1", "", ""], pedir_opciones)

    opciones = _con_input(["pdf", "informe final"], pedir_exportacion, opciones_originales)

    assert opciones.formato == "pdf"
    assert opciones.nombre == "informe final"
    # Las opciones previas no se pierden
    assert opciones.tema == "Camas"
