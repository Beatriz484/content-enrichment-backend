import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from src.scraper import WikipediaScraper

# Estos escenarios consultan Wikipedia en tiempo real: se ejecutan con `pytest -m integration`
pytestmark = pytest.mark.integration

# Conectamos este archivo Python con el archivo .feature que creamos antes
scenarios('features/scraper.feature')

@given(parsers.parse('que configuro el scraper con el tema "{topic}"'), target_fixture="test_data")
def configure_scraper(topic):
    return {"topic": topic, "result": None, "error": None}

@given(parsers.parse('que configuro el scraper con un tema inexistente "{topic}"'), target_fixture="test_data")
def configure_missing_scraper(topic):
    return {"topic": topic, "result": None, "error": None}

@when('ejecuto la extracción de contenido')
def run_extraction(test_data):
    try:
        scraper = WikipediaScraper(test_data["topic"])
        test_data["result"] = scraper.extract_content()
    except Exception as error:
        test_data["error"] = error

@when('intento extraer el contenido')
def try_extraction(test_data):
    try:
        scraper = WikipediaScraper(test_data["topic"])
        test_data["result"] = scraper.extract_content()
    except Exception as error:
        test_data["error"] = error

@then('obtengo un diccionario con un título válido')
def check_title(test_data):
    assert test_data["error"] is None
    assert "title" in test_data["result"]
    assert len(test_data["result"]["title"]) > 0

@then('la lista de párrafos contiene exactamente 5 elementos')
def check_paragraphs(test_data):
    assert "paragraphs" in test_data["result"]
    assert len(test_data["result"]["paragraphs"]) == 5

@then('el sistema lanza un error indicando que el artículo no existe')
def check_error(test_data):
    assert test_data["error"] is not None
