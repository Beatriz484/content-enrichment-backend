"""Tipografía y preparación de texto para la generación de PDF.

Problema que resuelve este módulo
---------------------------------
Helvetica (codificación WinAnsi) **no cubre** todos los caracteres que aparecen
en Wikipedia: ``ĭ``, ``ē``, ``²``, emojis... Cuando ReportLab no localiza el
glyph, cambia automáticamente a la fuente de respaldo ``ZapfDingbats`` (una
tipografía de símbolos) y el texto se dibuja ilegible: es el origen de los
"caracteres en negro/no reconocidos" del informe.

Estrategia en dos pasos:

1. Registrar una TTF Unicode del sistema si existe en alguna ruta conocida.
2. Si no hay ninguna, normalizar el texto para dejarlo dentro del repertorio
   WinAnsi (``ĭ`` → ``i``, ``ē`` → ``e``), en lugar de romper la generación.

Además escapa el texto como XML: ``Paragraph`` interpreta ``<...>`` como
etiquetas de marcado y *se come* el contenido si no se escapa antes.
"""
import logging
import os
import re
import unicodedata
from functools import lru_cache
from typing import Optional, Set
from xml.sax.saxutils import escape

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

FONT_NAME = "ContentEnricherUnicode"

# Rutas habituales de una TTF con cobertura Unicode completa.
CANDIDATE_FONT_PATHS = (
    # Windows
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\calibri.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    # macOS
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
)

# Repertorio WinAnsi que Helvetica sí sabe dibujar (se usa como fallback).
_ALLOWED_CODEPOINTS: Set[int] = (
    {0x0A}  # salto de línea
    | set(range(0x20, 0x7F))  # ASCII imprimible
    | set(range(0xA0, 0x100))  # Latin-1 supplement
    | set(map(ord, "ŒœŠšŽžŸ–—‘’‚“”„†‡•…‰‹›ƒˆ˜€™"))
)


@lru_cache(maxsize=1)
def _find_unicode_font() -> Optional[str]:
    """Registra la primera TTF Unicode disponible y devuelve su nombre.

    El resultado se memoriza: registrar la misma fuente dos veces es inútil y
    los tests pueden limpiar la caché con ``_find_unicode_font.cache_clear()``.
    """
    for path in CANDIDATE_FONT_PATHS:
        if not os.path.isfile(path):
            continue
        try:
            pdfmetrics.registerFont(TTFont(FONT_NAME, path))
        except Exception as error:  # noqa: BLE001 - una fuente corrupta no debe tumbar el informe
            logger.warning("Fuente descartada '%s': %s", path, error)
            continue
        logger.info("Fuente Unicode registrada para PDF: %s", path)
        return FONT_NAME
    return None


def unicode_font() -> Optional[str]:
    """Nombre de la fuente Unicode registrada, o ``None`` si no hay ninguna."""
    return _find_unicode_font()


def clean_text(text: str) -> str:
    """Normaliza el texto extraído: espacios duros, saltos y espacios repetidos."""
    text_without_hard_spaces = str(text).replace("\xa0", " ").replace("\r\n", "\n")
    return re.sub(r"[ \t]+", " ", text_without_hard_spaces).strip()


def sanitize_text(text: str) -> str:
    """Deja el texto dentro del repertorio WinAnsi (fallback sin TTF Unicode).

    Descompone los caracteres acentuados (``ĭ`` → ``i`` + acento), descarta los
    diacríticos y los símbolos que Helvetica no sabe dibujar y recoloca los
    espacios que queden sueltos.
    """
    decomposed = unicodedata.normalize("NFD", text)
    without_diacritics = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    filtered = "".join(
        char for char in without_diacritics if ord(char) in _ALLOWED_CODEPOINTS
    )
    return re.sub(r" +", " ", filtered).strip()


def prepare_text(text: str) -> str:
    """Prepara texto libre de Wikipedia para ser interpretado por ``Paragraph``.

    Limpia, escapa el XML (``<...>`` y ``&``) y, si no hay fuente Unicode
    registrada, sana los caracteres que Helvetica no podría dibujar.
    """
    cleaned = clean_text(text)
    if unicode_font() is None:
        cleaned = sanitize_text(cleaned)
    return escape(cleaned).replace("\n", "<br/>")
