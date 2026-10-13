r"""Feature: Contract of the translation service

  As a developer of the Content Enricher
  I want the translator to honour the contract the CLI depends on
  So that the last step of the pipeline never changes shape
"""

from unittest.mock import patch

from src.errors import ServiceUnavailableError, ServicioNoDisponibleError
from src.translation import DeepTranslateTranslator


def test_translator_exposes_the_agreed_contract():
    r"""@successful

    Scenario: Expose the translate entry point
        Given the DeepTranslateTranslator class
        When I look up its translate method
        Then the method is callable
    """
    assert callable(DeepTranslateTranslator.translate)


def test_translate_returns_the_translated_text():
    r"""@successful

    Scenario: Return the text returned by MyMemory
        Given a MyMemory call that answers "texte traduit"
        When I translate "texto original" to "fr-FR"
        Then I get "texte traduit"
    """
    with patch.object(
        DeepTranslateTranslator, "_call_mymemory", return_value="texte traduit"
    ):
        result = DeepTranslateTranslator().translate("texto original", "fr-FR")

    assert result == "texte traduit"


def test_spanish_error_name_is_kept_for_the_teammate_module():
    r"""@successful

    Scenario: Keep the Spanish error name as an alias
        Given the ServiceUnavailableError class
        When I look up the Spanish name ServicioNoDisponibleError
        Then both names refer to the same class
    """
    assert ServicioNoDisponibleError is ServiceUnavailableError
