from unittest.mock import MagicMock, patch

import pytest

from src.errors import ServiceUnavailableError
from src.main import (
    _create_enricher,
    _setup_console,
    ask_choice,
    ask_format,
    ask_text,
    confirm,
    main,
    research_topic,
)

RESEARCH_RESULT = {
    "title": "Python",
    "paragraphs": ["Párrafo uno.", "Párrafo dos."],
}
FULL_TEXT = "Párrafo uno.\n\nPárrafo dos."
ENRICHED_TEXT = "Contenido enriquecido por IA"


def _enricher_mock():
    enricher = MagicMock()
    enricher.enrich_content.return_value = ENRICHED_TEXT
    enricher.summarize_content.return_value = "Resumen ejecutivo"
    return enricher


def run_cli(
    inputs,
    prompts=None,
    with_ai=True,
    export_result=(True, "output/informe_test.txt"),
    scraper_error=None,
    translation_error=False,
):
    enricher_factory = (
        MagicMock(return_value=_enricher_mock())
        if with_ai
        else MagicMock(side_effect=ValueError("API key not found."))
    )
    translator = MagicMock()
    if translation_error:
        translator.translate.side_effect = ServiceUnavailableError(
            "El módulo de traducción (DeepTranslate) aún no está implementado."
        )
    else:
        translator.translate.return_value = "Texto traducido"

    answers = iter(inputs)
    prompt_log = prompts if prompts is not None else []

    def fake_input(prompt=""):
        prompt_log.append(prompt)
        try:
            return next(answers)
        except StopIteration:
            raise EOFError

    with patch("src.main.setup_logging"), \
            patch("src.main.AiContentEnricher", enricher_factory), \
            patch("src.main.WikipediaScraper") as scraper_cls, \
            patch("src.main.DeepTranslateTranslator", return_value=translator), \
            patch("src.main.DocumentExporter") as exporter_cls, \
            patch("builtins.input", side_effect=fake_input):
        scraper_cls.return_value.extract_content.return_value = dict(RESEARCH_RESULT)
        if scraper_error:
            scraper_cls.side_effect = scraper_error
        exporter_cls.return_value.export_content.return_value = export_result
        code = main()

    return code, exporter_cls, scraper_cls, translator


def test_setup_console_is_resilient_to_streams():
    stream = MagicMock()
    stream.reconfigure.side_effect = ValueError("stream cerrado")

    with patch("src.main.sys.stdout", stream), \
            patch("src.main.sys.stderr", stream), \
            patch("src.main.sys.stdin", stream):
        _setup_console()

    assert stream.reconfigure.called


def test_setup_console_forces_utf8():
    with patch("src.main.sys.stdout") as stdout:
        _setup_console()

    stdout.reconfigure.assert_called_with(encoding="utf-8", errors="replace")


def test_create_enricher_returns_none_without_credentials(monkeypatch, capsys):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert _create_enricher() is None
    assert "IA no disponible" in capsys.readouterr().out


def test_create_enricher_with_credentials(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://ejemplo/v1")

    enricher = _create_enricher()

    assert enricher is not None
    assert enricher.api_key == "sk-test"


def test_ask_text_retries_until_non_empty(capsys):
    with patch("builtins.input", side_effect=["", "  ", "python"]):
        assert ask_text("Tema: ") == "python"

    assert "no puede estar vacío" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("", True),
        ("si", True),
        ("no", False),
        ("N", False),
    ],
)
def test_confirm_answers(answer, expected):
    with patch("builtins.input", side_effect=[answer]):
        assert confirm("¿Guardar?", True) is expected


def test_confirm_retries_on_invalid_answer(capsys):
    with patch("builtins.input", side_effect=["tal vez", "sí"]):
        assert confirm("¿Guardar?", False) is True

    assert "Responde 'sí' o 'no'" in capsys.readouterr().out


def test_ask_format_retries_until_valid(capsys):
    with patch("builtins.input", side_effect=["docx", "TXT"]):
        assert ask_format() == "txt"

    assert "Formato no válido" in capsys.readouterr().out


def test_ask_choice_retries_until_valid_option(capsys):
    with patch("builtins.input", side_effect=["3", "2"]):
        assert ask_choice("➤ Elige una opción (1 / 2): ", ("1", "2")) == "2"

    assert "Opción no válida" in capsys.readouterr().out


def test_export_saves_one_result_and_never_asks_for_parts(capsys):
    inputs = ["python", "2", "n", "", "s", "txt", "informe_test"]
    code, exporter_cls, _, _ = run_cli(inputs)
    output = capsys.readouterr().out

    assert code == 0
    assert "Qué partes deseas guardar" not in output
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["content_data"]["body"] == ENRICHED_TEXT


def test_export_saves_original_wikipedia_if_chosen(capsys):
    inputs = ["python", "1", "n", "", "s", "txt", "informe_test"]
    code, exporter_cls, _, _ = run_cli(inputs)
    output = capsys.readouterr().out

    assert code == 0
    assert "Se mantendrá el texto original de Wikipedia" in output
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["content_data"]["body"] == FULL_TEXT


def test_export_result_is_the_last_stage_of_the_chain():
    inputs = ["python", "2", "s", "fr", "s", "pdf", "informe"]
    code, exporter_cls, _, translator = run_cli(inputs)

    assert code == 0
    translator.translate.assert_called_once_with("Resumen ejecutivo", "fr")
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["content_data"]["body"] == "Texto traducido"


def test_research_topic_normalizes_scraper_output():
    with patch("src.main.WikipediaScraper") as scraper_cls:
        scraper_cls.return_value.extract_content.return_value = dict(RESEARCH_RESULT)
        research = research_topic("python")

    assert research == {
        "title": "Python",
        "paragraphs": ["Párrafo uno.", "Párrafo dos."],
        "text": FULL_TEXT,
    }


def test_research_topic_propagates_scraper_errors():
    with patch("src.main.WikipediaScraper", side_effect=ValueError("no existe")):
        with pytest.raises(ValueError, match="no existe"):
            research_topic("tema inexistente")


def test_full_flow_exports_the_single_final_result():
    inputs = ["python", "2", "s", "fr", "s", "txt", "informe_test"]
    code, exporter_cls, scraper_cls, _ = run_cli(inputs)

    assert code == 0
    scraper_cls.assert_called_once_with("python")
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["file_name"] == "informe_test"
    assert call["output_format"] == "txt"
    assert call["content_data"]["topic"] == "Python"
    assert call["content_data"]["body"] == "Texto traducido"


def test_flow_asks_actions_after_showing_the_search_results(capsys):
    events = []
    answers = iter(["python", "2", "s", "fr", "s", "txt", "informe_test"])

    def record_input(prompt=""):
        events.append(prompt)
        return next(answers)

    translator = MagicMock()
    translator.translate.return_value = "Texto traducido"

    with patch("src.main.setup_logging"), \
            patch("src.main.AiContentEnricher", return_value=_enricher_mock()), \
            patch("src.main.WikipediaScraper") as scraper_cls, \
            patch("src.main.DeepTranslateTranslator", return_value=translator), \
            patch("src.main.DocumentExporter") as exporter_cls, \
            patch("builtins.input", side_effect=record_input):

        def record_wikipedia():
            events.append("wikipedia")
            return dict(RESEARCH_RESULT)

        scraper_cls.return_value.extract_content.side_effect = record_wikipedia
        exporter_cls.return_value.export_content.return_value = (
            True,
            "output/informe_test.txt",
        )
        assert main() == 0

    wikipedia_at = events.index("wikipedia")
    summary_at = next(i for i, event in enumerate(events) if "resumen" in event)
    language_at = next(i for i, event in enumerate(events) if "Idioma" in event)
    assert wikipedia_at < summary_at < language_at
    assert "TÍTULO: Python" in capsys.readouterr().out


def test_flow_shows_wikipedia_content_before_export(capsys):
    inputs = ["python", "2", "n", "", "s", "txt", "informe_test"]
    code, _, _, _ = run_cli(inputs)
    output = capsys.readouterr().out

    assert code == 0
    assert "TÍTULO: Python" in output
    assert "Párrafo 1" in output


def test_flow_without_ai_credentials_continues_with_original(capsys):
    inputs = ["python", "", "s", "txt", "informe_test"]
    code, exporter_cls, _, _ = run_cli(inputs, with_ai=False)
    output = capsys.readouterr().out

    assert code == 0
    assert "IA no disponible" in output
    assert "Enriquecimiento omitido" in output
    assert "Contenido enriquecido (IA)" not in output
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["content_data"]["body"] == FULL_TEXT


def test_flow_stops_when_wikipedia_falls():
    code, exporter_cls, _, _ = run_cli(
        ["python"],
        scraper_error=ValueError("no existe"),
    )

    assert code == 1
    exporter_cls.return_value.export_content.assert_not_called()


def test_flow_reports_unavailable_translation(capsys):
    inputs = ["python", "2", "n", "fr", "s", "txt", "informe_test"]
    code, exporter_cls, _, _ = run_cli(inputs, translation_error=True)
    output = capsys.readouterr().out

    assert code == 0
    assert "Traducción omitida" in output
    assert "CONTENIDO TRADUCIDO" not in output
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["content_data"]["body"] == ENRICHED_TEXT


def test_flow_translates_the_final_content():
    inputs = ["python", "2", "n", "fr", "s", "pdf", "informe"]
    code, exporter_cls, _, translator = run_cli(inputs)

    assert code == 0
    translator.translate.assert_called_once_with(ENRICHED_TEXT, "fr")
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["output_format"] == "pdf"
    assert call["content_data"]["body"] == "Texto traducido"


def test_discarding_the_report_skips_export():
    code, exporter_cls, _, _ = run_cli(["python", "2", "n", "", "no"])

    assert code == 0
    exporter_cls.return_value.export_content.assert_not_called()


def test_export_failure_returns_error_code():
    code, _, _, _ = run_cli(
        ["python", "2", "n", "", "s", "txt", "informe_test"],
        export_result=(False, "Error de Validación: formato"),
    )

    assert code == 1


def test_user_cancellation_returns_130():
    with patch("src.main.setup_logging"), patch("builtins.input", side_effect=EOFError):
        assert main() == 130