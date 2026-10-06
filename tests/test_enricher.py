"""Tests del enriquecedor con IA (sin llamadas reales a la API)."""
import pytest
from unittest.mock import MagicMock, patch

from src.enricher import AiContentEnricher


@pytest.fixture
def enricher_instance():
    """Instancia con clave simulada."""
    return AiContentEnricher(api_key="sk-fake-test-key")


def _mock_response(text):
    """Construye una respuesta simulada de la API de chat completions."""
    choice = MagicMock()
    choice.message.content = text
    return MagicMock(choices=[choice])


# --- Credenciales -----------------------------------------------------------

def test_initialization_without_key(monkeypatch):
    """Sin API key la construcción falla de forma explícita."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="API key not found"):
        AiContentEnricher(api_key=None)


def test_initialization_with_credentials():
    """La clave y la URL base se pueden inyectar desde el constructor."""
    enricher = AiContentEnricher(api_key="sk-test", base_url="https://ejemplo/v1")

    assert enricher.api_key == "sk-test"
    assert enricher.base_url == "https://ejemplo/v1"


# --- Enriquecimiento ---------------------------------------------------------

def test_enrich_content_success(enricher_instance):
    """La respuesta enriquecida se devuelve limpia (sin espacios sobrantes)."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response("  Texto enriquecido por IA  "),
    ):
        assert enricher_instance.enrich_content("Texto base") == "Texto enriquecido por IA"


def test_enrich_content_api_failure_returns_original(enricher_instance):
    """Un fallo de la API se registra y devuelve el texto original sin romper el flujo."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        side_effect=Exception("API Error 500"),
    ):
        assert enricher_instance.enrich_content("Texto base") == "Texto base"


def test_enrich_content_empty_response_returns_original(enricher_instance):
    """Una respuesta vacía de la API nunca se acepta como contenido enriquecido."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response(""),
    ):
        assert enricher_instance.enrich_content("Texto base") == "Texto base"


def test_enrich_content_empty_text_skips_api(enricher_instance):
    """Un texto sin contenido no se envía a la API."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
    ) as mock_create:
        assert enricher_instance.enrich_content("   ") == "   "

    mock_create.assert_not_called()


def test_enrich_content_truncates_long_inputs(enricher_instance):
    """El texto se trunca antes de enviarlo para no desbordar el contexto."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response("ok"),
    ) as mock_create:
        enricher_instance.enrich_content("a" * 15000)

    sent = mock_create.call_args.kwargs["messages"][1]["content"]
    assert len(sent) < 11000


# --- Resumen -----------------------------------------------------------------

def test_summarize_content_success(enricher_instance):
    """El resumen estructurado se devuelve limpio."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_mock_response("Resumen estructurado"),
    ):
        assert enricher_instance.summarize_content("Texto largo") == "Resumen estructurado"


def test_summarize_content_api_failure_returns_original(enricher_instance):
    """El resumen también devuelve el original si la API falla, sin interrumpir el flujo."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        side_effect=Exception("API Error 500"),
    ):
        assert enricher_instance.summarize_content("Texto largo") == "Texto largo"


def test_summarize_content_empty_text_skips_api(enricher_instance):
    """Un resumen de texto vacío no llega a consultar a la API."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
    ) as mock_create:
        assert enricher_instance.summarize_content("") == ""

    mock_create.assert_not_called()
