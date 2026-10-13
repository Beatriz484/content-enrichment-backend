from .errors import ServiceUnavailableError

class TranslationServiceError(ServiceUnavailableError):
    pass


class InvalidLanguageError(TranslationServiceError):
    pass


class EmptyTextError(TranslationServiceError):
    pass


class RateLimitError(TranslationServiceError):
    pass


class TranslationTimeoutError(TranslationServiceError):
    pass


class NoConnectionError(TranslationServiceError):
    pass


class TextTooLongError(TranslationServiceError):
    pass
