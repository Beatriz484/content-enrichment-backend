"""Tests de los rótulos coherentes de las secciones del informe."""
from src.exporter.titles import (
    NOTA_TRADUCCION_PENDIENTE,
    hay_traduccion,
    ia_actuo,
    titulos_del_informe,
)

CON_IA = {
    "raw_text": "Texto original.",
    "enriched_text": "Texto ampliado por la IA.",
    "translated_text": "Translated content.",
}


def test_titulo_de_enriquecimiento_cuando_la_ia_actuo():
    """Si la IA enriqueció, la sección 2 se llama 'Contenido Enriquecido (IA)'."""
    titulos = titulos_del_informe(CON_IA)

    assert titulos["enriquecimiento"] == "2. Contenido Enriquecido (IA)"
    assert ia_actuo(CON_IA) is True


def test_titulo_de_enriquecimiento_sin_ia():
    """Si la IA no actuó (texto idéntico al original), el título lo reconoce."""
    sin_ia = dict(CON_IA, enriched_text=CON_IA["raw_text"])
    titulos = titulos_del_informe(sin_ia)

    assert titulos["enriquecimiento"] == "2. Contenido Sin Enriquecer (IA no disponible)"
    assert ia_actuo(sin_ia) is False


def test_bandera_explicita_manda_sobre_la_comparacion():
    """La bandera 'enriched_with_ai' tiene prioridad sobre comparar textos."""
    contenido = dict(CON_IA, enriched_with_ai=False)

    assert ia_actuo(contenido) is False


def test_titulo_de_traduccion_cuando_hay_contenido():
    """Con texto traducido, la sección 3 no lleva ningún aviso."""
    titulos = titulos_del_informe(CON_IA)

    assert titulos["traduccion"] == "3. Contenido Traducido"
    assert hay_traduccion(CON_IA) is True


def test_titulo_de_traduccion_pendiente_si_no_hay_texto():
    """Sin traductor integrado, la sección 3 indica que está pendiente."""
    sin_traduccion = dict(CON_IA, translated_text="")
    titulos = titulos_del_informe(sin_traduccion)

    assert titulos["traduccion"] == "3. Contenido Traducido (pendiente)"
    assert hay_traduccion(sin_traduccion) is False


def test_nota_de_traduccion_pendiente():
    """La nota explica por qué la sección 3 está vacía."""
    assert "traducción" in NOTA_TRADUCCION_PENDIENTE
    assert "no está disponible" in NOTA_TRADUCCION_PENDIENTE


def test_titulos_de_original_y_resumen():
    """Las secciones 1 y 4 mantienen su redacción."""
    titulos = titulos_del_informe(CON_IA)

    assert titulos["original"] == "1. Contenido Original (Extraído)"
    assert titulos["resumen"] == "4. Resumen Ejecutivo (IA)"
