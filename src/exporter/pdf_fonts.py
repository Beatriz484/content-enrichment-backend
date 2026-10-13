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

CANDIDATE_FONT_PATHS = (
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\calibri.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
)

_ALLOWED_CODEPOINTS: Set[int] = (
    {0x0A}
    | set(range(0x20, 0x7F))
    | set(range(0xA0, 0x100))
    | set(map(ord, "ŒœŠšŽžŸ–—‘’‚“”„†‡•…‰‹›ƒˆ˜€™"))
)


@lru_cache(maxsize=1)
def _find_unicode_font() -> Optional[str]:
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
    return _find_unicode_font()


def clean_text(text: str) -> str:
    text_without_hard_spaces = str(text).replace("\xa0", " ").replace("\r\n", "\n")
    return re.sub(r"[ \t]+", " ", text_without_hard_spaces).strip()


def sanitize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    without_diacritics = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    filtered = "".join(
        char for char in without_diacritics if ord(char) in _ALLOWED_CODEPOINTS
    )
    return re.sub(r" +", " ", filtered).strip()


def prepare_text(text: str) -> str:
    cleaned = clean_text(text)
    if unicode_font() is None:
        cleaned = sanitize_text(cleaned)
    return escape(cleaned).replace("\n", "<br/>")
