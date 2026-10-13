import pytest

from src.translation.language_validator import (
    ask_language,
    is_valid_language,
    validate_language,
)
from src.translation.translation_errors import InvalidLanguageError


def entrada_simulada(respuestas):
    pendientes = list(respuestas)

    def leer(mensaje):
        return pendientes.pop(0)

    return leer


@pytest.mark.parametrize(
    "entrada, codigo",
    [
        ("español", "es-ES"),
        ("espanol", "es-ES"),
        ("  INGLÉS  ", "en-GB"),
        ("french", "fr-FR"),
        ("de-DE", "de-DE"),
    ],
    ids=[
        "nombre en espanol",
        "nombre en espanol sin tilde",
        "mayusculas y espacios",
        "nombre en ingles",
        "codigo de MyMemory",
    ],
)
def test_escribir_un_idioma_valido(entrada, codigo):
    assert is_valid_language(entrada) is True
    assert validate_language(entrada) == codigo


@pytest.mark.parametrize(
    "entrada, mensaje",
    [
        ("espanil", "no existe o está mal escrito"),
        ("3spañol", "contiene números"),
        ("123", "contiene números"),
        ("", "No has escrito ningún idioma"),
        ("mesa", "no existe o está mal escrito"),
    ],
    ids=[
        "una letra mal",
        "numero colado",
        "solo numeros",
        "vacio",
        "texto que no es un idioma",
    ],
)
def test_escribir_un_idioma_con_errores(entrada, mensaje):
    assert is_valid_language(entrada) is False
    with pytest.raises(InvalidLanguageError, match=mensaje):
        validate_language(entrada)


def test_recibir_el_idioma_vacio_desde_el_formulario():
    with pytest.raises(InvalidLanguageError, match="No has escrito ningún idioma"):
        validate_language(None)


def test_un_intento_fallido_y_despues_uno_correcto(capsys):
    codigo = ask_language(input_func=entrada_simulada(["espanil", "francés"]))

    assert "no existe o está mal escrito" in capsys.readouterr().out
    assert codigo == "fr-FR"


def test_agotar_los_intentos():
    with pytest.raises(InvalidLanguageError, match="Has agotado los 3 intentos"):
        ask_language(input_func=entrada_simulada(["3spañol", "123", ""]), max_attempts=3)

@pytest.mark.parametrize("entrada, esperado", [
    ("en", "en-GB"),
    ("fr", "fr-FR"),
    ("EN ", "en-GB"),
    ("Fr", "fr-FR"),
    ("pt", "pt-PT"),
])
def test_codigo_corto_se_convierte_al_codigo_de_mymemory(entrada, esperado):
    assert validate_language(entrada) == esperado


def test_codigo_corto_inexistente_da_error():
    with pytest.raises(InvalidLanguageError):
        validate_language("xx")