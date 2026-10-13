from src.text_splitter import split_text

FRASE = "La investigación científica avanza rápidamente cada año."


def test_trocear_un_texto_corto():
    texto = "Hola. ¿Qué tal?"

    trozos = split_text(texto, 400)

    assert trozos == [texto]


def test_trocear_un_texto_largo_por_frases():
    texto = " ".join([FRASE] * 20)

    trozos = split_text(texto, 400)

    assert len(trozos) > 1
    for trozo in trozos:
        assert len(trozo) <= 400
        assert trozo.endswith(".")
    assert " ".join(trozos) == texto


def test_trocear_una_frase_sola_mas_larga_que_el_limite():
    texto = " ".join(["palabra"] * 120) + "."

    trozos = split_text(texto, 400)

    assert len(trozos) > 1
    for trozo in trozos:
        assert len(trozo) <= 400
        for palabra in trozo.split():
            assert palabra in ("palabra", "palabra.")
    assert " ".join(trozos) == texto


def test_trocear_un_texto_vacio():
    assert split_text("", 400) == []
