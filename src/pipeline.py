import logging
from typing import Any, Dict, Optional

from .enricher import AiContentEnricher
from .scraper import WikipediaScraper
from .translation import DeepTranslateTranslator

logger = logging.getLogger(__name__)


def research_topic(topic: str) -> Dict[str, Any]:
    try:
        result = WikipediaScraper(topic).extract_content()
    except (ValueError, ConnectionError) as error:
        logger.error("Wikipedia: %s", error)
        raise

    paragraphs = result["paragraphs"]
    logger.info(
        "Wikipedia: extraídos %s párrafos de '%s'.",
        len(paragraphs),
        result["title"],
    )
    return {
        "title": result["title"],
        "paragraphs": paragraphs,
        "text": "\n\n".join(paragraphs),
    }


def enrich_content(enricher: AiContentEnricher, text: str) -> str:
    enriched = enricher.enrich_content(text)
    logger.info("IA: contenido enriquecido generado.")
    return enriched


def summarize_content(enricher: AiContentEnricher, text: str) -> str:
    summary = enricher.summarize_content(text)
    logger.info("IA: resumen generado.")
    return summary


def translate_content(
    translator: DeepTranslateTranslator,
    text: str,
    language: str,
) -> str:
    translated = translator.translate(text, language)
    logger.info("Traducción al idioma '%s' completada.", language)
    return translated


def _create_enricher() -> Optional[AiContentEnricher]:
    try:
        return AiContentEnricher()
    except ValueError as error:
        logger.warning("IA no disponible: %s", error)
        print(f"⚠️  IA no disponible: {error}")
        print("   El flujo continuará solo con el texto original.")
        return None
