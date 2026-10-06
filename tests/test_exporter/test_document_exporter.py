"""Tests del orquestador de exportación."""
import os

from src.exporter.document_exporter import DocumentExporter

INFORME = {"topic": "Integración", "body": "Contenido de la variante pedida."}


def test_document_exporter_initialization(tmp_path):
    """Prueba que se cree el directorio de salida si no existe."""
    target_dir = tmp_path / "new_output_dir"
    DocumentExporter(output_dir=str(target_dir))
    assert os.path.exists(target_dir)


def test_export_content_txt_success(tmp_path):
    """Flujo completo exitoso para TXT."""
    exporter = DocumentExporter(output_dir=str(tmp_path))

    is_success, file_path = exporter.export_content("informe_test", "txt", INFORME)

    assert is_success is True
    assert file_path.endswith("informe_test.txt")
    assert os.path.exists(file_path)


def test_export_content_pdf_success(tmp_path):
    """Flujo completo exitoso para PDF."""
    exporter = DocumentExporter(output_dir=str(tmp_path))

    is_success, file_path = exporter.export_content("informe_test", "pdf", INFORME)

    assert is_success is True
    assert file_path.endswith("informe_test.pdf")
    assert os.path.exists(file_path)


def test_export_content_no_duplica_la_extension(tmp_path):
    """Si el nombre ya trae la extensión, no se añade una segunda."""
    exporter = DocumentExporter(output_dir=str(tmp_path))

    is_success, file_path = exporter.export_content("informe.txt", "txt", INFORME)

    assert is_success is True
    assert file_path.endswith(os.path.join("informe.txt"))


def test_export_content_validation_failure(tmp_path):
    """No se crea ningún archivo si falla la validación temprana."""
    exporter = DocumentExporter(output_dir=str(tmp_path))

    is_success, error_msg = exporter.export_content("informe_fallido", "doc", {})

    assert is_success is False
    assert "Error de Validación" in error_msg
    assert os.listdir(tmp_path) == []


def _permiso_denegado(*args, **kwargs):
    raise PermissionError()


def _disco_lleno(*args, **kwargs):
    raise RuntimeError("disco lleno")


def test_export_content_permisos_insuficientes(tmp_path, monkeypatch):
    """Un error de permisos del SO se traduce en un mensaje accionable."""
    from src.exporter import document_exporter

    monkeypatch.setattr(document_exporter.TxtExporter, "generate", _permiso_denegado)

    is_success, error_msg = DocumentExporter(output_dir=str(tmp_path)).export_content(
        "bloqueado", "txt", INFORME
    )

    assert is_success is False
    assert "Permisos insuficientes" in error_msg


def test_export_content_error_inesperado(tmp_path, monkeypatch):
    """Cualquier otro fallo queda capturado y devuelto como detalle."""
    from src.exporter import document_exporter

    monkeypatch.setattr(document_exporter.TxtExporter, "generate", _disco_lleno)

    is_success, error_msg = DocumentExporter(output_dir=str(tmp_path)).export_content(
        "fallo", "txt", INFORME
    )

    assert is_success is False
    assert "disco lleno" in error_msg
