"""Tests del enriquecedor con IA (sin llamadas reales a la API)."""
import pytest
from unittest.mock import MagicMock, patch

from src.enricher import AiContentEnricher, ajustar_longitud, texto_valido
from src.errors import AiError


@pytest.fixture
def enricher_instance():
    """Instancia con clave simulada."""
    return AiContentEnricher(api_key="sk-fake-test-key")


def _respuesta(texto):
    eleccion = MagicMock()
    eleccion.message.content = texto
    return MagicMock(choices=[eleccion])


# --- Credenciales -----------------------------------------------------------

def test_initialization_without_key(monkeypatch):
    """Sin API key la construcción falla de forma explícita."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="API key not found"):
        AiContentEnricher(api_key=None)


def test_initialization_con_base_url_y_modelo():
    """La clave, la URL base y el modelo se pueden inyectar o leer del entorno."""
    enricher = AiContentEnricher(api_key="sk-test", base_url="https://ejemplo/v1")

    assert enricher.api_key == "sk-test"
    assert enricher.base_url == "https://ejemplo/v1"
    assert enricher.model


# --- Utilidades -------------------------------------------------------------

def test_texto_valido():
    """Un texto vacío o no cadena no es procesable."""
    assert texto_valido("Texto válido") is True
    assert texto_valido("   ") is False
    assert texto_valido("") is False
    assert texto_valido(None) is False


def test_ajustar_longitud():
    """Recorte de seguridad para no desbordar el contexto del modelo."""
    texto_largo = "a" * 15000
    assert len(ajustar_longitud(texto_largo, max_characters=10000)) == 10000
    assert ajustar_longitud("corto") == "corto"


# --- Enriquecimiento --------------------------------------------------------

def test_enrich_content_success(enricher_instance):
    """La respuesta enriquecida se devuelve limpia."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_respuesta("  Texto enriquecido por IA  "),
    ):
        assert enricher_instance.enrich_content("Texto base") == "Texto enriquecido por IA"


def test_enrich_content_falla_de_api_lanza_error(enricher_instance):
    """Regresión: antes devolvía el original haciéndose pasar por enriquecido."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        side_effect=Exception("API Error 500"),
    ):
        with pytest.raises(AiError, match="No se pudo contactar"):
            enricher_instance.enrich_content("Texto base")


def test_enrich_content_respuesta_vacia_lanza_error(enricher_instance):
    """Una respuesta vacía de la API nunca se acepta como contenido."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_respuesta(""),
    ):
        with pytest.raises(AiError, match="respuesta vacía"):
            enricher_instance.enrich_content("Texto base")


def test_enrich_content_texto_vacio_lanza_error(enricher_instance):
    """No se envía a la API un texto sin contenido."""
    with pytest.raises(AiError, match="texto vacío"):
        enricher_instance.enrich_content("   ")


def test_enrich_content_recorta_entradas_demasiado_largas(enricher_instance):
    """El texto se trunca antes de enviarlo para no desbordar el contexto."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_respuesta("ok"),
    ) as mock_create:
        enricher_instance.enrich_content("a" * 15000)

    enviado = mock_create.call_args.kwargs["messages"][1]["content"]
    assert len(enviado) < 11000


# --- Resumen ----------------------------------------------------------------

def test_summarize_content_success(enricher_instance):
    """El resumen estructurado se devuelve limpio."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        return_value=_respuesta("Resumen estructurado"),
    ):
        assert enricher_instance.summarize_content("Texto largo") == "Resumen estructurado"


def test_summarize_content_falla_de_api_lanza_error(enricher_instance):
    """El resumen también propaga el fallo en lugar de devolver el original."""
    with patch.object(
        enricher_instance.client.chat.completions,
        "create",
        side_effect=Exception("API Error 500"),
    ):
        with pytest.raises(AiError, match="No se pudo contactar"):
            enricher_instance.summarize_content("Texto largo")
