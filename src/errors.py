"""Errores controlados del dominio Content Enricher.

``src/main.py`` captura estos errores y los traduce a un mensaje accionable en
la terminal. Los errores de red o de artículo heredados del scraper
(``ConnectionError`` y ``ValueError``) se tratan igual en esa capa de
presentación, de modo que un fallo nunca se oculta en silencio.
"""


class ContentEnricherError(Exception):
    """Base de todos los errores controlados del sistema."""


class ServiceUnavailableError(ContentEnricherError):
    """Falta una dependencia: la IA o el traductor no están inyectados."""


# ``src/translator.py`` (módulo entregado por el equipo y no modificado) sigue
# importando este error por su nombre en español: se mantiene como alias.
ServicioNoDisponibleError = ServiceUnavailableError
