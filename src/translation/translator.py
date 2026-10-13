import os

import requests
from deep_translator import MyMemoryTranslator
from deep_translator.exceptions import NotValidLength, RequestError, TooManyRequests
from dotenv import load_dotenv

from .language_validator import validate_language
from .text_splitter import MAX_CHARS_PER_CHUNK, split_text
from .translation_errors import (
    EmptyTextError,
    NoConnectionError,
    RateLimitError,
    TextTooLongError,
    TranslationTimeoutError,
)

load_dotenv()

DEFAULT_SOURCE_LANGUAGE = "es-ES"

QUOTA_WARNING = "MYMEMORY WARNING"


class DeepTranslateTranslator:

    def __init__(self, source_language=DEFAULT_SOURCE_LANGUAGE, email=None):
        self.source_language = validate_language(source_language)
        self.email = email or os.getenv("MYMEMORY_EMAIL") or None

    def translate(self, text, target_language):
        target_code = validate_language(target_language)
        if text is None or text.strip() == "":
            raise EmptyTextError("No hay ningún texto que traducir.")

        translated_paragraphs = []
        for paragraph in text.split("\n"):
            translated_chunks = []
            for chunk in split_text(paragraph, MAX_CHARS_PER_CHUNK):
                translated_chunks.append(self._translate_chunk(chunk, target_code))
            translated_paragraphs.append(" ".join(translated_chunks))

        return "\n".join(translated_paragraphs)

    def show_translation(self, translated_text, title="CONTENIDO TRADUCIDO"):
        print(f"=== {title} ===")
        print(f"{translated_text}\n")

    def _translate_chunk(self, chunk, target_code):
        try:
            translated = self._call_mymemory(chunk, target_code)
        except TooManyRequests:
            raise RateLimitError(
                "Se ha superado el límite de peticiones de MyMemory. "
                "Es una cuota diaria que se reinicia al día siguiente, no en "
                "minutos: inténtalo mañana o añade MYMEMORY_EMAIL en el "
                "archivo .env para subirla a 50.000 caracteres."
            )
        except requests.exceptions.Timeout:
            raise TranslationTimeoutError(
                "El servicio de traducción ha tardado demasiado en responder. "
                "Inténtalo de nuevo más tarde."
            )
        except (requests.exceptions.ConnectionError, RequestError):
            raise NoConnectionError(
                "No se ha podido conectar con el servicio de traducción. "
                "Revisa tu conexión a internet."
            )
        except NotValidLength:
            raise TextTooLongError(
                "El texto tiene un fragmento sin espacios demasiado largo para "
                "traducirlo (MyMemory admite menos de 500 caracteres por petición)."
            )

        if translated.startswith(QUOTA_WARNING):
            raise RateLimitError(
                "Se ha agotado la cuota diaria gratuita de MyMemory "
                "(5.000 caracteres sin email). Se reinicia al día siguiente: "
                "inténtalo mañana o añade MYMEMORY_EMAIL en el archivo .env "
                "para subirla a 50.000 caracteres."
            )
        return translated

    def _call_mymemory(self, text, target_code):
        translator = MyMemoryTranslator(
            source=self.source_language,
            target=target_code,
            email=self.email,
        )
        return translator.translate(text)
