"""Traducción de contenido (HU-04).

Módulo **aún no implementado** por el equipo. Aquí se fija el contrato que la
pipeline ya espera, de modo que cuando se integre la API de DeepTranslate solo
haya que entregar la clase a ``ContentPipeline(translator=...)`` sin tocar ni
la matriz de control ni la CLI.

Contrato:

    translate(text: str, target_language: str) -> str
"""
from .errors import ServicioNoDisponibleError


class DeepTranslateTranslator:
    """Traductor con la interfaz acordada. Implementación pendiente."""

    def translate(self, text: str, target_language: str) -> str:
        """Traduce ``text`` al idioma ``target_language``.

        Raises:
            ServicioNoDisponibleError: mientras la integración con DeepTranslate
                no esté entregada. Nunca devuelve una cadena vacía en silencio.
        """
        raise ServicioNoDisponibleError(
            "El módulo de traducción (DeepTranslate) aún no está implementado."
        )
