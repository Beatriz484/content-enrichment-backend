"""Tests del troceado de textos (tests/features/translator.feature)."""
from src.text_splitter import split_text

FRASE = "La investigación científica avanza rápidamente cada año."


def test_trocear_un_texto_corto():
    """Escenario: Trocear un texto corto."""
    texto = "Hola. ¿Qué tal?"

    trozos = split_text(texto, 400)

    assert trozos == [texto]


def test_trocear_un_texto_largo_por_frases():
    """Escenario: Trocear un texto largo por frases."""
    texto = " ".join([FRASE] * 20)

    trozos = split_text(texto, 400)

    assert len(trozos) > 1
    for trozo in trozos:
        assert len(trozo) <= 400
        # Cada trozo termina en punto: ninguna frase queda partida
        assert trozo.endswith(".")
    assert " ".join(trozos) == texto


def test_trocear_una_frase_sola_mas_larga_que_el_limite():
    """Escenario: Trocear una frase sola más larga que el límite."""
    texto = " ".join(["palabra"] * 120) + "."

    trozos = split_text(texto, 400)

    assert len(trozos) > 1
    for trozo in trozos:
        assert len(trozo) <= 400
        # Todas las palabras siguen enteras
        for palabra in trozo.split():
            assert palabra in ("palabra", "palabra.")
    assert " ".join(trozos) == texto


def test_trocear_un_texto_vacio():
    """Escenario: Trocear un texto vacío."""
    assert split_text("", 400) == []
