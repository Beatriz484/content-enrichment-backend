"""Tests unitarios de WikipediaScraper con peticiones simuladas (sin red)."""
import pytest
import requests
from unittest.mock import MagicMock, patch

from src.scraper import API_BUSQUEDA, WikipediaScraper

HTML_ARTICULO = """
<html><body>
  <div id="firstHeading">Python</div>
  <div id="mw-content-text">
    <p>Primer párrafo.</p>
    <p></p>
    <p>Segundo párrafo.</p>
    <p>Tercer párrafo.</p>
    <p>Cuarto párrafo.</p>
    <p>Quinto párrafo.</p>
    <p>Sexto párrafo que no debe entrar.</p>
  </div>
</body></html>
"""


def _respuesta(status_code=200, text="", json_data=None):
    """Construye una respuesta simulada de requests."""
    respuesta = MagicMock()
    respuesta.status_code = status_code
    respuesta.text = text
    respuesta.json.return_value = json_data if json_data is not None else {}

    if status_code >= 400 and status_code != 404:
        respuesta.raise_for_status.side_effect = requests.exceptions.HTTPError("error HTTP")
    else:
        respuesta.raise_for_status.return_value = None
    return respuesta


@pytest.mark.parametrize("tema", ["", "   "])
def test_constructor_rechaza_tema_vacio(tema):
    """Un tema vacío o en blanco debe rechazarse en la construcción."""
    with pytest.raises(ValueError, match="no puede estar vacío"):
        WikipediaScraper(tema)


@patch("src.scraper.requests.get")
def test_extraer_contenido_devuelve_titulo_y_cinco_parrafos(mock_get):
    """Extrae el título y exactamente los primeros 5 párrafos con contenido."""
    mock_get.return_value = _respuesta(text=HTML_ARTICULO)

    resultado = WikipediaScraper("Python").extraer_contenido()

    assert resultado["titulo"] == "Python"
    assert len(resultado["parrafos"]) == 5
    assert resultado["parrafos"][0] == "Primer párrafo."
    # Primero se intenta la URL directa construida con el tema
    assert mock_get.call_args_list[0][0][0] == "https://es.wikipedia.org/wiki/Python"


@patch("src.scraper.requests.get")
def test_extraer_contenido_articulo_inexistente(mock_get):
    """Si no existe el artículo ni en la búsqueda de respaldo, lanza ValueError."""
    mock_get.side_effect = [
        _respuesta(status_code=404),
        _respuesta(json_data={"query": {"search": []}}),
    ]

    with pytest.raises(ValueError, match="no existe"):
        WikipediaScraper("TemaFalsoQueNoExiste12345ABC").extraer_contenido()


@patch("src.scraper.requests.get")
def test_extraer_contenido_usa_busqueda_como_respaldo(mock_get):
    """Ante un 404, busca el artículo por texto y extrae su contenido."""
    mock_get.side_effect = [
        _respuesta(status_code=404),
        _respuesta(json_data={"query": {"search": [{"title": "Inteligencia artificial"}]}}),
        _respuesta(text=HTML_ARTICULO.replace(">Python<", ">Inteligencia artificial<")),
    ]

    resultado = WikipediaScraper("inteligencia artificial").extraer_contenido()

    assert resultado["titulo"] == "Inteligencia artificial"
    assert len(resultado["parrafos"]) == 5
    assert mock_get.call_count == 3
    # La segunda llamada consulta la API de búsqueda de Wikipedia
    assert mock_get.call_args_list[1][0][0] == API_BUSQUEDA
    # La tercera vuelve a pedir el artículo con el título resuelto
    assert mock_get.call_args_list[2][0][0].endswith("/wiki/Inteligencia_artificial")


@patch("src.scraper.requests.get")
def test_fallo_en_la_busqueda_de_respaldo_lanza_connection_error(mock_get):
    "Si la API de búsqueda tampoco responde, el error también queda controlado."
    mock_get.side_effect = [
        _respuesta(status_code=404),
        requests.exceptions.ConnectionError("sin internet"),
    ]

    with pytest.raises(ConnectionError, match="Error de conexión"):
        WikipediaScraper("Python").extraer_contenido()


@patch("src.scraper.requests.get")
def test_respaldo_que_tampoco_existe_lanza_value_error(mock_get):
    "Si el artículo que devuelve la búsqueda tampoco existe, se reporta el error."
    mock_get.side_effect = [
        _respuesta(status_code=404),
        _respuesta(json_data={"query": {"search": [{"title": "Otro artículo"}]}}),
        _respuesta(status_code=404),
    ]

    with pytest.raises(ValueError, match="no existe"):
        WikipediaScraper("Tema Falso").extraer_contenido()


@patch("src.scraper.requests.get")
def test_error_de_red_lanza_connection_error(mock_get):
    "Un fallo de red se transforma en ConnectionError controlado."
    mock_get.side_effect = requests.exceptions.ConnectionError("sin internet")

    with pytest.raises(ConnectionError, match="Error de conexión"):
        WikipediaScraper("Python").extraer_contenido()


@patch("src.scraper.requests.get")
def test_error_http_lanza_connection_error(mock_get):
    "Un estado HTTP distinto de 404 (p. ej. 500) también se controla."
    mock_get.return_value = _respuesta(status_code=500)

    with pytest.raises(ConnectionError, match="Error de conexión"):
        WikipediaScraper("Python").extraer_contenido()
