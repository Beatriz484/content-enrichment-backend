r"""Feature: End-to-end flow of the command line application

  As a Content Enricher user
  I want the whole pipeline run in order and a single result exported
  So that I always know what was done and exactly what was saved
"""

from unittest.mock import MagicMock, patch

from src.cli import _setup_console, main
from src.errors import ServiceUnavailableError

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

    with patch("src.cli.setup_logging"), \
            patch("src.pipeline.AiContentEnricher", enricher_factory), \
            patch("src.pipeline.WikipediaScraper") as scraper_cls, \
            patch("src.cli.DeepTranslateTranslator", return_value=translator), \
            patch("src.cli.DocumentExporter") as exporter_cls, \
            patch("builtins.input", side_effect=fake_input):
        scraper_cls.return_value.extract_content.return_value = dict(RESEARCH_RESULT)
        if scraper_error:
            scraper_cls.side_effect = scraper_error
        exporter_cls.return_value.export_content.return_value = export_result
        code = main()

    return code, exporter_cls, scraper_cls, translator


def test_setup_console_is_resilient_to_streams():
    r"""@successful

    Scenario: Keep starting up when a stream refuses to be reconfigured
        Given a stream that raises while it is being reconfigured
        When the console is set up
        Then the reconfiguration is still attempted
        And the application does not crash
    """
    stream = MagicMock()
    stream.reconfigure.side_effect = ValueError("stream cerrado")

    with patch("src.cli.sys.stdout", stream), \
            patch("src.cli.sys.stderr", stream), \
            patch("src.cli.sys.stdin", stream):
        _setup_console()

    assert stream.reconfigure.called


def test_setup_console_forces_utf8():
    r"""@successful

    Scenario: Force UTF-8 on the console
        Given the standard output stream
        When the console is set up
        Then the stream is reconfigured with the UTF-8 encoding
        And unknown characters are replaced instead of raising
    """
    with patch("src.cli.sys.stdout") as stdout:
        _setup_console()

    stdout.reconfigure.assert_called_with(encoding="utf-8", errors="replace")


def test_export_saves_one_result_and_never_asks_for_parts(capsys):
    r"""@successful

    Scenario: Save one result without ever asking which parts to keep
        Given the user researches "python"
        And chooses the enriched content
        And declines the summary
        And keeps the original language
        And agrees to save the report as "txt" under the name "informe_test"
        When the pipeline runs
        Then the exit code is 0
        And the question "Qué partes deseas guardar" is never shown
        And the exported body is the enriched content
    """
    inputs = ["python", "2", "n", "", "s", "txt", "informe_test"]
    code, exporter_cls, _, _ = run_cli(inputs)
    output = capsys.readouterr().out

    assert code == 0
    assert "Qué partes deseas guardar" not in output
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["content_data"]["body"] == ENRICHED_TEXT


def test_export_saves_original_wikipedia_if_chosen(capsys):
    r"""@successful

    Scenario: Save the original Wikipedia text when that option is chosen
        Given the user researches "python"
        And chooses the original Wikipedia text
        And declines the summary
        And keeps the original language
        And agrees to save the report as "txt" under the name "informe_test"
        When the pipeline runs
        Then the exit code is 0
        And the terminal says that the original Wikipedia text is kept
        And the exported body is the original text
    """
    inputs = ["python", "1", "n", "", "s", "txt", "informe_test"]
    code, exporter_cls, _, _ = run_cli(inputs)
    output = capsys.readouterr().out

    assert code == 0
    assert "Se mantendrá el texto original de Wikipedia" in output
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["content_data"]["body"] == FULL_TEXT


def test_export_result_is_the_last_stage_of_the_chain():
    r"""@successful

    Scenario: Export the last stage of the chain
        Given the user researches "python"
        And chooses the enriched content
        And asks for a summary
        And asks for the French translation
        And agrees to save the report as "pdf" under the name "informe"
        When the pipeline runs
        Then the exit code is 0
        And the summary is the text handed to the translator
        And the exported body is the translated text
    """
    inputs = ["python", "2", "s", "fr", "s", "pdf", "informe"]
    code, exporter_cls, _, translator = run_cli(inputs)

    assert code == 0
    translator.translate.assert_called_once_with("Resumen ejecutivo", "fr")
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["content_data"]["body"] == "Texto traducido"


def test_full_flow_exports_the_single_final_result():
    r"""@successful

    Scenario: Run every step of the pipeline and export one single result
        Given the user researches "python"
        And chooses the enriched content
        And asks for a summary
        And asks for the French translation
        And agrees to save the report as "txt" under the name "informe_test"
        When the pipeline runs
        Then the exit code is 0
        And Wikipedia is searched once for "python"
        And the export receives the file name "informe_test"
        And the export receives the format "txt"
        And the export receives the title "Python"
        And the export receives the translated text
    """
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
    r"""@successful

    Scenario: Ask for each decision only after the search results are shown
        Given the user researches "python" and answers every prompt
        When the pipeline runs
        Then Wikipedia is read before the summary is asked
        And the summary is asked before the language is asked
        And the title of the article is shown on screen
    """
    events = []
    answers = iter(["python", "2", "s", "fr", "s", "txt", "informe_test"])

    def record_input(prompt=""):
        events.append(prompt)
        return next(answers)

    translator = MagicMock()
    translator.translate.return_value = "Texto traducido"

    with patch("src.cli.setup_logging"), \
            patch("src.pipeline.AiContentEnricher", return_value=_enricher_mock()), \
            patch("src.pipeline.WikipediaScraper") as scraper_cls, \
            patch("src.cli.DeepTranslateTranslator", return_value=translator), \
            patch("src.cli.DocumentExporter") as exporter_cls, \
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
    r"""@successful

    Scenario: Show the Wikipedia content before the export is offered
        Given the user researches "python" and answers every prompt
        When the pipeline runs
        Then the exit code is 0
        And the title "TÍTULO: Python" is shown on screen
        And the paragraph "Párrafo 1" is shown on screen
    """
    inputs = ["python", "2", "n", "", "s", "txt", "informe_test"]
    code, _, _, _ = run_cli(inputs)
    output = capsys.readouterr().out

    assert code == 0
    assert "TÍTULO: Python" in output
    assert "Párrafo 1" in output


def test_flow_without_ai_credentials_continues_with_original(capsys):
    r"""@failure

    Scenario: Continue with the original text when there are no AI credentials
        Given no AI credentials are configured
        And the user researches "python" and answers every prompt
        When the pipeline runs
        Then the exit code is 0
        And the terminal says that AI is unavailable
        And the terminal says that the enrichment was skipped
        And no enriched section is shown
        And the exported body is the original text
    """
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
    r"""@failure

    Scenario: Stop the pipeline when Wikipedia cannot be read
        Given the scraper raises the error "no existe"
        And the user researches "python"
        When the pipeline runs
        Then the exit code is 1
        And nothing is exported
    """
    code, exporter_cls, _, _ = run_cli(
        ["python"],
        scraper_error=ValueError("no existe"),
    )

    assert code == 1
    exporter_cls.return_value.export_content.assert_not_called()


def test_flow_reports_unavailable_translation(capsys):
    r"""@failure

    Scenario: Report an unavailable translation and export the previous stage
        Given the translation service is unavailable
        And the user researches "python" and answers every prompt in French
        When the pipeline runs
        Then the exit code is 0
        And the terminal says that the translation was skipped
        And no translated section is shown
        And the exported body is the enriched content
    """
    inputs = ["python", "2", "n", "fr", "s", "txt", "informe_test"]
    code, exporter_cls, _, _ = run_cli(inputs, translation_error=True)
    output = capsys.readouterr().out

    assert code == 0
    assert "Traducción omitida" in output
    assert "CONTENIDO TRADUCIDO" not in output
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["content_data"]["body"] == ENRICHED_TEXT


def test_flow_translates_the_final_content():
    r"""@successful

    Scenario: Translate the final content and export it as a PDF
        Given the user researches "python"
        And chooses the enriched content
        And declines the summary
        And asks for the French translation
        And agrees to save the report as "pdf" under the name "informe"
        When the pipeline runs
        Then the exit code is 0
        And the translator receives the enriched content and the code "fr"
        And the export receives the format "pdf"
        And the exported body is the translated text
    """
    inputs = ["python", "2", "n", "fr", "s", "pdf", "informe"]
    code, exporter_cls, _, translator = run_cli(inputs)

    assert code == 0
    translator.translate.assert_called_once_with(ENRICHED_TEXT, "fr")
    call = exporter_cls.return_value.export_content.call_args.kwargs
    assert call["output_format"] == "pdf"
    assert call["content_data"]["body"] == "Texto traducido"


def test_discarding_the_report_skips_export():
    r"""@successful

    Scenario: Skip the export when the user discards the report
        Given the user researches "python" and discards the report
        When the pipeline runs
        Then the exit code is 0
        And nothing is exported
    """
    code, exporter_cls, _, _ = run_cli(["python", "2", "n", "", "no"])

    assert code == 0
    exporter_cls.return_value.export_content.assert_not_called()


def test_export_failure_returns_error_code():
    r"""@failure

    Scenario: Return an error code when the export fails
        Given the export answers with the error "Error de Validación: formato"
        And the user researches "python" and agrees to save the report
        When the pipeline runs
        Then the exit code is 1
    """
    code, _, _, _ = run_cli(
        ["python", "2", "n", "", "s", "txt", "informe_test"],
        export_result=(False, "Error de Validación: formato"),
    )

    assert code == 1


def test_user_cancellation_returns_130():
    r"""@failure

    Scenario: Return the cancellation code when the user interrupts the run
        Given the input stream is closed by the user
        When the pipeline runs
        Then the exit code is 130
    """
    with patch("src.cli.setup_logging"), patch("builtins.input", side_effect=EOFError):
        assert main() == 130
