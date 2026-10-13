from unittest.mock import patch

from src.errors import ServiceUnavailableError, ServicioNoDisponibleError
from src.translator import DeepTranslateTranslator


def test_translator_exposes_the_agreed_contract():
    assert callable(DeepTranslateTranslator.translate)


def test_translate_returns_the_translated_text():
    with patch.object(
        DeepTranslateTranslator, "_call_mymemory", return_value="texte traduit"
    ):
        result = DeepTranslateTranslator().translate("texto original", "fr-FR")

    assert result == "texte traduit"


def test_spanish_error_name_is_kept_for_the_teammate_module():
    assert ServicioNoDisponibleError is ServiceUnavailableError