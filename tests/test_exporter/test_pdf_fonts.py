"""Tests de la tipografía y la preparación de texto del PDF."""
import pytest

from src.exporter import pdf_fonts


@pytest.fixture(autouse=True)
def _cache_limpia():
    """Cada test decide si 'hay' fuente Unicode: se limpia la caché antes y después."""
    pdf_fonts._buscar_fuente_unicode.cache_clear()
    yield
    pdf_fonts._buscar_fuente_unicode.cache_clear()


# --- Resolución de fuente ---------------------------------------------------

def test_devuelve_none_cuando_no_hay_ninguna_ttf(monkeypatch):
    """Sin fuente Unicode el sistema cae en el modo de normalización."""
    monkeypatch.setattr(pdf_fonts, "FUENTES_CANDIDATAS", ("/ruta/que/no/existe.ttf",))

    assert pdf_fonts.fuente_unicode() is None


def test_registra_la_primera_fuente_disponible(monkeypatch):
    """Se registra la primera TTF del sistema que se encuentra."""
    monkeypatch.setattr(pdf_fonts, "FUENTES_CANDIDATAS", ("buena.ttf",))
    monkeypatch.setattr(pdf_fonts.os.path, "isfile", lambda ruta: True)
    monkeypatch.setattr(pdf_fonts, "TTFont", lambda *args, **kwargs: object())
    registrado = {}
    monkeypatch.setattr(
        pdf_fonts.pdfmetrics, "registerFont", lambda fuente: registrado.setdefault("ok", fuente)
    )

    assert pdf_fonts.fuente_unicode() == pdf_fonts.NOMBRE_FUENTE
    assert "ok" in registrado


def test_una_fuente_corrupta_no_tumba_el_proceso(monkeypatch):
    """Si la TTF no se puede cargar se descarta y se sigue buscando."""
    monkeypatch.setattr(pdf_fonts, "FUENTES_CANDIDATAS", ("mala.ttf",))
    monkeypatch.setattr(pdf_fonts.os.path, "isfile", lambda ruta: True)

    def _romper(*args, **kwargs):
        raise ValueError("archivo corrupto")

    monkeypatch.setattr(pdf_fonts, "TTFont", _romper)

    assert pdf_fonts.fuente_unicode() is None


def test_la_fuente_se_memoriza(monkeypatch):
    """La búsqueda se hace una sola vez por proceso."""
    llamadas = []
    monkeypatch.setattr(pdf_fonts, "FUENTES_CANDIDATAS", ("buena.ttf",))
    monkeypatch.setattr(pdf_fonts.os.path, "isfile", lambda ruta: llamadas.append(ruta) or True)
    monkeypatch.setattr(pdf_fonts, "TTFont", lambda *args, **kwargs: object())
    monkeypatch.setattr(pdf_fonts.pdfmetrics, "registerFont", lambda fuente: None)

    pdf_fonts.fuente_unicode()
    pdf_fonts.fuente_unicode()

    assert llamadas == ["buena.ttf"]


# --- Limpieza y saneado ------------------------------------------------------

def test_limpia_texto_real():
    texto = "Camas tiene 11,66\xa0km²  y  espacios."
    assert pdf_fonts.limpiar(texto) == "Camas tiene 11,66 km² y espacios."


def test_limpia_normaliza_salto_de_windows():
    assert pdf_fonts.limpiar("uno\r\ndos") == "uno\ndos"


def test_sanear_quita_los_caracteres_que_helvetica_no_dibuja():
    """Los diacríticos exóticos se reducen a su letra base y el emoji desaparece."""
    saneado = pdf_fonts.sanear("mulĭer -ēris 🟢 km² — «texto»")

    assert "mulier" in saneado
    assert "-eris" in saneado
    assert "\U0001F7E2" not in saneado
    # WinAnsi sí dibuja superíndices, rayas y comillas angulares
    assert "km²" in saneado
    assert "—" in saneado
    assert "«texto»" in saneado
    # El hueco que deja el emoji no se queda duplicado
    assert "  " not in saneado


# --- Preparación final -------------------------------------------------------

def test_preparar_escapa_el_xml_para_que_no_se_coma_el_texto(monkeypatch):
    """Regression: <tag> desaparecía del PDF porque Paragraph lo leía como etiqueta."""
    monkeypatch.setattr(pdf_fonts, "fuente_unicode", lambda: None)

    assert pdf_fonts.preparar("5 < 10 y & <b>tag</b>") == (
        "5 &lt; 10 y &amp; &lt;b&gt;tag&lt;/b&gt;"
    )


def test_preparar_convierte_saltos_en_etiquetas_de_linea(monkeypatch):
    monkeypatch.setattr(pdf_fonts, "fuente_unicode", lambda: "MiFuente")

    assert pdf_fonts.preparar("párrafo uno\npárrafo dos") == "párrafo uno<br/>párrafo dos"


def test_preparar_conserva_caracteres_exoticos_si_hay_fuente_unicode(monkeypatch):
    """Con TTF registrada no se toca el texto: es la solución al bug de ZapfDingbats."""
    monkeypatch.setattr(pdf_fonts, "fuente_unicode", lambda: "MiFuente")

    assert pdf_fonts.preparar("del latín mulĭer, -ēris") == "del latín mulĭer, -ēris"
