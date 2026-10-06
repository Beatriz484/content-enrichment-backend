"""Tests de la CLI (``src/main.py``) con todas las dependencias simuladas."""
from unittest.mock import MagicMock, patch

import pytest

from src.enricher import AiContentEnricher
from src.errors import AiError
from src.main import _configurar_consola, _crear_enricher, main
from src.options import ContentMode, OutputOptions
from src.pipeline import ContentPipeline

INVESTIGACION = {
    "titulo": "Python",
    "parrafos": ["Párrafo uno.", "Párrafo dos."],
    "texto": "Párrafo uno.\n\nPárrafo dos.",
}


def _opciones(**cambios):
    base = {
        "tema": "python",
        "content_mode": ContentMode.ORIGINAL,
        "formato": "txt",
        "nombre": "informe_test",
    }
    base.update(cambios)
    return OutputOptions(**base)


def _pipeline_simulado():
    pipeline = MagicMock(spec=ContentPipeline)
    pipeline.translator = None
    pipeline.investigar.return_value = INVESTIGACION
    pipeline.procesar.return_value = MagicMock(
        topic="Python",
        body="VARIANTE FINAL",
        pasos=[("CONTENIDO ORIGINAL", INVESTIGACION["texto"])],
        informe={"topic": "Python", "body": "VARIANTE FINAL"},
        variante="original",
    )
    return pipeline


def _ejecutar_cli(
    opciones=None,
    guardar=True,
    pipeline_factory=None,
    export_resultado=(True, "output/informe_test.txt"),
    enricher=MagicMock(spec=AiContentEnricher),
):
    """Lanza la CLI con dependencias simuladas y devuelve los mocks."""
    pipeline = (pipeline_factory or _pipeline_simulado)()
    with patch("src.main.setup_logging"), \
            patch("src.main.AiContentEnricher", return_value=enricher), \
            patch("src.main.ContentPipeline", return_value=pipeline), \
            patch("src.main.pedir_opciones", return_value=opciones or _opciones()), \
            patch("src.main.confirmar", return_value=guardar), \
            patch("src.main.pedir_exportacion", side_effect=lambda opciones: opciones), \
            patch("src.main.DocumentExporter") as exporter_cls:
        exporter_cls.return_value.export_content.return_value = export_resultado
        codigo = main()
    return codigo, pipeline, exporter_cls


# --- Consola ---------------------------------------------------------------

def test_configurar_consola_es_resiliente_a_los_streams():
    """La CLI no debe fallar por codificación ni si un stream no soporta reconfigure."""
    stream = MagicMock()
    stream.reconfigure.side_effect = ValueError("stream cerrado")

    with patch("src.main.sys.stdout", stream), \
            patch("src.main.sys.stderr", stream), \
            patch("src.main.sys.stdin", stream):
        _configurar_consola()

    assert stream.reconfigure.called


def test_configurar_consola_fuerza_utf8():
    """La salida se reconfigura a UTF-8 para soportar emojis y tildes."""
    with patch("src.main.sys.stdout") as stdout:
        _configurar_consola()

    stdout.reconfigure.assert_called_with(encoding="utf-8", errors="replace")


# --- Servicio de IA ---------------------------------------------------------

def test_crear_enricher_sin_clave_devuelve_none(monkeypatch):
    """Sin credenciales la CLI sigue en pie: el enricher queda en ``None``."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert _crear_enricher() is None


def test_crear_enricher_con_clave(monkeypatch):
    """Con credenciales se construye el cliente de IA."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://ejemplo/v1")

    enricher = _crear_enricher()

    assert enricher is not None
    assert enricher.api_key == "sk-test"


# --- Flujo completo ---------------------------------------------------------

def test_main_exporta_exclusivamente_la_variante():
    """El exportador recibe únicamente {topic, body}: no puede colar secciones."""
    codigo, pipeline, exporter_cls = _ejecutar_cli()

    assert codigo == 0
    pipeline.investigar.assert_called_once_with("python")
    pipeline.procesar.assert_called_once()
    llamada = exporter_cls.return_value.export_content.call_args.kwargs
    assert llamada["file_name"] == "informe_test"
    assert llamada["output_format"] == "txt"
    assert llamada["content_data"] == {"topic": "Python", "body": "VARIANTE FINAL"}


def test_main_muestra_los_resultados_de_wikipedia_antes_de_exportar():
    """Requisito: la extracción se muestra antes de pedir acciones adicionales."""
    codigo, pipeline, _ = _ejecutar_cli()

    assert codigo == 0
    pipeline.investigar.assert_called_once_with("python")


def test_main_con_opciones_invalidas_no_investiga():
    """Failed: la validación corta el flujo antes de gastar una petición."""
    opciones = _opciones(content_mode=ContentMode.ENRICHED, resumir=True, idioma="fr")
    codigo, pipeline, exporter_cls = _ejecutar_cli(
        opciones=opciones,
        enricher=None,
    )

    assert codigo == 1
    pipeline.investigar.assert_not_called()
    exporter_cls.return_value.export_content.assert_not_called()


def test_main_sin_ia_en_modo_original_continua():
    """La variante original no necesita IA: el flujo no se interrumpe."""
    opciones = _opciones(content_mode=ContentMode.ORIGINAL, resumir=False, idioma=None)
    codigo, pipeline, _ = _ejecutar_cli(opciones=opciones, enricher=None)

    assert codigo == 0
    pipeline.procesar.assert_called_once()


def test_main_aborta_si_wikipedia_falla():
    """Un artículo inexistente se informa y no se exporta nada."""
    def _pipeline_roto():
        pipeline = _pipeline_simulado()
        pipeline.investigar.side_effect = ValueError("no existe")
        return pipeline

    codigo, _, exporter_cls = _ejecutar_cli(pipeline_factory=_pipeline_roto)

    assert codigo == 1
    exporter_cls.return_value.export_content.assert_not_called()


def test_main_aborta_si_el_procesamiento_falla():
    """Un fallo de la API de IA llega a la terminal y no genera archivo."""
    def _pipeline_con_error():
        pipeline = _pipeline_simulado()
        pipeline.procesar.side_effect = AiError("la API de IA se cayó")
        return pipeline

    codigo, _, exporter_cls = _ejecutar_cli(pipeline_factory=_pipeline_con_error)

    assert codigo == 1
    exporter_cls.return_value.export_content.assert_not_called()


def test_main_descarta_el_informe_si_el_usuario_dice_que_no():
    """El usuario puede abandonar sin escribir nada en disco."""
    codigo, _, exporter_cls = _ejecutar_cli(guardar=False)

    assert codigo == 0
    exporter_cls.return_value.export_content.assert_not_called()


def test_main_devuelve_error_si_la_exportacion_falla():
    codigo, _, _ = _ejecutar_cli(export_resultado=(False, "Error de Validación: formato"))

    assert codigo == 1


def test_main_se_cancela_con_control_c():
    with patch("src.main.setup_logging"), patch("builtins.input", side_effect=EOFError):
        assert main() == 130
