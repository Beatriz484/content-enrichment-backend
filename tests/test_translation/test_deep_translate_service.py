from unittest.mock import patch

import pytest
import requests
from deep_translator.exceptions import NotValidLength, TooManyRequests

from src.translation.text_splitter import split_text
from src.translation.translation_errors import (
    EmptyTextError,
    InvalidLanguageError,
    NoConnectionError,
    RateLimitError,
    TextTooLongError,
    TranslationTimeoutError,
)
from src.translation import DeepTranslateTranslator


@pytest.fixture
def service():
    return DeepTranslateTranslator(email="")


def fake_translation(text, code):
    return text.upper()


def test_translates_a_short_sentence_to_the_chosen_language(service):
    r"""@successful

    Scenario: Translate a short sentence to the chosen language
        Given a MyMemory call that answers "Hello, good morning."
        When I translate "Hola, buenos días." to "inglés"
        Then I get "Hello, good morning."
        And MyMemory receives the text and the code "en-GB"
    """
    with patch.object(
        DeepTranslateTranslator, "_call_mymemory", return_value="Hello, good morning."
    ) as api:
        result = service.translate("Hola, buenos días.", "inglés")

    assert result == "Hello, good morning."
    api.assert_called_once_with("Hola, buenos días.", "en-GB")


def test_translates_the_enriched_content_and_the_summary(service):
    r"""@successful

    Scenario: Translate both the enriched content and the summary
        Given a MyMemory call that echoes its input
        When I translate "Contenido ampliado por la IA." to "francés"
        And I translate "Resumen corto." to "francés"
        Then I get "CONTENIDO AMPLIADO POR LA IA."
        And I get "RESUMEN CORTO."
    """
    with patch.object(DeepTranslateTranslator, "_call_mymemory", side_effect=fake_translation):
        enriched = service.translate("Contenido ampliado por la IA.", "francés")
        summary = service.translate("Resumen corto.", "francés")

    assert enriched == "CONTENIDO AMPLIADO POR LA IA."
    assert summary == "RESUMEN CORTO."


def test_translates_a_long_text_split_into_chunks(service):
    r"""@successful

    Scenario: Translate a long text by sending it in chunks
        Given a text longer than 500 characters
        When I translate it to "en-GB"
        Then more than one chunk is sent
        And every chunk is at most 400 characters long
        And the chunks are the ones the splitter produces
        And the final result joins every translated chunk
    """
    text = " ".join(["Esta es una frase de prueba con tildes y eñes."] * 20)
    assert len(text) > 500

    with patch.object(
        DeepTranslateTranslator, "_call_mymemory", side_effect=fake_translation
    ) as api:
        result = service.translate(text, "en-GB")

    sent_chunks = [call.args[0] for call in api.call_args_list]
    assert len(sent_chunks) > 1
    for chunk in sent_chunks:
        assert len(chunk) <= 400
    assert sent_chunks == split_text(text, 400)
    assert result == text.upper()


def test_preserves_the_paragraphs_of_the_text(service):
    r"""@successful

    Scenario: Keep the line breaks between paragraphs
        Given a MyMemory call that echoes its input
        When I translate "Primer párrafo.\n\nSegundo párrafo." to "inglés"
        Then I get "PRIMER PÁRRAFO.\n\nSEGUNDO PÁRRAFO."
    """
    with patch.object(DeepTranslateTranslator, "_call_mymemory", side_effect=fake_translation):
        result = service.translate("Primer párrafo.\n\nSegundo párrafo.", "inglés")

    assert result == "PRIMER PÁRRAFO.\n\nSEGUNDO PÁRRAFO."


def test_shows_the_translation_in_the_terminal(service, capsys):
    r"""@successful

    Scenario: Show the translation in the terminal
        Given the translated text "Hello, good morning."
        When I show the translation
        Then the terminal shows "=== CONTENIDO TRADUCIDO ==="
        And the terminal shows "Hello, good morning."
    """
    service.show_translation("Hello, good morning.")

    output = capsys.readouterr().out
    assert "=== CONTENIDO TRADUCIDO ===" in output
    assert "Hello, good morning." in output


def test_sends_the_optional_env_email_to_mymemory(monkeypatch):
    r"""@successful

    Scenario: Send the optional MYMEMORY_EMAIL from the .env
        Given the environment variable MYMEMORY_EMAIL is "alumno@ejemplo.com"
        When I translate "Hola." to "inglés"
        Then MyMemory receives the origin "es-ES"
        And MyMemory receives the target "en-GB"
        And MyMemory receives the email
    """
    monkeypatch.setenv("MYMEMORY_EMAIL", "alumno@ejemplo.com")
    service = DeepTranslateTranslator()

    with patch("src.translation.translator.MyMemoryTranslator") as fake_class:
        fake_class.return_value.translate.return_value = "Hello."
        result = service.translate("Hola.", "inglés")

    assert result == "Hello."
    fake_class.assert_called_once_with(
        source="es-ES", target="en-GB", email="alumno@ejemplo.com"
    )


def test_rejects_an_invalid_target_language(service):
    r"""@failure

    Scenario: Reject a target language that does not exist
        Given a MyMemory call that would never be reached
        When I try to translate "Hola." to "klingon"
        Then the error says "no existe o está mal escrito"
        And MyMemory is never called
    """
    with patch.object(DeepTranslateTranslator, "_call_mymemory") as api:
        with pytest.raises(InvalidLanguageError, match="no existe o está mal escrito"):
            service.translate("Hola.", "klingon")

    api.assert_not_called()


def test_rejects_an_empty_text(service):
    r"""@failure

    Scenario: Reject a text with nothing to translate
        Given a MyMemory call that would never be reached
        When I try to translate "   " to "inglés"
        Then the error says "No hay ningún texto que traducir"
        And MyMemory is never called
    """
    with patch.object(DeepTranslateTranslator, "_call_mymemory") as api:
        with pytest.raises(EmptyTextError, match="No hay ningún texto que traducir"):
            service.translate("   ", "inglés")

    api.assert_not_called()


def test_raises_a_rate_limit_error_when_the_service_throttles(service):
    r"""@failure

    Scenario: Report the request limit of the service
        Given a MyMemory call that answers with too many requests
        When I try to translate "Hola." to "inglés"
        Then the error says "límite de peticiones"
    """
    with patch.object(DeepTranslateTranslator, "_call_mymemory", side_effect=TooManyRequests()):
        with pytest.raises(RateLimitError, match="límite de peticiones"):
            service.translate("Hola.", "inglés")


def test_raises_a_rate_limit_error_when_the_daily_quota_is_used_up(service):
    r"""@failure

    Scenario: Report that the daily MyMemory quota is used up
        Given a MyMemory call that answers "MYMEMORY WARNING: YOU USED ALL AVAILABLE FREE TRANSLATIONS FOR TODAY"
        When I try to translate "Hola." to "inglés"
        Then the error says "cuota diaria"
    """
    notice = "MYMEMORY WARNING: YOU USED ALL AVAILABLE FREE TRANSLATIONS FOR TODAY"
    with patch.object(DeepTranslateTranslator, "_call_mymemory", return_value=notice):
        with pytest.raises(RateLimitError, match="cuota diaria"):
            service.translate("Hola.", "inglés")


def test_raises_a_timeout_error_when_the_api_takes_too_long(service):
    r"""@failure

    Scenario: Report an API that takes too long to answer
        Given a MyMemory call that times out
        When I try to translate "Hola." to "inglés"
        Then the error says "ha tardado demasiado"
    """
    with patch.object(
        DeepTranslateTranslator, "_call_mymemory", side_effect=requests.exceptions.Timeout()
    ):
        with pytest.raises(TranslationTimeoutError, match="ha tardado demasiado"):
            service.translate("Hola.", "inglés")


def test_raises_a_connection_error_when_there_is_no_network(service):
    r"""@failure

    Scenario: Report that there is no connection to the service
        Given a MyMemory call that fails to connect
        When I try to translate "Hola." to "inglés"
        Then the error says "Revisa tu conexión"
    """
    with patch.object(
        DeepTranslateTranslator,
        "_call_mymemory",
        side_effect=requests.exceptions.ConnectionError(),
    ):
        with pytest.raises(NoConnectionError, match="Revisa tu conexión"):
            service.translate("Hola.", "inglés")


def test_raises_a_text_too_long_error_for_a_chunk_without_spaces(service):
    r"""@failure

    Scenario: Report a chunk that is too long because it has no spaces
        Given a single word of 600 letters
        And a MyMemory call that refuses it as too long
        When I try to translate it to "inglés"
        Then the error says "demasiado largo"
    """
    word = "a" * 600
    with patch.object(
        DeepTranslateTranslator, "_call_mymemory", side_effect=NotValidLength(word, 0, 500)
    ):
        with pytest.raises(TextTooLongError, match="demasiado largo"):
            service.translate(word, "inglés")


def test_rejects_auto_as_the_source_language():
    r"""@failure

    Scenario: Reject "auto" as the source language
        When I create the service with the source language "auto"
        Then the error says "no existe o está mal escrito"
    """
    with pytest.raises(InvalidLanguageError, match="no existe o está mal escrito"):
        DeepTranslateTranslator(source_language="auto")
