"""Orquestador del flujo Content Enricher.

Coordina los módulos del sistema (scraper, IA y traductor) y aplica la matriz
de control: ``base → (resumen) → (traducción)``. Ese orden es el único que la
CLI y el exportador necesitan conocer.

La capa de UI (``src/prompts.py`` y ``src/main.py``) solo muestra resultados y
pide decisiones al usuario.
"""
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .errors import ServicioNoDisponibleError
from .options import ContentMode, OutputOptions
from .scraper import WikipediaScraper

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Resultado:
    """Salida del procesamiento.

    Attributes:
        topic: Título real del artículo de Wikipedia.
        body: **La variante pedida**. Es lo único que se escribe en el archivo.
        original: Texto extraído de Wikipedia, para mostrarlo en la terminal.
        enriquecido: Texto ampliado por IA (vacío si el modo no lo pidió).
        resumen: Síntesis (vacía si no se pidió).
        traducido: Traducción (vacía si no se pidió).
        variante: Rótulo de la variante resuelta, para informar al usuario.
    """

    topic: str
    body: str
    original: str
    enriquecido: str = ""
    resumen: str = ""
    traducido: str = ""
    variante: str = ""

    @property
    def informe(self) -> Dict[str, Any]:
        """Contrato mínimo que consume el exportador: título + variante."""
        return {"topic": self.topic, "body": self.body}

    @property
    def pasos(self) -> List[Tuple[str, str]]:
        """Pares (rótulo, texto) que la CLI imprime en pantalla."""
        mostrar: List[Tuple[str, str]] = [("CONTENIDO ORIGINAL", self.original)]
        if self.enriquecido:
            mostrar.append(("CONTENIDO ENRIQUECIDO (IA)", self.enriquecido))
        if self.resumen:
            mostrar.append(("RESUMEN (IA)", self.resumen))
        if self.traducido:
            mostrar.append(("CONTENIDO TRADUCIDO", self.traducido))
        return mostrar


class ContentPipeline:
    """Encadena investigar → enriquecer → resumir → traducir."""

    def __init__(self, enricher: Optional[Any] = None, translator: Optional[Any] = None):
        """
        Args:
            enricher: Objeto con ``enrich_content(text)`` y ``summarize_content(text)``.
                ``None`` cuando no hay API key de IA.
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
            resultado = scraper.extract_content()
        except (ValueError, ConnectionError) as error:
            logger.error("Wikipedia: %s", error)
            raise

        parrafos = resultado["paragraphs"]
        logger.info(
            "Wikipedia: extraídos %s párrafos de '%s'.",
            len(parrafos),
            resultado["title"],
        )
        return {
            "titulo": resultado["title"],
            "parrafos": parrafos,
            "texto": "\n\n".join(parrafos),
        }

    # 2. Enriquecimiento ----------------------------------------------
    def enriquecer(self, texto: str) -> str:
        """Amplía el contenido con IA.

        Raises:
            ServicioNoDisponibleError: no hay enriquecedor inyectado.
        """
        if self.enricher is None:
            raise ServicioNoDisponibleError(
                "El servicio de IA no está disponible: falta OPENAI_API_KEY."
            )
        enriquecido = self.enricher.enrich_content(texto)
        logger.info("IA: contenido enriquecido generado.")
        return enriquecido

    # 3. Resumen -------------------------------------------------------
    def resumir(self, texto: str) -> str:
        """Genera una síntesis del texto con IA.

        Raises:
            ServicioNoDisponibleError: no hay enriquecedor inyectado.
        """
        if self.enricher is None:
            raise ServicioNoDisponibleError(
                "El servicio de IA no está disponible: falta OPENAI_API_KEY."
            )
        resumen = self.enricher.summarize_content(texto)
        logger.info("IA: resumen generado.")
        return resumen

    # 4. Traducción ----------------------------------------------------
    def traducir(self, texto: str, idioma: str) -> str:
        """Traduce al idioma indicado.

        Raises:
            ServicioNoDisponibleError: no hay traductor inyectado.
            TranslationError: la API de traducción falló.
        """
        if self.translator is None:
            raise ServicioNoDisponibleError(
                "El módulo de traducción no está disponible: "
                "src/translator.py aún no ha sido implementado."
            )
        traducido = self.translator.translate(texto, idioma)
        logger.info("Traducción al idioma '%s' completada.", idioma)
        return traducido

    # Matriz de control -------------------------------------------------
    def procesar(self, investigacion: Dict[str, Any], opciones: OutputOptions) -> Resultado:
        """Aplica la variante elegida y devuelve la salida exacta a mostrar/exportar.

        El orden es siempre el mismo:

            1. base      → texto original o enriquecido (eje A)
            2. resumen   → síntesis de la base, si se pidió (eje B)
            3. traducción→ aplicada al final sobre la variante, si se pidió

        Raises:
            ServicioNoDisponibleError: falta un servicio obligatorio.
            AiError / TranslationError: falló una llamada a una API externa.
        """
        original = investigacion["texto"]
        base = original
        enriquecido = ""

        if opciones.content_mode is ContentMode.ENRICHED:
            enriquecido = self.enriquecer(original)
            base = enriquecido

        resumen = self.resumir(base) if opciones.resumir else ""
        cuerpo = resumen if opciones.resumir else base

        traducido = self.traducir(cuerpo, opciones.idioma) if opciones.idioma else ""
        if opciones.idioma:
            cuerpo = traducido

        logger.info("Variante resuelta: '%s'.", opciones.variante.value)
        return Resultado(
            topic=investigacion["titulo"],
            body=cuerpo,
            original=original,
            enriquecido=enriquecido,
            resumen=resumen,
            traducido=traducido,
            variante=opciones.variante.value,
        )
