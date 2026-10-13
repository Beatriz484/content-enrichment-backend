"""Tests de la conversión de Markdown a texto plano."""
from src.exporter.plain_text import markdown_to_plain_text


def test_quita_los_simbolos_de_titulo():
    assert markdown_to_plain_text("## Granada") == "Granada"
    assert markdown_to_plain_text("### 1. Geografía") == "1. Geografía"


def test_quita_la_negrita():
    texto = "Se sitúa en la **Vega de Granada** y en __Andalucía__."
    assert markdown_to_plain_text(texto) == "Se sitúa en la Vega de Granada y en Andalucía."


def test_quita_la_cursiva():
    assert markdown_to_plain_text("Una *gran* ciudad") == "Una gran ciudad"


def test_quita_el_simbolo_de_cita():
    assert markdown_to_plain_text("> **Dato técnico:** nieblas") == "Dato técnico: nieblas"


def test_la_linea_separadora_pasa_a_ser_una_linea_en_blanco():
    assert markdown_to_plain_text("Uno\n---\nDos") == "Uno\n\nDos"


def test_las_tablas_pasan_a_una_fila_por_linea():
    tabla = (
        "| Elemento | Descripción |\n"
        "|----------|-------------|\n"
        "| **Altitud** | 680 m |"
    )
    esperado = "Elemento - Descripción\nAltitud - 680 m"
    assert markdown_to_plain_text(tabla) == esperado


def test_los_enlaces_muestran_texto_y_direccion():
    texto = "Mira [la Alhambra](https://alhambra.org) hoy"
    assert markdown_to_plain_text(texto) == "Mira la Alhambra (https://alhambra.org) hoy"


def test_las_listas_con_guion_se_conservan():
    texto = "- **Población:** 235 294\n- Barrios: 7"
    assert markdown_to_plain_text(texto) == "- Población: 235 294\n- Barrios: 7"


def test_las_listas_con_asterisco_pasan_a_guion():
    assert markdown_to_plain_text("* uno\n* dos") == "- uno\n- dos"


def test_un_texto_sin_markdown_no_cambia():
    texto = "Párrafo uno.\n\nPárrafo dos."
    assert markdown_to_plain_text(texto) == texto


def test_no_deja_mas_de_una_linea_en_blanco_seguida():
    assert markdown_to_plain_text("Uno\n\n\n\nDos") == "Uno\n\nDos"

def test_las_referencias_numeradas_quedan_como_numero_entre_corchetes():
        texto = "Superficie: 1 049,05 km² [[1]](#ref1) y otra cifra [[2]](#ref2)"
        assert markdown_to_plain_text(texto) == "Superficie: 1 049,05 km² [1] y otra cifra [2]"