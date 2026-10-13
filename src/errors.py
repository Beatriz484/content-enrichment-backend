class ContentEnricherError(Exception):
    pass


class ServiceUnavailableError(ContentEnricherError):
    pass


ServicioNoDisponibleError = ServiceUnavailableError
