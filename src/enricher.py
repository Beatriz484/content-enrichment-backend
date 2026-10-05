import logging
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Los handlers (consola + archivo logs/app.log) se configuran de forma global
# en src.logging_config.setup_logging(), que invoca src.main al arrancar.
logger = logging.getLogger(__name__)


class AiContentEnricher:
    """Service responsible for enriching and summarizing text using AI completions."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        """Initialize the OpenAI-compatible client validating credentials."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")

        if not self.api_key:
            raise ValueError(
                "API key not found. Ensure it is configured in .env or passed to constructor."
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def _is_valid_text(self, text: str | None) -> bool:
        """Check whether input text contains non-empty string content."""
        if not text or not isinstance(text, str):
            return False
        return bool(text.strip())

    def _adjust_length(self, text: str, max_characters: int = 10000) -> str:
        """Truncate text safely if it exceeds max allowed character length."""
        if len(text) > max_characters:
            return text[:max_characters].strip()
        return text

    def enrich_content(self, text: str, model: str = "qwen/qwen3.8-27b") -> str:
        """Enrich given content using AI models."""
        if not self._is_valid_text(text):
            logger.warning("Memoria vacía")
            return text

        prepared_text = self._adjust_length(text)

        system_prompt = (
            "Eres un asistente educativo especializado en investigación y síntesis académica. "
            "Tu tarea es enriquecer el contenido proporcionado: amplía los conceptos clave, "
            "añade contexto histórico o técnico relevante y organiza la información con claridad, "
            "manteniendo un tono didáctico, riguroso y estructurado."
        )

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Contenido a enriquecer:\n\n{prepared_text}"},
                ],
                temperature=0.7,
                max_tokens=4096,  # Permite que desarrolle el texto entero sin cortarse
            )
            enriched_content = response.choices[0].message.content
            if enriched_content:
                logger.info("IA respondió con éxito")
                return enriched_content.strip()

            logger.warning("IA no disponible")
            return text
        except Exception as e:
            logger.warning(f"IA no disponible: {e}")
            return text

    def summarize_content(self, text: str, model: str = "qwen/qwen3.8-27b") -> str:
        """Generate structured educational summary from input text."""
        if not self._is_valid_text(text):
            logger.warning("Memoria vacía")
            return text

        prepared_text = self._adjust_length(text)

        system_prompt = (
            "Eres un asistente educativo especializado en síntesis de información. "
            "Tu tarea es generar un resumen conciso y estructurado del contenido proporcionado, "
            "destacando los puntos principales, definiciones clave y conclusiones esenciales."
        )

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Contenido a resumir:\n\n{prepared_text}"},
                ],
                temperature=0.5,
                max_tokens=1500,
            )
            summary_content = response.choices[0].message.content
            if summary_content:
                logger.info("IA respondió con éxito")
                return summary_content.strip()

            logger.warning("IA no disponible")
            return text
        except Exception as e:
            logger.warning(f"IA no disponible: {e}")
            return text