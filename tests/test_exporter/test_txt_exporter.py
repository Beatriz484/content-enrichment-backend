import os

from src.exporter.txt_exporter import TxtExporter


def _leer(ruta):
    with open(ruta, "r", encoding="utf-8-sig") as archivo:
        return archivo.read()


def test_txt_exporta_exclusivamente_titulo_y_body(tmp_path):
    output_file = tmp_path / "informe.txt"
    contenido = {
        "topic": "Python Testing",
        "body": "Únicamente la variante solicitada.",
    }

    result_path = TxtExporter.generate(str(output_file), contenido)

    texto = _leer(result_path)
    assert "TÍTULO: Python Testing" in texto
    assert "Únicamente la variante solicitada." in texto
    assert "CONTENIDO ORIGINAL" not in texto
    assert "CONTENIDO ENRIQUECIDO" not in texto
    assert "CONTENIDO TRADUCIDO" not in texto
    assert "Resumen" not in texto
    assert "generado exitosamente" not in texto


def test_txt_contiene_solo_el_resumen_si_esa_fue_la_variante(tmp_path):
    output_file = tmp_path / "resumen.txt"

    result_path = TxtExporter.generate(
        str(output_file),
        {"topic": "Camas", "body": "Resumen ejecutivo de Camas."},
    )

    texto = _leer(result_path)
    assert "Resumen ejecutivo de Camas." in texto
    assert "municipio y ciudad" not in texto


def test_txt_es_utf8_con_bom_para_que_windows_lo_reconozca(tmp_path):
    output_file = tmp_path / "encoding.txt"

    result_path = TxtExporter.generate(str(output_file), {"topic": "Título", "body": "Contenido"})

    with open(result_path, "rb") as archivo:
        cabecera = archivo.read(3)

    assert cabecera == b"\xef\xbb\xbf"
    assert os.path.exists(result_path)


def test_txt_conserva_los_saltos_de_linea_del_body(tmp_path):
    output_file = tmp_path / "saltos.txt"

    result_path = TxtExporter.generate(
        str(output_file), {"topic": "Tema", "body": "Párrafo uno.\n\nPárrafo dos."}
    )

    texto = _leer(result_path)
    assert "Párrafo uno.\n\nPárrafo dos." in texto

def test_txt_se_escribe_en_texto_plano_sin_simbolos_de_markdown(tmp_path):
    """Si el body llega en Markdown (lo habitual con la IA), el TXT sale limpio."""
    output_file = tmp_path / "plano.txt"
    contenido = {
        "topic": "Granada",
        "body": "## Geografía\n\nLa **Vega de Granada** es fértil.",
    }

    result_path = TxtExporter.generate(str(output_file), contenido)

    texto = _leer(result_path)
    assert "Geografía" in texto
    assert "La Vega de Granada es fértil." in texto
    assert "#" not in texto
    assert "**" not in texto