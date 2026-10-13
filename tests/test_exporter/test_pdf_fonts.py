r"""Feature: Unicode font handling for the PDF

  As a Content Enricher user
  I want the report rendered with a font that covers the characters of the text
  So that accents, symbols and exotic characters are never silently dropped
"""

import pytest

from src.exporter import pdf_fonts


@pytest.fixture(autouse=True)
def _clean_cache():
    pdf_fonts._find_unicode_font.cache_clear()
    yield
    pdf_fonts._find_unicode_font.cache_clear()


def test_returns_none_when_no_ttf_is_available(monkeypatch):
    r"""@failure

    Scenario: Report that no usable TrueType font was found
        Given no candidate font file exists on disk
        When I ask for the Unicode font
        Then no font is returned
    """
    monkeypatch.setattr(pdf_fonts, "CANDIDATE_FONT_PATHS", ("/ruta/que/no/existe.ttf",))

    assert pdf_fonts.unicode_font() is None


def test_registers_the_first_available_font(monkeypatch):
    r"""@successful

    Scenario: Register the first font that can be loaded
        Given a candidate font file that exists and loads correctly
        When I ask for the Unicode font
        Then the font is registered
        And the agreed font name is returned
    """
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
    r"""@failure

    Scenario: Discard a corrupt font without breaking the report
        Given a candidate font file that raises while it is being read
        When I ask for the Unicode font
        Then no font is returned
        And the process keeps running
    """
    monkeypatch.setattr(pdf_fonts, "CANDIDATE_FONT_PATHS", ("mala.ttf",))
    monkeypatch.setattr(pdf_fonts.os.path, "isfile", lambda path: True)

    def _raise(*args, **kwargs):
        raise ValueError("archivo corrupto")

    monkeypatch.setattr(pdf_fonts, "TTFont", _raise)

    assert pdf_fonts.unicode_font() is None


def test_font_lookup_is_cached(monkeypatch):
    r"""@successful

    Scenario: Look the font up only once
        Given a candidate font file that exists and loads correctly
        When I ask for the Unicode font twice
        Then the file system is only consulted once
    """
    calls = []
    monkeypatch.setattr(pdf_fonts, "CANDIDATE_FONT_PATHS", ("buena.ttf",))
    monkeypatch.setattr(pdf_fonts.os.path, "isfile", lambda path: calls.append(path) or True)
    monkeypatch.setattr(pdf_fonts, "TTFont", lambda *args, **kwargs: object())
    monkeypatch.setattr(pdf_fonts.pdfmetrics, "registerFont", lambda font: None)

    pdf_fonts.unicode_font()
    pdf_fonts.unicode_font()

    assert calls == ["buena.ttf"]


def test_clean_text_normalizes_real_text():
    r"""@successful

    Scenario: Normalise the stray spacing of a real article
        Given the text "Camas tiene 11,66\xa0km²  y  espacios."
        When I clean the text
        Then I get the text "Camas tiene 11,66 km² y espacios."
    """
    text = "Camas tiene 11,66\xa0km²  y  espacios."
    assert pdf_fonts.clean_text(text) == "Camas tiene 11,66 km² y espacios."


def test_clean_text_normalizes_windows_line_breaks():
    r"""@successful

    Scenario: Turn Windows line breaks into plain line breaks
        Given the text "uno\r\ndos"
        When I clean the text
        Then I get the text "uno\ndos"
    """
    assert pdf_fonts.clean_text("uno\r\ndos") == "uno\ndos"


def test_sanitize_text_removes_what_helvetica_cannot_draw():
    r"""@successful

    Scenario: Keep only what Helvetica is able to draw when no Unicode font exists
        Given the text "mulĭer -ēris 🟢 km² — «texto»"
        When I sanitise the text for the PDF
        Then the diacritics are flattened to plain letters
        And the emoji is removed
        And the symbols, the dash and the guillemets are kept
        And no double space is left behind
    """
    sanitized = pdf_fonts.sanitize_text("mulĭer -ēris 🟢 km² — «texto»")

    assert "mulier" in sanitized
    assert "-eris" in sanitized
    assert "\U0001F7E2" not in sanitized
    assert "km²" in sanitized
    assert "—" in sanitized
    assert "«texto»" in sanitized
    assert "  " not in sanitized


def test_prepare_text_escapes_xml_so_it_is_not_eaten(monkeypatch):
    r"""@successful

    Scenario: Escape the XML characters so they are not eaten by the PDF
        Given no Unicode font is available
        And the text "5 < 10 y & <b>tag</b>"
        When I prepare the text for the PDF
        Then I get the text "5 &lt; 10 y &amp; &lt;b&gt;tag&lt;/b&gt;"
    """
    monkeypatch.setattr(pdf_fonts, "unicode_font", lambda: None)

    assert pdf_fonts.prepare_text("5 < 10 y & <b>tag</b>") == (
        "5 &lt; 10 y &amp; &lt;b&gt;tag&lt;/b&gt;"
    )


def test_prepare_text_converts_line_breaks_into_line_tags(monkeypatch):
    r"""@successful

    Scenario: Convert line breaks into line tags
        Given the Unicode font "MiFuente"
        And the text "párrafo uno\npárrafo dos"
        When I prepare the text for the PDF
        Then I get the text "párrafo uno<br/>párrafo dos"
    """
    monkeypatch.setattr(pdf_fonts, "unicode_font", lambda: "MiFuente")

    assert pdf_fonts.prepare_text("párrafo uno\npárrafo dos") == "párrafo uno<br/>párrafo dos"


def test_prepare_text_keeps_exotic_characters_when_unicode_font_exists(monkeypatch):
    r"""@successful

    Scenario: Keep the exotic characters when a Unicode font exists
        Given the Unicode font "MiFuente"
        And the text "del latín mulĭer, -ēris"
        When I prepare the text for the PDF
        Then I get the text "del latín mulĭer, -ēris"
    """
    monkeypatch.setattr(pdf_fonts, "unicode_font", lambda: "MiFuente")

    assert pdf_fonts.prepare_text("del latín mulĭer, -ēris") == "del latín mulĭer, -ēris"
