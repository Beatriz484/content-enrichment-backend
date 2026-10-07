"""Errores controlados del servicio de traducción.

Todos heredan de ``TranslationServiceError``. Así quien use el servicio puede
capturar un solo tipo de error y enseñar el mensaje al usuario sin traceback.
"""
from .errors import ServiceUnavailableError

class TranslationServiceError(ServiceUnavailableError):
    """Base de todos los errores del servicio de traducción."""


class InvalidLanguageError(TranslationServiceError):
    """El idioma escrito por el usuario no es válido."""


class EmptyTextError(TranslationServiceError):
    """No hay texto que traducir."""


class RateLimitError(TranslationServiceError):
    """MyMemory rechaza la petición por exceso de uso (límite de peticiones)."""


class TranslationTimeoutError(TranslationServiceError):
    """MyMemory tardó demasiado en responder."""


class NoConnectionError(TranslationServiceError):
    """No se pudo conectar con MyMemory."""


class TextTooLongError(TranslationServiceError):
    """Un trozo supera el límite de caracteres de MyMemory."""
