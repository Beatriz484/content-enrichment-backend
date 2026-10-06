"""Tests de la CLI (``src/main.py``) con todas las dependencias simuladas."""
from unittest.mock import MagicMock, patch

import pytest

from src.errors import ServicioNoDisponibleError
from src.main import (
    _create_enricher,
    _setup_console,
    ask_format,
    ask_sections,
    ask_text,
    compose_body,
    confirm,
    main,
    research_topic,
)

RESEARCH_RESULT = {
    "title": "Python",
    "paragraphs": ["Párrafo uno.", "Párrafo dos."],
}
FULL_TEXT = "Párrafo uno.\n\nPárrafo dos."

SECTIONS = [
    ("1", "Texto original", "original"),
    ("2", "Contenido enriquecido (IA)", "enriquecido"),
    ("3", "Resumen (IA)", "resumen"),
]


def _enricher_mock():
    enricher = MagicMock()
    enricher.enrich_content.return_value = "Contenido enriquecido por IA"
    enricher.summarize_content.return_value = "Resumen ejecutivo"
    return enricher


def run_cli(
    inputs,
    with_ai=True,
    export_result=(True, "output/informe_test.txt"),
    scraper_error=None,
    translation_error=False,
):
    """Lanza la CLI con dependencias simuladas y devuelve los mocks."""
    enricher_factory = (
        MagicMock(return_value=_enricher_mock())
        if with_ai
        else MagicMock(side_effect=ValueError("API key not found."))
    )
    translator = MagicMock()
    if translation_error:
        translator.translate.side_effect = ServicioNoDisponibleError(
            "El módulo de traducción (DeepTranslate) aún no está implementado."
        )
    else:
        translator.translate.return_value = "Texto traducido"

    with patch("src.main.setup_logging"), \
            patch("src.main.AiContentEnricher", enricher_factory), \
            patch("src.main.WikipediaScraper") as scraper_cls, \
            patch("src.main.DeepTranslateTranslator", return_value=translator), \
            patch("src.main.DocumentExporter") as exporter_cls, \
            patch("builtins.input", side_effect=inputs):
        scraper_cls.return_value.extract_content.return_value = dict(RESEARCH_RESULT)
        if scraper_error:
            scraper_cls.side_effect = scraper_error
        exporter_cls.return_value.export_content.return_value = export_result
        code = main()

    return code, exporter_cls, scraper_cls, translator


# --- Consola -----------------------------------------------------------------

def test_setup_console_is_resilient_to_streams():
    """La CLI no debe fallar por codificación ni si un stream no soporta reconfigure."""
    stream = MagicMock()
    stream.reconfigure.side_effect = ValueError("stream cerrado")

    with patch("src.main.sys.stdout", stream), \
            patch("src.main.sys.stderr", stream), \
            patch("src.main.sys.stdin", stream):
        _setup_console()

    assert stream.reconfigure.called


def test_setup_console_forces_utf8():
    """La salida se reconfigura a UTF-8 para soportar emojis y tildes."""
    with patch("src.main.sys.stdout") as stdout:
        _setup_console()

    stdout.reconfigure.assert_called_with(encoding="utf-8", errors="replace")


# --- Servicio de IA ----------------------------------------------------------

def test_create_enricher_returns_none_without_credentials(monkeypatch, capsys):
    """Sin credenciales la CLI sigue en pie: se avisa y el flujo continúa."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert _create_enricher() is None
    assert "IA no disponible" in capsys.readouterr().out


def test_create_enricher_with_credentials(monkeypatch):
    """Con credenciales se construye el cliente de IA."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://ejemplo/v1")

    enricher = _create_enricher()

    assert enricher is not None
    assert enricher.api_key == "sk-test"


# --- Diálogo con el usuario ---------------------------------------------------

def test_ask_text_retries_until_non_empty(capsys):
    """Un valor vacío repite la pregunta hasta recibir texto."""
    with patch("builtins.input", side_effect=["", "  ", "python"]):
        assert ask_text("Tema: ") == "python"

    assert "no puede estar vacío" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("", True),          # Enter aplica el valor por defecto
        ("si", True),
        ("no", False),
        ("N", False),
    ],
)
def test_confirm_answers(answer, expected):
    """Confirmar acepta el valor por defecto y las variantes de sí/no."""
    with patch("builtins.input", side_effect=[answer]):
        assert confirm("¿Guardar?", True) is expected


def test_confirm_retries_on_invalid_answer(capsys):
    """Una respuesta que no es sí/no vuelve a preguntar."""
    with patch("builtins.input", side_effect=["tal vez", "sí"]):
        assert confirm("¿Guardar?", False) is True

    assert "Responde 'sí' o 'no'" in capsys.readouterr().out


def test_ask_format_retries_until_valid(capsys):
    """Solo se aceptan los formatos soportados por el exportador."""
    with patch("builtins.input", side_effect=["docx", "TXT"]):
        assert ask_format() == "txt"

    assert "Formato no válido" in capsys.readouterr().out


def test_ask_sections_accepts_multiple_values():
    """La multi-selección admite varias claves separadas por comas, sin repetir."""
    with patch("builtins.input", side_effect=["3,1,3"]):
        selected = ask_sections(SECTIONS)

    assert selected == [SECTIONS[0], SECTIONS[2]]


def test_ask_sections_rejects_unknown_keys(capsys):
    """Una clave inexistente repite la pregunta hasta recibir una válida."""
    with patch("builtins.input", side_effect=["9", "2"]):
        selected = ask_sections(SECTIONS)

    assert selected == [SECTIONS[1]]
    assert "Respuesta no válida" in capsys.readouterr().out


# --- Composición del informe ---------------------------------------------------

def test_compose_body_single_section_returns_exact_text():
    """Con una sola sección el archivo contiene exactamente ese contenido."""
    assert compose_body([SECTIONS[0]]) == "original"


def test_compose_body_multiple_sections_adds_labels():
    """Con varias secciones cada una se identifica con su rótulo."""
    body = compose_body([SECTIONS[0], SECTIONS[1]])

    assert "Texto original" in body
    assert "original" in body
    assert "Contenido enriquecido (IA)" in body
    assert "enriquecido" in body


# --- Investigación -------------------------------------------------------------

def test_research_topic_normalizes_scraper_output():
    """La investigación devuelve un único diccionario con el texto unido."""
    with patch("src.main.WikipediaScraper") as scraper_cls:
        scraper_cls.return_value.extract_content.return_value = dict(RESEARCH_RESULT)
        research = research_topic("python")

    assert research == {
        "title": "Python",
        "paragraphs": ["Párrafo uno.", "Párrafo dos."],
        "text": FULL_TEXT,
    }


def test_research_topic_propagates_scraper_errors():
    """Un artículo inexistente sube hasta la CLI como error controlado."""
    with patch("src.main.WikipediaScraper", side_effect=ValueError("no existe")):
        with pytest.raises(ValueError, match="no existe"):
            research_topic("tema inexistente")


# --- Flujo completo -------------------------------------------------------------

def test_full_flow_exports_only_the_selected_sections():
    """Requisito: el archivo recibe únicamente las partes pedidas por el usuario."""
    inputs = ["python", "fr", "s", "s", "1,3", "txt", "informe_test"]
    code, exporter_cls, scraper_cls, _ = run_cli(inputs)

    assert code == 0
    scraper_cls.assert_called_once_with("python")
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["file_name"] == "informe_test"
    assert call["output_format"] == "txt"
    assert call["content_data"]["topic"] == "Python"
    body = call["content_data"]["body"]
    assert "Párrafo uno." in body
    assert "Resumen ejecutivo" in body
    assert "Contenido enriquecido por IA" not in body


def test_flow_shows_wikipedia_content_before_export(capsys):
    """Requisito: la extracción se muestra en terminal durante el flujo."""
    inputs = ["python", "", "n", "s", "1", "txt", "informe_test"]
    code, _, _, _ = run_cli(inputs)
    output = capsys.readouterr().out

    assert code == 0
    assert "TÍTULO: Python" in output
    assert "Párrafo 1" in output


def test_flow_without_ai_credentials_continues_with_original(capsys):
    """Sin IA el flujo no se interrumpe: se avisa y solo existe el texto original."""
    inputs = ["python", "", "s", "1", "txt", "informe_test"]
    code, exporter_cls, _, _ = run_cli(inputs, with_ai=False)
    output = capsys.readouterr().out

    assert code == 0
    assert "IA no disponible" in output
    assert "Enriquecimiento omitido" in output
    assert "Contenido enriquecido (IA)" not in output
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["content_data"]["body"] == FULL_TEXT


def test_flow_stops_when_wikipedia_falls():
    """Failed: un artículo inexistente informa del motivo y no se exporta nada."""
    code, exporter_cls, _, _ = run_cli(
        ["python", "", "s"],
        scraper_error=ValueError("no existe"),
    )

    assert code == 1
    exporter_cls.return_value.export_content.assert_not_called()


def test_flow_reports_unavailable_translation(capsys):
    """Mientras el módulo no esté entregado se avisa y la traducción se omite."""
    inputs = ["python", "fr", "n", "s", "1,2", "txt", "informe_test"]
    code, exporter_cls, _, _ = run_cli(inputs, translation_error=True)
    output = capsys.readouterr().out

    assert code == 0
    assert "Traducción omitida" in output
    assert "[4] Traducción" not in output
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert "Traducción" not in call["content_data"]["body"]


def test_flow_translates_the_final_content():
    """Si el traductor está disponible, la traducción se muestra y se puede guardar."""
    inputs = ["python", "fr", "n", "s", "4", "pdf", "informe"]
    code, exporter_cls, _, translator = run_cli(inputs)

    assert code == 0
    # La traducción se aplica al final, sobre el contenido resultante.
    translator.translate.assert_called_once_with("Contenido enriquecido por IA", "fr")
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["output_format"] == "pdf"
    assert call["content_data"]["body"] == "Texto traducido"


def test_discarding_the_report_skips_export():
    """El usuario puede abandonar sin escribir nada en disco."""
    code, exporter_cls, _, _ = run_cli(["python", "", "s", "no"])

    assert code == 0
    exporter_cls.return_value.export_content.assert_not_called()


def test_export_failure_returns_error_code():
    """Un fallo del exportador se devuelve como código de salida distinto de cero."""
    code, _, _, _ = run_cli(
        ["python", "", "s", "s", "1", "txt", "informe_test"],
        export_result=(False, "Error de Validación: formato"),
    )

    assert code == 1


def test_user_cancellation_returns_130():
    """Ctrl+C o fin de entrada devuelven el código de cancelación."""
    with patch("src.main.setup_logging"), patch("builtins.input", side_effect=EOFError):
        assert main() == 130
