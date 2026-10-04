import pytest
from unittest.mock import MagicMock, patch
from src.enricher import AiContentEnricher


@pytest.fixture
def enricher_instance():
    """Fixture que devuelve una instancia con clave simulada."""
    return AiContentEnricher(api_key="sk-fake-test-key")


def test_initialization_without_key(monkeypatch):
    """Verifica que se lance ValueError si no existe API key."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        AiContentEnricher(api_key=None)


def test_is_valid_text(enricher_instance):
    """Verifica la validación de texto vacío o incorrecto."""
    assert enricher_instance._is_valid_text("Texto válido") is True
    assert enricher_instance._is_valid_text("   ") is False
    assert enricher_instance._is_valid_text("") is False
    assert enricher_instance._is_valid_text(None) is False


def test_adjust_length(enricher_instance):
    """Comprueba el recorte de seguridad según longitud máxima."""
    texto_largo = "a" * 15000
    texto_recortado = enricher_instance._adjust_length(texto_largo, max_characters=10000)
    assert len(texto_recortado) == 10000


def test_enrich_content_invalid_text(enricher_instance):
    """Retorna el texto original si no es válido."""
    assert enricher_instance.enrich_content("   ") == "   "


def test_enrich_content_success(enricher_instance):
    """Comprueba la respuesta enriquecida exitosa usando mock."""
    mock_choice = MagicMock()
    mock_choice.message.content = "Texto enriquecido por IA"
    mock_response = MagicMock(choices=[mock_choice])

    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=mock_response,
    ):
        resultado = enricher_instance.enrich_content("Texto base")
        assert resultado == "Texto enriquecido por IA"


def test_enrich_content_fallback_error(enricher_instance):
    """Comprueba la degradación elegante ante fallo de API."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        side_effect=Exception("API Error 500"),
    ):
        resultado = enricher_instance.enrich_content("Texto base")
        assert resultado == "Texto base"


def test_summarize_content_success(enricher_instance):
    """Comprueba el resumen exitoso usando mock."""
    mock_choice = MagicMock()
    mock_choice.message.content = "Resumen estructurado"
    mock_response = MagicMock(choices=[mock_choice])

    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=mock_response,
    ):
        resultado = enricher_instance.summarize_content("Texto largo")
        assert resultado == "Resumen estructurado"


def test_summarize_content_fallback_error(enricher_instance):
    """Comprueba la degradación elegante en el resumen ante fallos."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        side_effect=Exception("API Error 500"),
    ):
        resultado = enricher_instance.summarize_content("Texto base resumen")
        assert resultado == "Texto base resumen"