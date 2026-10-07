"""Tests del contrato de DeepTranslateTranslator (HU-04)."""
from unittest.mock import patch

from src.errors import ServiceUnavailableError, ServicioNoDisponibleError
from src.translator import DeepTranslateTranslator


def test_translator_exposes_the_agreed_contract():
    """La CLI espera exactamente este método, sin parámetros extra."""
    assert callable(DeepTranslateTranslator.translate)


def test_translate_returns_the_translated_text():
    """Devuelve el texto traducido; se simula MyMemory para no usar internet."""
    with patch.object(
        DeepTranslateTranslator, "_call_mymemory", return_value="texte traduit"
    ):
        result = DeepTranslateTranslator().translate("texto original", "fr-FR")

    assert result == "texte traduit"


def test_spanish_error_name_is_kept_for_the_teammate_module():
    """Compatibility: src/translator.py importa el error por su nombre en español."""
    assert ServicioNoDisponibleError is ServiceUnavailableError