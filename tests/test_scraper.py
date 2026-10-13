import pytest
import requests
from unittest.mock import MagicMock, patch

from src.scraper import SEARCH_API_URL, WikipediaScraper

ARTICLE_HTML = """
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


def _mock_response(status_code=200, text="", json_data=None):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.json.return_value = json_data if json_data is not None else {}

    if status_code >= 400 and status_code != 404:
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("error HTTP")
    else:
        response.raise_for_status.return_value = None
    return response


@pytest.mark.parametrize("topic", ["", "   "])
def test_constructor_rejects_empty_topic(topic):
    with pytest.raises(ValueError, match="no puede estar vacío"):
        WikipediaScraper(topic)


@patch("src.scraper.requests.get")
def test_extract_content_returns_title_and_five_paragraphs(mock_get):
    mock_get.return_value = _mock_response(text=ARTICLE_HTML)

    result = WikipediaScraper("Python").extract_content()

    assert result["title"] == "Python"
    assert len(result["paragraphs"]) == 5
    assert result["paragraphs"][0] == "Primer párrafo."
    assert mock_get.call_args_list[0][0][0] == "https://es.wikipedia.org/wiki/Python"


@patch("src.scraper.requests.get")
def test_extract_content_missing_article_raises_value_error(mock_get):
    mock_get.side_effect = [
        _mock_response(status_code=404),
        _mock_response(json_data={"query": {"search": []}}),
    ]

    with pytest.raises(ValueError, match="no existe"):
        WikipediaScraper("TemaFalsoQueNoExiste12345ABC").extract_content()


@patch("src.scraper.requests.get")
def test_extract_content_uses_search_as_fallback(mock_get):
    mock_get.side_effect = [
        _mock_response(status_code=404),
        _mock_response(json_data={"query": {"search": [{"title": "Inteligencia artificial"}]}}),
        _mock_response(text=ARTICLE_HTML.replace(">Python<", ">Inteligencia artificial<")),
    ]

    result = WikipediaScraper("inteligencia artificial").extract_content()

    assert result["title"] == "Inteligencia artificial"
    assert len(result["paragraphs"]) == 5
    assert mock_get.call_count == 3
    assert mock_get.call_args_list[1][0][0] == SEARCH_API_URL
    assert mock_get.call_args_list[2][0][0].endswith("/wiki/Inteligencia_artificial")


@patch("src.scraper.requests.get")
def test_failed_fallback_search_raises_connection_error(mock_get):
    mock_get.side_effect = [
        _mock_response(status_code=404),
        requests.exceptions.ConnectionError("sin internet"),
    ]

    with pytest.raises(ConnectionError, match="Error de conexión"):
        WikipediaScraper("Python").extract_content()


@patch("src.scraper.requests.get")
def test_fallback_title_not_found_raises_value_error(mock_get):
    mock_get.side_effect = [
        _mock_response(status_code=404),
        _mock_response(json_data={"query": {"search": [{"title": "Otro artículo"}]}}),
        _mock_response(status_code=404),
    ]

    with pytest.raises(ValueError, match="no existe"):
        WikipediaScraper("Tema Falso").extract_content()


@patch("src.scraper.requests.get")
def test_network_failure_raises_connection_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("sin internet")

    with pytest.raises(ConnectionError, match="Error de conexión"):
        WikipediaScraper("Python").extract_content()


@patch("src.scraper.requests.get")
def test_http_failure_raises_connection_error(mock_get):
    mock_get.return_value = _mock_response(status_code=500)

    with pytest.raises(ConnectionError, match="Error de conexión"):
        WikipediaScraper("Python").extract_content()
