r"""Feature: Enrichment and summarisation of the content with AI

  As a Content Enricher user
  I want the researched content enriched and optionally summarised
  So that the report reads like a study document instead of raw extracts
"""

from unittest.mock import MagicMock, patch

import pytest

from src.enricher import AiContentEnricher


@pytest.fixture
def enricher_instance():
    return AiContentEnricher(api_key="sk-fake-test-key")


def _mock_response(text):
    choice = MagicMock()
    choice.message.content = text
    return MagicMock(choices=[choice])


def test_initialization_without_key(monkeypatch):
    r"""@failure

    Scenario: Refuse to start without an API key
        Given no OPENAI_API_KEY in the environment
        When the enricher is created without a key
        Then the error says that no API key was found
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="API key not found"):
        AiContentEnricher(api_key=None)


def test_initialization_with_credentials():
    r"""@successful

    Scenario: Start with the configured credentials
        Given the key "sk-test" and the base URL "https://ejemplo/v1"
        When the enricher is created
        Then it holds the configured key
        And it holds the configured base URL
    """
    enricher = AiContentEnricher(api_key="sk-test", base_url="https://ejemplo/v1")

    assert enricher.api_key == "sk-test"
    assert enricher.base_url == "https://ejemplo/v1"


def test_enrich_content_success(enricher_instance):
    r"""@successful

    Scenario: Return the enriched content
        Given an AI that answers "  Texto enriquecido por IA  "
        When I enrich the text "Texto base"
        Then I get "Texto enriquecido por IA" without the surrounding spaces
    """
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response("  Texto enriquecido por IA  "),
    ):
        assert enricher_instance.enrich_content("Texto base") == "Texto enriquecido por IA"


def test_enrich_content_api_failure_returns_original(enricher_instance):
    r"""@failure

    Scenario: Keep the original text when the AI call fails
        Given an AI that answers with the error "API Error 500"
        When I enrich the text "Texto base"
        Then I get the original text "Texto base"
    """
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        side_effect=Exception("API Error 500"),
    ):
        assert enricher_instance.enrich_content("Texto base") == "Texto base"


def test_enrich_content_empty_response_returns_original(enricher_instance):
    r"""@failure

    Scenario: Keep the original text when the AI returns nothing
        Given an AI that answers with an empty text
        When I enrich the text "Texto base"
        Then I get the original text "Texto base"
    """
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response(""),
    ):
        assert enricher_instance.enrich_content("Texto base") == "Texto base"


def test_enrich_content_empty_text_skips_api(enricher_instance):
    r"""@failure

    Scenario: Skip the AI call when there is nothing to enrich
        Given an AI that would never be reached
        When I enrich the text "   "
        Then I get the text "   "
        And the AI is never called
    """
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
    ) as mock_create:
        assert enricher_instance.enrich_content("   ") == "   "

    mock_create.assert_not_called()


def test_enrich_content_truncates_long_inputs(enricher_instance):
    r"""@successful

    Scenario: Truncate an input that is longer than the model accepts
        Given an AI that answers "ok"
        When I enrich a text of 15000 characters
        Then the text sent to the model is shorter than 11000 characters
    """
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response("ok"),
    ) as mock_create:
        enricher_instance.enrich_content("a" * 15000)

    sent = mock_create.call_args.kwargs["messages"][1]["content"]
    assert len(sent) < 11000


def test_summarize_content_success(enricher_instance):
    r"""@successful

    Scenario: Return the generated summary
        Given an AI that answers "Resumen estructurado"
        When I summarise the text "Texto largo"
        Then I get "Resumen estructurado"
    """
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response("Resumen estructurado"),
    ):
        assert enricher_instance.summarize_content("Texto largo") == "Resumen estructurado"


def test_summarize_content_api_failure_returns_original(enricher_instance):
    r"""@failure

    Scenario: Keep the original text when the summary call fails
        Given an AI that answers with the error "API Error 500"
        When I summarise the text "Texto largo"
        Then I get the original text "Texto largo"
    """
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        side_effect=Exception("API Error 500"),
    ):
        assert enricher_instance.summarize_content("Texto largo") == "Texto largo"


def test_summarize_content_empty_response_returns_original(enricher_instance):
    r"""@failure

    Scenario: Keep the original text when the AI returns no summary
        Given an AI that answers with an empty text
        When I summarise the text "Texto largo"
        Then I get the original text "Texto largo"
    """
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response(""),
    ):
        assert enricher_instance.summarize_content("Texto largo") == "Texto largo"


def test_summarize_content_empty_text_skips_api(enricher_instance):
    r"""@failure

    Scenario: Skip the AI call when there is nothing to summarise
        Given an AI that would never be reached
        When I summarise the text ""
        Then I get the text ""
        And the AI is never called
    """
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
    ) as mock_create:
        assert enricher_instance.summarize_content("") == ""

    mock_create.assert_not_called()

def test_summarize_alias_calls_summarize_content(enricher_instance):
    """El alias summarize() invoca correctamente la lógica de resumen."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response("Resumen mediante alias"),
    ):
        assert enricher_instance.summarize("Texto de prueba") == "Resumen mediante alias"