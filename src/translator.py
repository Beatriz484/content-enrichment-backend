"""Servicio de traducción del Content Enricher.

Traduce el contenido enriquecido y el resumen al idioma elegido por el
usuario usando la librería ``deep_translator`` (clase ``MyMemoryTranslator``).

Responsabilidad única: este módulo solo traduce. No investiga, no enriquece
y no exporta.

Interfaz pública:

    translate(text: str, target_language: str) -> str
"""

# Idioma de origen por defecto: el scraper lee de es.wikipedia.org
DEFAULT_SOURCE_LANGUAGE = "es-ES"


class DeepTranslateService:
    """Traduce textos con MyMemory a través de deep_translator."""

    def __init__(self, source_language=DEFAULT_SOURCE_LANGUAGE, email=None):
        """
        Args:
            source_language: Código del idioma de origen (por defecto "es-ES").
            email: Email opcional para MyMemory. Sube el límite diario de uso.
        """
        self.source_language = source_language
        self.email = email
