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
        assert "2. CONTENIDO ENRIQUECIDO (IA)" in content
        assert "3. CONTENIDO TRADUCIDO" in content


def test_txt_exporter_incluye_resumen_cuando_existe(tmp_path):
    """La sección 4 solo aparece si la IA generó resumen."""
    output_file = tmp_path / "test_report_summary.txt"
    sample_data = {
        "topic": "Python Testing",
        "raw_text": "Texto extraído de prueba.",
        "enriched_text": "Texto enriquecido por IA.",
        "translated_text": "Translated text for testing.",
        "summary": "Resumen ejecutivo de prueba.",
    }

    result_path = TxtExporter.generate(str(output_file), sample_data)

    with open(result_path, "r", encoding="utf-8") as file:
        content = file.read()
    assert "4. RESUMEN EJECUTIVO (IA)" in content
    assert "Resumen ejecutivo de prueba." in content


def test_txt_exporter_omite_resumen_si_es_vacio(tmp_path):
    """Sin resumen, el informe conserva únicamente las 3 secciones originales."""
    output_file = tmp_path / "test_report_no_summary.txt"
    sample_data = {
        "topic": "Python Testing",
        "raw_text": "Texto extraído de prueba.",
        "enriched_text": "Texto enriquecido por IA.",
        "translated_text": "Translated text for testing.",
        "summary": "",
    }

    result_path = TxtExporter.generate(str(output_file), sample_data)

    with open(result_path, "r", encoding="utf-8") as file:
        content = file.read()
    assert "4. RESUMEN" not in content
    assert "3. CONTENIDO TRADUCIDO" in content


def test_txt_exporter_titula_sin_ia_cuando_no_hubo_enriquecimiento(tmp_path):
    """Si la IA no actuó, la sección 2 no debe decir 'enriquecido (IA)'."""
    output_file = tmp_path / "test_report_no_ai.txt"
    texto_original = "Texto original sin tocar."
    sample_data = {
        "topic": "Sin IA",
        "raw_text": texto_original,
        "enriched_text": texto_original,  # la IA devolvió el texto original
        "translated_text": "Traducido.",
    }

    result_path = TxtExporter.generate(str(output_file), sample_data)

    with open(result_path, "r", encoding="utf-8") as file:
        content = file.read()
    assert "2. CONTENIDO SIN ENRIQUECER (IA NO DISPONIBLE)" in content
    assert "2. CONTENIDO ENRIQUECIDO (IA)" not in content


def test_txt_exporter_marca_traduccion_pendiente_si_esta_vacia(tmp_path):
    """Sin texto traducido, la sección 3 avisa en lugar de dejar un hueco."""
    output_file = tmp_path / "test_report_pending.txt"
    sample_data = {
        "topic": "Traducción pendiente",
        "raw_text": "Texto original.",
        "enriched_text": "Texto enriquecido.",
        "translated_text": "",
    }

    result_path = TxtExporter.generate(str(output_file), sample_data)

    with open(result_path, "r", encoding="utf-8") as file:
        content = file.read()
    assert "3. CONTENIDO TRADUCIDO (PENDIENTE)" in content
    assert "El módulo de traducción aún no está disponible" in content