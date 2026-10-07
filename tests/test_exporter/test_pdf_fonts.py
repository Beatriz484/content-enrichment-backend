"""Tests de la tipografía y la preparación de texto del PDF."""
import pytest

from src.exporter import pdf_fonts


@pytest.fixture(autouse=True)
def _clean_cache():
    """Cada test decide si 'hay' fuente Unicode: se limpia la caché antes y después."""
    pdf_fonts._find_unicode_font.cache_clear()
    yield
    pdf_fonts._find_unicode_font.cache_clear()


# --- Resolución de fuente ---------------------------------------------------

def test_returns_none_when_no_ttf_is_available(monkeypatch):
    """Sin fuente Unicode el sistema cae en el modo de normalización."""
    monkeypatch.setattr(pdf_fonts, "CANDIDATE_FONT_PATHS", ("/ruta/que/no/existe.ttf",))

    assert pdf_fonts.unicode_font() is None


def test_registers_the_first_available_font(monkeypatch):
    """Se registra la primera TTF del sistema que se encuentra."""
    monkeypatch.setattr(pdf_fonts, "CANDIDATE_FONT_PATHS", ("buena.ttf",))
    monkeypatch.setattr(pdf_fonts.os.path, "isfile", lambda path: True)
    monkeypatch.setattr(pdf_fonts, "TTFont", lambda *args, **kwargs: object())
    registered = {}
    monkeypatch.setattr(
        pdf_fonts.pdfmetrics, "registerFont", lambda font: registered.setdefault("ok", font)
    )

    assert pdf_fonts.unicode_font() == pdf_fonts.FONT_NAME
    assert "ok" in registered


def test_a_broken_font_does_not_break_the_process(monkeypatch):
    """Si la TTF no se puede cargar se descarta y se sigue buscando."""
    monkeypatch.setattr(pdf_fonts, "CANDIDATE_FONT_PATHS", ("mala.ttf",))
    monkeypatch.setattr(pdf_fonts.os.path, "isfile", lambda path: True)

    def _raise(*args, **kwargs):
        raise ValueError("archivo corrupto")

    monkeypatch.setattr(pdf_fonts, "TTFont", _raise)

    assert pdf_fonts.unicode_font() is None


def test_font_lookup_is_cached(monkeypatch):
    """La búsqueda se hace una sola vez por proceso."""
    calls = []
    monkeypatch.setattr(pdf_fonts, "CANDIDATE_FONT_PATHS", ("buena.ttf",))
    monkeypatch.setattr(pdf_fonts.os.path, "isfile", lambda path: calls.append(path) or True)
    monkeypatch.setattr(pdf_fonts, "TTFont", lambda *args, **kwargs: object())
    monkeypatch.setattr(pdf_fonts.pdfmetrics, "registerFont", lambda font: None)

    pdf_fonts.unicode_font()
    pdf_fonts.unicode_font()

    assert calls == ["buena.ttf"]


# --- Limpieza y saneado ------------------------------------------------------

def test_clean_text_normalizes_real_text():
    text = "Camas tiene 11,66\xa0km²  y  espacios."
    assert pdf_fonts.clean_text(text) == "Camas tiene 11,66 km² y espacios."


def test_clean_text_normalizes_windows_line_breaks():
    assert pdf_fonts.clean_text("uno\r\ndos") == "uno\ndos"


def test_sanitize_text_removes_what_helvetica_cannot_draw():
    """Los diacríticos exóticos se reducen a su letra base y el emoji desaparece."""
    sanitized = pdf_fonts.sanitize_text("mulĭer -ēris 🟢 km² — «texto»")

    assert "mulier" in sanitized
    assert "-eris" in sanitized
    assert "\U0001F7E2" not in sanitized
    # WinAnsi sí dibuja superíndices, rayas y comillas angulares
    assert "km²" in sanitized
    assert "—" in sanitized
    assert "«texto»" in sanitized
    # El hueco que deja el emoji no se queda duplicado
    assert "  " not in sanitized


# --- Preparación final -------------------------------------------------------

def test_prepare_text_escapes_xml_so_it_is_not_eaten(monkeypatch):
    """Regression: <tag> desaparecía del PDF porque Paragraph lo leía como etiqueta."""
    monkeypatch.setattr(pdf_fonts, "unicode_font", lambda: None)

    assert pdf_fonts.prepare_text("5 < 10 y & <b>tag</b>") == (
        "5 &lt; 10 y &amp; &lt;b&gt;tag&lt;/b&gt;"
    )


def test_prepare_text_converts_line_breaks_into_line_tags(monkeypatch):
    monkeypatch.setattr(pdf_fonts, "unicode_font", lambda: "MiFuente")

    assert pdf_fonts.prepare_text("párrafo uno\npárrafo dos") == "párrafo uno<br/>párrafo dos"


def test_prepare_text_keeps_exotic_characters_when_unicode_font_exists(monkeypatch):
    """Con TTF registrada no se toca el texto: es la solución al bug de ZapfDingbats."""
    monkeypatch.setattr(pdf_fonts, "unicode_font", lambda: "MiFuente")

    assert pdf_fonts.prepare_text("del latín mulĭer, -ēris") == "del latín mulĭer, -ēris"
