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

NOMBRE_FUENTE = "ContentEnricherUnicode"

# Rutas habituales de una TTF con cobertura Unicode completa.
FUENTES_CANDIDATAS = (
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
_CODIGOS_PERMITIDOS: Set[int] = (
    {0x0A}  # salto de línea
    | set(range(0x20, 0x7F))  # ASCII imprimible
    | set(range(0xA0, 0x100))  # Latin-1 supplement
    | set(map(ord, "ŒœŠšŽžŸ–—‘’‚“”„†‡•…‰‹›ƒˆ˜€™"))
)


@lru_cache(maxsize=1)
def _buscar_fuente_unicode() -> Optional[str]:
    """Registra la primera TTF Unicode disponible y devuelve su nombre.

    El resultado se memoriza: registrar la misma fuente dos veces es inútil y
    los tests pueden limpiar la caché con ``_buscar_fuente_unicode.cache_clear()``.
    """
    for ruta in FUENTES_CANDIDATAS:
        if not os.path.isfile(ruta):
            continue
        try:
            pdfmetrics.registerFont(TTFont(NOMBRE_FUENTE, ruta))
        except Exception as error:  # noqa: BLE001 - una fuente corrupta no debe tumbar el informe
            logger.warning("Fuente descartada '%s': %s", ruta, error)
            continue
        logger.info("Fuente Unicode registrada para PDF: %s", ruta)
        return NOMBRE_FUENTE
    return None


def fuente_unicode() -> Optional[str]:
    """Nombre de la fuente Unicode registrada, o ``None`` si no hay ninguna."""
    return _buscar_fuente_unicode()


def limpiar(texto: str) -> str:
    """Normaliza el texto extraído: espacios duros, saltos y espacios repetidos."""
    sin_espacios_duros = str(texto).replace("\xa0", " ").replace("\r\n", "\n")
    return re.sub(r"[ \t]+", " ", sin_espacios_duros).strip()


def sanear(texto: str) -> str:
    """Deja el texto dentro del repertorio WinAnsi (fallback sin TTF Unicode).

    Descompone los caracteres acentuados (``ĭ`` → ``i`` + acento), descarta los
    diacríticos y los símbolos que Helvetica no sabe dibujar y recoloca los
    espacios que queden sueltos.
    """
    descompuesto = unicodedata.normalize("NFD", texto)
    sin_diacriticos = "".join(
        caracter for caracter in descompuesto if not unicodedata.combining(caracter)
    )
    filtrado = "".join(
        caracter for caracter in sin_diacriticos if ord(caracter) in _CODIGOS_PERMITIDOS
    )
    return re.sub(r" +", " ", filtrado).strip()


def preparar(texto: str) -> str:
    """Prepara texto libre de Wikipedia para ser interpretado por ``Paragraph``.

    Limpia, escapa el XML (``<...>`` y ``&``) y, si no hay fuente Unicode
    registrada, sana los caracteres que Helvetica no podría dibujar.
    """
    limpio = limpiar(texto)
    if fuente_unicode() is None:
        limpio = sanear(limpio)
    return escape(limpio).replace("\n", "<br/>")
