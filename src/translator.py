"""Servicio de traducción del Content Enricher.

Traduce el contenido enriquecido y el resumen al idioma elegido por el
usuario usando la librería ``deep_translator`` (clase ``MyMemoryTranslator``).

Responsabilidad única: este módulo solo traduce. No investiga, no enriquece
y no exporta.

Interfaz pública:

    translate(text: str, target_language: str) -> str
"""
import os

from deep_translator import MyMemoryTranslator
from dotenv import load_dotenv

from .language_validator import validate_language
from .text_splitter import MAX_CHARS_PER_CHUNK, split_text
from .translation_errors import EmptyTextError

# Carga las variables del archivo .env (si existe)
load_dotenv()

# Idioma de origen por defecto: el scraper lee de es.wikipedia.org
DEFAULT_SOURCE_LANGUAGE = "es-ES"


class DeepTranslateService:
    """Traduce textos con MyMemory a través de deep_translator."""

    def __init__(self, source_language=DEFAULT_SOURCE_LANGUAGE, email=None):
        """
        Args:
            source_language: Código del idioma de origen (por defecto "es-ES").
            email: Email opcional para MyMemory. Sube el límite diario de uso.
                Si no se pasa, se lee MYMEMORY_EMAIL del .env.
        """
        # Se valida también el origen: MyMemory no acepta "auto"
        self.source_language = validate_language(source_language)
        # Si no hay email, queda en None y MyMemory funciona igual
        self.email = email or os.getenv("MYMEMORY_EMAIL") or None

    def translate(self, text, target_language):
        """Traduce ``text`` al idioma ``target_language`` y devuelve el resultado.

        Se usa igual para el contenido enriquecido y para el resumen.

        Args:
            text: Texto a traducir. Puede ser largo: se trocea automáticamente.
            target_language: Nombre (español o inglés) o código del idioma.

        Raises:
            InvalidLanguageError: el idioma no es válido.
            EmptyTextError: el texto está vacío.
        """
        target_code = validate_language(target_language)
        if text is None or text.strip() == "":
            raise EmptyTextError("No hay ningún texto que traducir.")

        # Se traduce párrafo a párrafo para conservar los saltos de línea
        translated_paragraphs = []
        for paragraph in text.split("\n"):
            translated_chunks = []
            for chunk in split_text(paragraph, MAX_CHARS_PER_CHUNK):
                translated_chunks.append(self._call_mymemory(chunk, target_code))
            translated_paragraphs.append(" ".join(translated_chunks))

        return "\n".join(translated_paragraphs)

    def _call_mymemory(self, text, target_code):
        """Única llamada a la librería. Si cambia el proveedor, solo se toca aquí."""
        translator = MyMemoryTranslator(
            source=self.source_language,
            target=target_code,
            email=self.email,
        )
        return translator.translate(text)
