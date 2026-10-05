"""Tests de la CLI (``src/main.py``) con todas las dependencias simuladas."""
from unittest.mock import MagicMock, patch

from src.main import _confirmar, _pedir_formato, _preguntar_texto, main
from src.pipeline import ContentPipeline


def _pipeline_simulada():
    pipeline = MagicMock()
    pipeline.investigar.return_value = {
        "titulo": "Python",
        "parrafos": ["Párrafo uno.", "Párrafo dos."],
        "texto": "Párrafo uno.\n\nPárrafo dos.",
    }
    pipeline.enriquecer.return_value = "Contenido enriquecido"
    pipeline.resumir.return_value = "Resumen ejecutivo"
    pipeline.traducir.return_value = ""
    # Se mantiene la construcción real del contrato del exportador
    pipeline.construir_content_data = ContentPipeline.construir_content_data
    return pipeline


def _ejecutar_cli(respuestas, export_resultado=(True, "output/informe_test.txt")):
    """Lanza la CLI con respuestas simuladas y devuelve los mocks."""
    with patch("src.main.setup_logging"), \
            patch("src.main.AiContentEnricher", return_value=MagicMock()), \
            patch("src.main.ContentPipeline", return_value=_pipeline_simulada()) as pipeline_cls, \
            patch("src.main.DocumentExporter") as exporter_cls, \
            patch("builtins.input", side_effect=respuestas):
        exporter_cls.return_value.export_content.return_value = export_resultado
        codigo = main()
    return codigo, pipeline_cls, exporter_cls


# --- Helpers de interacción -------------------------------------------------

def test_preguntar_texto_repite_hasta_recibir_valor():
    with patch("builtins.input", side_effect=["", "   ", "tema final"]):
        assert _preguntar_texto("➤ Tema: ") == "tema final"


def test_confirmar_acepta_respuestas_validas():
    with patch("builtins.input", side_effect=["xyz", "no"]):
        assert _confirmar("¿Continuar?") is False
    with patch("builtins.input", side_effect=["sí"]):
        assert _confirmar("¿Continuar?") is True


def test_confirmar_enter_conserva_el_valor_por_defecto():
    with patch("builtins.input", return_value=""):
        assert _confirmar("¿Continuar?", True) is True
        assert _confirmar("¿Continuar?", False) is False


def test_pedir_formato_valida_entradas():
    with patch("builtins.input", side_effect=["docx", "TXT"]):
        assert _pedir_formato() == "txt"


# --- Flujo completo ---------------------------------------------------------

def test_main_exporta_el_informe_correctamente():
    codigo, _, exporter_cls = _ejecutar_cli(
        ["Python", "en", "", "", "txt", "informe_test"]
    )

    assert codigo == 0
    llamada = exporter_cls.return_value.export_content.call_args.kwargs
    assert llamada["file_name"] == "informe_test"
    assert llamada["output_format"] == "txt"
    assert llamada["content_data"]["summary"] == "Resumen ejecutivo"
    assert llamada["content_data"]["topic"] == "Python"


def test_main_sin_ia_genera_informe_sin_resumen():
    with patch("src.main.setup_logging"), \
            patch("src.main.AiContentEnricher", side_effect=ValueError("API key not found")), \
            patch("src.main.ContentPipeline") as pipeline_cls, \
            patch("src.main.DocumentExporter") as exporter_cls, \
            patch("builtins.input", side_effect=["Python", "en", "", "", "pdf", "informe"]):
        pipeline = pipeline_cls.return_value
        pipeline.enriquecer.return_value = "Contenido original"
        pipeline.resumir.return_value = ""
        pipeline.traducir.return_value = ""
        pipeline.construir_content_data = ContentPipeline.construir_content_data
        exporter_cls.return_value.export_content.return_value = (True, "output/informe.pdf")
        codigo = main()

    # Sin API key la pipeline se construye sin enriquecedor
    assert pipeline_cls.call_args.kwargs["enricher"] is None
    assert codigo == 0


def test_main_descarta_el_informe_si_el_usuario_dice_que_no():
    codigo, _, exporter_cls = _ejecutar_cli(["Python", "en", "n", "n"])

    assert codigo == 0
    exporter_cls.assert_not_called()


def test_main_no_exporta_si_wikipedia_falla():
    with patch("src.main.setup_logging"), \
            patch("src.main.AiContentEnricher", return_value=MagicMock()), \
            patch("src.main.ContentPipeline") as pipeline_cls, \
            patch("src.main.DocumentExporter") as exporter_cls, \
            patch("builtins.input", side_effect=["tema inexistente", "en"]):
        pipeline_cls.return_value.investigar.side_effect = ValueError("no existe")
        codigo = main()

    assert codigo == 1
    exporter_cls.assert_not_called()


def test_main_devuelve_error_si_la_exportacion_falla():
    codigo, _, _ = _ejecutar_cli(
        ["Python", "en", "", "", "txt", "informe"],
        export_resultado=(False, "Error de Validación: formato no permitido"),
    )

    assert codigo == 1


def test_main_se_cancela_con_control_c():
    with patch("src.main.setup_logging"), patch("builtins.input", side_effect=EOFError):
        assert main() == 130
