from unittest.mock import patch

import pytest
import requests
from deep_translator.exceptions import NotValidLength, TooManyRequests

from src.text_splitter import split_text
from src.translation_errors import (
    EmptyTextError,
    InvalidLanguageError,
    NoConnectionError,
    RateLimitError,
    TextTooLongError,
    TranslationTimeoutError,
)
from src.translator import DeepTranslateTranslator


@pytest.fixture
def service():
    return DeepTranslateTranslator(email="")


def traduccion_falsa(texto, codigo):
    return texto.upper()


def test_traducir_una_frase_corta_al_idioma_elegido(service):
    with patch.object(
        DeepTranslateTranslator, "_call_mymemory", return_value="Hello, good morning."
    ) as api:
        resultado = service.translate("Hola, buenos días.", "inglés")

    assert resultado == "Hello, good morning."
    api.assert_called_once_with("Hola, buenos días.", "en-GB")


def test_traducir_el_contenido_enriquecido_y_el_resumen(service):
    with patch.object(DeepTranslateTranslator, "_call_mymemory", side_effect=traduccion_falsa):
        enriquecido = service.translate("Contenido ampliado por la IA.", "francés")
        resumen = service.translate("Resumen corto.", "francés")

    assert enriquecido == "CONTENIDO AMPLIADO POR LA IA."
    assert resumen == "RESUMEN CORTO."


def test_traducir_un_texto_largo_dividido_en_trozos(service):
    texto = " ".join(["Esta es una frase de prueba con tildes y eñes."] * 20)
    assert len(texto) > 500

    with patch.object(
        DeepTranslateTranslator, "_call_mymemory", side_effect=traduccion_falsa
    ) as api:
        resultado = service.translate(texto, "en-GB")

    trozos_enviados = [llamada.args[0] for llamada in api.call_args_list]
    assert len(trozos_enviados) > 1
    for trozo in trozos_enviados:
        assert len(trozo) <= 400
    assert trozos_enviados == split_text(texto, 400)
    assert resultado == texto.upper()


def test_conservar_los_parrafos_del_texto(service):
    with patch.object(DeepTranslateTranslator, "_call_mymemory", side_effect=traduccion_falsa):
        resultado = service.translate("Primer párrafo.\n\nSegundo párrafo.", "inglés")

    assert resultado == "PRIMER PÁRRAFO.\n\nSEGUNDO PÁRRAFO."


def test_mostrar_la_traduccion_en_la_terminal(service, capsys):
    service.show_translation("Hello, good morning.")

    salida = capsys.readouterr().out
    assert "=== CONTENIDO TRADUCIDO ===" in salida
    assert "Hello, good morning." in salida


def test_enviar_a_mymemory_el_email_opcional_del_env(monkeypatch):
    monkeypatch.setenv("MYMEMORY_EMAIL", "alumno@ejemplo.com")
    service = DeepTranslateTranslator()

    with patch("src.translator.MyMemoryTranslator") as clase_falsa:
        clase_falsa.return_value.translate.return_value = "Hello."
        resultado = service.translate("Hola.", "inglés")

    assert resultado == "Hello."
    clase_falsa.assert_called_once_with(
        source="es-ES", target="en-GB", email="alumno@ejemplo.com"
    )


def test_traducir_a_un_idioma_no_valido(service):
    with patch.object(DeepTranslateTranslator, "_call_mymemory") as api:
        with pytest.raises(InvalidLanguageError, match="no existe o está mal escrito"):
            service.translate("Hola.", "klingon")

    api.assert_not_called()


def test_traducir_un_texto_vacio(service):
    with patch.object(DeepTranslateTranslator, "_call_mymemory") as api:
        with pytest.raises(EmptyTextError, match="No hay ningún texto que traducir"):
            service.translate("   ", "inglés")

    api.assert_not_called()


def test_superar_el_limite_de_peticiones(service):
    with patch.object(DeepTranslateTranslator, "_call_mymemory", side_effect=TooManyRequests()):
        with pytest.raises(RateLimitError, match="límite de peticiones"):
            service.translate("Hola.", "inglés")


def test_agotar_la_cuota_diaria_de_mymemory(service):
    aviso = "MYMEMORY WARNING: YOU USED ALL AVAILABLE FREE TRANSLATIONS FOR TODAY"
    with patch.object(DeepTranslateTranslator, "_call_mymemory", return_value=aviso):
        with pytest.raises(RateLimitError, match="cuota diaria"):
            service.translate("Hola.", "inglés")


def test_la_api_tarda_demasiado_en_responder(service):
    with patch.object(
        DeepTranslateTranslator, "_call_mymemory", side_effect=requests.exceptions.Timeout()
    ):
        with pytest.raises(TranslationTimeoutError, match="ha tardado demasiado"):
            service.translate("Hola.", "inglés")


def test_no_hay_conexion_con_el_servicio_de_traduccion(service):
    with patch.object(
        DeepTranslateTranslator,
        "_call_mymemory",
        side_effect=requests.exceptions.ConnectionError(),
    ):
        with pytest.raises(NoConnectionError, match="Revisa tu conexión"):
            service.translate("Hola.", "inglés")


def test_un_fragmento_sin_espacios_demasiado_largo(service):
    palabra = "a" * 600
    with patch.object(
        DeepTranslateTranslator, "_call_mymemory", side_effect=NotValidLength(palabra, 0, 500)
    ):
        with pytest.raises(TextTooLongError, match="demasiado largo"):
            service.translate(palabra, "inglés")


def test_usar_auto_como_idioma_de_origen():
    with pytest.raises(InvalidLanguageError, match="no existe o está mal escrito"):
        DeepTranslateTranslator(source_language="auto")
