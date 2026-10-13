import pytest
from unittest.mock import MagicMock, patch

from src.enricher import AiContentEnricher


@pytest.fixture
def enricher_instance():
    return AiContentEnricher(api_key="sk-fake-test-key")


def _mock_response(text):
    choice = MagicMock()
    choice.message.content = text
    return MagicMock(choices=[choice])


def test_initialization_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="API key not found"):
        AiContentEnricher(api_key=None)


def test_initialization_with_credentials():
    enricher = AiContentEnricher(api_key="sk-test", base_url="https://ejemplo/v1")

    assert enricher.api_key == "sk-test"
    assert enricher.base_url == "https://ejemplo/v1"


def test_enrich_content_success(enricher_instance):
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response("  Texto enriquecido por IA  "),
    ):
        assert enricher_instance.enrich_content("Texto base") == "Texto enriquecido por IA"


def test_enrich_content_api_failure_returns_original(enricher_instance):
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        side_effect=Exception("API Error 500"),
    ):
        assert enricher_instance.enrich_content("Texto base") == "Texto base"


def test_enrich_content_empty_response_returns_original(enricher_instance):
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response(""),
    ):
        assert enricher_instance.enrich_content("Texto base") == "Texto base"


def test_enrich_content_empty_text_skips_api(enricher_instance):
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
    ) as mock_create:
        assert enricher_instance.enrich_content("   ") == "   "

    mock_create.assert_not_called()


def test_enrich_content_truncates_long_inputs(enricher_instance):
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response("ok"),
    ) as mock_create:
        enricher_instance.enrich_content("a" * 15000)

    sent = mock_create.call_args.kwargs["messages"][1]["content"]
    assert len(sent) < 11000


def test_summarize_content_success(enricher_instance):
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response("Resumen estructurado"),
    ):
        assert enricher_instance.summarize_content("Texto largo") == "Resumen estructurado"


def test_summarize_content_api_failure_returns_original(enricher_instance):
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        side_effect=Exception("API Error 500"),
    ):
        assert enricher_instance.summarize_content("Texto largo") == "Texto largo"


def test_summarize_content_empty_response_returns_original(enricher_instance):
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response(""),
    ):
        assert enricher_instance.summarize_content("Texto largo") == "Texto largo"


def test_summarize_content_empty_text_skips_api(enricher_instance):
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
    ) as mock_create:
        assert enricher_instance.summarize_content("") == ""

    mock_create.assert_not_called()
