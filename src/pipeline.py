"""Orquestador del flujo Content Enricher.

Coordina los módulos del sistema (scraper, IA y traductor) y prepara el
diccionario ``content_data`` que consume el exportador. La capa de UI
(``src/main.py``) solo muestra resultados y pide decisiones al usuario.
"""
import logging
from typing import Any, Dict, Optional

from .scraper import WikipediaScraper

logger = logging.getLogger(__name__)


class ContentPipeline:
    """Encadena investigar → enriquecer → resumir → traducir."""

    def __init__(self, enricher: Optional[Any] = None, translator: Optional[Any] = None):
        """
        Args:
            enricher: Objeto con ``enrich_content(text)`` y ``summarize_content(text)``.
                ``None`` cuando no hay API key de IA (degradación elegante).
            translator: Objeto con ``translate(text, target_language) -> str``.
                ``None`` mientras el módulo ``src/translator.py`` está en desarrollo.
        """
        self.enricher = enricher
        self.translator = translator

    # 1. Investigación -------------------------------------------------
    def investigar(self, tema: str) -> Dict[str, Any]:
        """Extrae título y primeros párrafos de Wikipedia.

        Returns:
            ``{"titulo": str, "parrafos": list[str], "texto": str}``

        Raises:
            ValueError: El artículo no existe.
            ConnectionError: Fallo de conexión con Wikipedia.
        """
        try:
            scraper = WikipediaScraper(tema)
            resultado = scraper.extraer_contenido()
        except (ValueError, ConnectionError) as error:
            logger.error("Wikipedia: %s", error)
            raise

        parrafos = resultado["parrafos"]
        logger.info(
            "Wikipedia: extraídos %s párrafos de '%s'.",
            len(parrafos),
            resultado["titulo"],
        )
        return {
            "titulo": resultado["titulo"],
            "parrafos": parrafos,
            "texto": "\n\n".join(parrafos),
        }

    # 2. Enriquecimiento ----------------------------------------------
    def enriquecer(self, texto: str) -> str:
        """Amplía el contenido con IA. Sin IA disponible devuelve el original."""
        if self.enricher is None:
            logger.warning("IA no disponible: se conserva el contenido original.")
            return texto

        enriquecido = self.enricher.enrich_content(texto)
        logger.info("IA: contenido enriquecido generado.")
        return enriquecido

    # 3. Resumen -------------------------------------------------------
    def resumir(self, texto: str) -> str:
        """Genera un resumen con IA. Devuelve '' si no hay IA disponible."""
        if self.enricher is None:
            logger.warning("IA no disponible: no se generará resumen.")
            return ""

        resumen = self.enricher.summarize_content(texto)
        logger.info("IA: resumen generado.")
        return resumen

    # 4. Traducción ----------------------------------------------------
    def traducir(self, texto: str, idioma: str) -> str:
        """Traduce al idioma indicado.

        Devuelve ``''`` si el traductor aún no está disponible o falla, para
        no bloquear el resto del flujo (degradación elegante).
        """
        if self.translator is None:
            logger.warning(
                "Traducción pendiente: el módulo 'src/translator.py' aún no está disponible."
            )
            return ""

        try:
            traducido = self.translator.translate(texto, idioma)
        except Exception as error:  # noqa: BLE001 - el traductor decide sus errores
            logger.error("Traducción fallida al idioma '%s': %s", idioma, error)
            return ""

        logger.info("Traducción al idioma '%s' completada.", idioma)
        return traducido

    # Contrato del exportador ------------------------------------------
    @staticmethod
    def construir_content_data(
        titulo: str,
        texto_original: str,
        texto_enriquecido: str,
        texto_traducido: str = "",
        resumen: str = "",
    ) -> Dict[str, Any]:
        """Construye el ``content_data`` que consumen TxtExporter y PdfExporter.

        Incluye la bandera ``enriched_with_ai``: la IA se consideró activa si
        ``enriched_text`` difiere de ``raw_text``, de modo que los exportadores
        pongan un título coherente en la sección 2.

        ``summary`` es opcional: si viene vacío, los exportadores omiten la
        sección 4 del informe.
        """
        return {
            "topic": titulo,
            "raw_text": texto_original,
            "enriched_text": texto_enriquecido,
            "translated_text": texto_traducido,
            "summary": resumen,
            "enriched_with_ai": texto_enriquecido != texto_original,
        }
