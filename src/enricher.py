"""Enriquecimiento y síntesis de texto con inteligencia artificial.

Un único punto de llamada a la API (``_completar``) del que derivan las dos
operaciones del sistema. Si la API falla se propaga ``AiError``: **nunca se
devuelve el texto original haciéndose pasar por contenido enriquecido**.
"""
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from .errors import AiError

load_dotenv()

# Los handlers (consola + archivo logs/app.log) se configuran de forma global
# en src.logging_config.setup_logging(), que invoca src.main al arrancar.
logger = logging.getLogger(__name__)

MODELO_POR_DEFECTO = os.getenv("AI_MODEL", "qwen/qwen3.8-27b")
MAX_CARACTERES = 10000

PROMPT_ENRIQUECER = (
    "Eres un asistente educativo especializado en investigación y síntesis académica. "
    "Tu tarea es enriquecer el contenido proporcionado: amplía los conceptos clave, "
    "añade contexto histórico o técnico relevante y organiza la información con claridad, "
    "manteniendo un tono didáctico, riguroso y estructurado."
)

PROMPT_RESUMIR = (
    "Eres un asistente educativo especializado en síntesis de información. "
    "Tu tarea es generar un resumen conciso y estructurado del contenido proporcionado, "
    "destacando los puntos principales, definiciones clave y conclusiones esenciales."
)


def texto_valido(text: Optional[str]) -> bool:
    """Indica si la cadena contiene contenido no vacío tras recortar espacios."""
    return bool(text) and isinstance(text, str) and bool(text.strip())


def ajustar_longitud(text: str, max_characters: int = MAX_CARACTERES) -> str:
    """Recorta la entrada de forma segura para no desbordar el contexto."""
    return text[:max_characters].strip() if len(text) > max_characters else text


class AiContentEnricher:
    """Cliente de una API compatible con OpenAI para enriquecer y resumir texto."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        """Inicializa el cliente validando las credenciales.

        Raises:
            ValueError: si no hay API key disponible.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")

        if not self.api_key:
            raise ValueError(
                "API key not found. Ensure it is configured in .env or passed to constructor."
            )

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.model = MODELO_POR_DEFECTO

    def _completar(self, instruccion: str, texto: str, max_tokens: int, temperatura: float) -> str:
        """Único punto de llamada a la API de chat completions.

        Raises:
            AiError: si la API responde vacía o lanza una excepción.
        """
        if not texto_valido(texto):
            raise AiError("No se puede procesar un texto vacío.")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": instruccion},
                    {"role": "user", "content": f"Contenido:\n\n{ajustar_longitud(texto)}"},
                ],
                temperature=temperatura,
                max_tokens=max_tokens,
            )
        except Exception as error:
            logger.error("Fallo en la API de IA: %s", error)
            raise AiError(f"No se pudo contactar con la API de IA: {error}") from error

        contenido = response.choices[0].message.content
        if not contenido:
            logger.error("La API de IA devolvió una respuesta vacía.")
            raise AiError("La API de IA devolvió una respuesta vacía.")

        logger.info("IA: respuesta generada (%s caracteres).", len(contenido))
        return contenido.strip()

    def enrich_content(self, text: str) -> str:
        """Amplía el contenido con IA añadiendo contexto y explicaciones."""
        return self._completar(PROMPT_ENRIQUECER, text, max_tokens=4096, temperatura=0.7)

    def summarize_content(self, text: str) -> str:
        """Genera una síntesis estructurada y concisa del contenido."""
        return self._completar(PROMPT_RESUMIR, text, max_tokens=1500, temperatura=0.5)
