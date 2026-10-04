from unittest.mock import MagicMock, patch
import pytest
from src.enricher import AiContentEnricher


@pytest.fixture
def enricher_instancia():
    """Fixture que proporciona una instancia de AiContentEnricher con clave de prueba."""
    return AiContentEnricher(api_key="test-api-key")


def test_inicializacion_sin_clave():
    """Valida que se lance ValueError si no hay API key disponible."""
    with patch("os.getenv", return_value=None):
        with pytest.raises(ValueError) as exc_info:
            AiContentEnricher(api_key=None)
        assert "No se encontró la clave de API" in str(exc_info.value)


def test_es_texto_valido(enricher_instancia):
    """Valida los filtros de detección de texto vacío o no válido."""
    assert enricher_instancia._es_texto_valido("") is False
    assert enricher_instancia._es_texto_valido("   ") is False
    assert enricher_instancia._es_texto_valido(None) is False
    assert enricher_instancia._es_texto_valido("Texto con contenido") is True


def test_ajustar_longitud(enricher_instancia):
    """Comprueba que el texto se recorte adecuadamente al superar el límite."""
    texto_largo = "a" * 15000
    texto_recortado = enricher_instancia._ajustar_longitud(texto_largo, max_caracteres=500)
    assert len(texto_recortado) == 500

    texto_corto = "Texto dentro de límites"
    assert enricher_instancia._ajustar_longitud(texto_corto) == texto_corto


def test_enriquecer_contenido_texto_invalido(enricher_instancia):
    """Si el texto está vacío, retorna el mismo texto sin llamar a la API."""
    assert enricher_instancia.enriquecer_contenido("") == ""


def test_enriquecer_contenido_exitoso(enricher_instancia):
    """Valida el enriquecimiento simulando una respuesta exitosa de OpenAI."""
    mock_respuesta = MagicMock()
    mock_respuesta.choices = [MagicMock()]
    mock_respuesta.choices[0].message.content = "Texto enriquecido por IA"

    with patch.object(
        enricher_instancia.client.chat.completions,
        "create",
        return_value=mock_respuesta
    ):
        resultado = enricher_instancia.enriquecer_contenido("Texto base")
        assert resultado == "Texto enriquecido por IA"


def test_enriquecer_contenido_degradacion_error(enricher_instancia):
    """Si la API falla, debe degradar con elegancia y devolver el texto original."""
    with patch.object(
        enricher_instancia.client.chat.completions,
        "create",
        side_effect=Exception("API Timeout")
    ):
        resultado = enricher_instancia.enriquecer_contenido("Texto original de respaldo")
        assert resultado == "Texto original de respaldo"


def test_resumir_contenido_exitoso(enricher_instancia):
    """Valida la generación del resumen simulando una respuesta exitosa."""
    mock_respuesta = MagicMock()
    mock_respuesta.choices = [MagicMock()]
    mock_respuesta.choices[0].message.content = "Puntos clave resumidos"

    with patch.object(
        enricher_instancia.client.chat.completions,
        "create",
        return_value=mock_respuesta
    ):
        resultado = enricher_instancia.resumir_contenido("Texto base a resumir")
        assert resultado == "Puntos clave resumidos"


def test_resumir_contenido_degradacion_error(enricher_instancia):
    """Si la API falla al resumir, debe retornar el texto original."""
    with patch.object(
        enricher_instancia.client.chat.completions,
        "create",
        side_effect=Exception("API Error 500")
    ):
        resultado = enricher_instancia.resumir_contenido("Texto base resumen")
        assert resultado == "Texto base resumen"