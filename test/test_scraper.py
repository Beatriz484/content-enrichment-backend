from pytest_bdd import scenarios, given, when, then, parsers
from src.scraper import WikipediaScraper

# Conectamos este archivo Python con el archivo .feature que creamos antes
scenarios('features/scraper.feature')

@given(parsers.parse('que configuro el scraper con el tema "{tema}"'), target_fixture="datos_prueba")
def configurar_scraper(tema):
    return {"tema": tema, "resultado": None, "error": None}

@given(parsers.parse('que configuro el scraper con un tema inexistente "{tema}"'), target_fixture="datos_prueba")
def configurar_scraper_inexistente(tema):
    return {"tema": tema, "resultado": None, "error": None}

@when('ejecuto la extracción de contenido')
def ejecutar_extraccion(datos_prueba):
    try:
        scraper = WikipediaScraper(datos_prueba["tema"])
        datos_prueba["resultado"] = scraper.extraer_contenido()
    except Exception as e:
        datos_prueba["error"] = e

@when('intento extraer el contenido')
def intentar_extraccion(datos_prueba):
    try:
        scraper = WikipediaScraper(datos_prueba["tema"])
        datos_prueba["resultado"] = scraper.extraer_contenido()
    except Exception as e:
        datos_prueba["error"] = e

@then('obtengo un diccionario con un título válido')
def verificar_titulo(datos_prueba):
    assert datos_prueba["error"] is None
    assert "titulo" in datos_prueba["resultado"]
    assert len(datos_prueba["resultado"]["titulo"]) > 0

@then('la lista de párrafos contiene exactamente 5 elementos')
def verificar_parrafos(datos_prueba):
    assert "parrafos" in datos_prueba["resultado"]
    assert len(datos_prueba["resultado"]["parrafos"]) == 5

@then('el sistema lanza un error indicando que el artículo no existe')
def verificar_error(datos_prueba):
    assert datos_prueba["error"] is not None
