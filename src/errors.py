"""Errores controlados del dominio Content Enricher.

Toda la capa de presentación (``src/main.py``) captura únicamente
``ContentEnricherError`` y los errores de red/artículo heredados del scraper
(``ConnectionError`` y ``ValueError``). Así un fallo nunca se oculta en
silencio y siempre llega al usuario con un mensaje accionable.
"""


class ContentEnricherError(Exception):
    """Base de todos los errores controlados del sistema."""


class ServicioNoDisponibleError(ContentEnricherError):
    """Falta una dependencia: la IA o el traductor no están inyectados."""


class AiError(ContentEnricherError):
    """La llamada a la API de inteligencia artificial falló."""


class TranslationError(ContentEnricherError):
    """La llamada a la API de traducción falló."""
