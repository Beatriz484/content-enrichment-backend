import os
from src.exporter.txt_exporter import TxtExporter


def test_txt_exporter_generate_success(tmp_path):
    """Prueba que el archivo TXT se genere correctamente con las secciones requeridas."""
    output_file = tmp_path / "test_report.txt"
    sample_data = {
        "topic": "Python Testing",
        "raw_text": "Texto extraído de prueba.",
        "enriched_text": "Texto enriquecido por IA.",
        "translated_text": "Translated text for testing."
    }

    result_path = TxtExporter.generate(str(output_file), sample_data)
    assert os.path.exists(result_path)

    with open(result_path, "r", encoding="utf-8") as file:
        content = file.read()
        assert "INFORME DE INVESTIGACIÓN: Python Testing" in content
        assert "1. CONTENIDO ORIGINAL (EXTRAÍDO)" in content
        assert "Texto extraído de prueba." in content
        assert "2. CONTENIDO ENRIQUECIDO Y RESUMIDO (IA)" in content
        assert "3. CONTENIDO TRADUCIDO" in content