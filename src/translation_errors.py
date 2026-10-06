"""Errores controlados del servicio de traducción.

Todos heredan de ``TranslationServiceError``. Así quien use el servicio puede
capturar un solo tipo de error y enseñar el mensaje al usuario sin traceback.
"""


class TranslationServiceError(Exception):
    """Base de todos los errores del servicio de traducción."""


class InvalidLanguageError(TranslationServiceError):
    """El idioma escrito por el usuario no es válido."""
