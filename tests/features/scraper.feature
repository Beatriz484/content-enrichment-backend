# language: es
Característica: Scraping de artículos de Wikipedia
  Como desarrollador del sistema Content Enricher
  Quiero extraer el título y los primeros 5 párrafos de Wikipedia
  Para asegurar que la información base de los artículos es correcta

  Escenario: Extracción exitosa de un artículo existente
    Dado que configuro el scraper con el tema "Python (lenguaje de programación)"
    Cuando ejecuto la extracción de contenido
    Entonces obtengo un diccionario con un título válido
    Y la lista de párrafos contiene exactamente 5 elementos

  Escenario: Error al buscar un artículo que no existe
    Dado que configuro el scraper con un tema inexistente "TemaFalsoQueNoExiste12345ABC"
    Cuando intento extraer el contenido
    Entonces el sistema lanza un error indicando que el artículo no existe
