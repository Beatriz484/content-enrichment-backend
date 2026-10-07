"""Tests del exportador TXT: la variante pedida, y solo la variante pedida."""
import os

from src.exporter.txt_exporter import TxtExporter


def _leer(ruta):
    # utf-8-sig descarta el BOM: así se comprueba el contenido real del archivo
    with open(ruta, "r", encoding="utf-8-sig") as archivo:
        return archivo.read()


def test_txt_exporta_exclusivamente_titulo_y_body(tmp_path):
    """El archivo no contiene ninguna sección ni nota que no se pidiera."""
    output_file = tmp_path / "informe.txt"
    contenido = {
        "topic": "Python Testing",
        "body": "Únicamente la variante solicitada.",
    }

    result_path = TxtExporter.generate(str(output_file), contenido)

    texto = _leer(result_path)
    assert "TÍTULO: Python Testing" in texto
    assert "Únicamente la variante solicitada." in texto
    # Nada del texto original ni de secciones antiguas
    assert "CONTENIDO ORIGINAL" not in texto
    assert "CONTENIDO ENRIQUECIDO" not in texto
    assert "CONTENIDO TRADUCIDO" not in texto
    assert "Resumen" not in texto
    assert "generado exitosamente" not in texto


def test_txt_contiene_solo_el_resumen_si_esa_fue_la_variante(tmp_path):
    """Caso 4 del documento: 'solo resumen' no arrastra el texto base."""
    output_file = tmp_path / "resumen.txt"

    result_path = TxtExporter.generate(
        str(output_file),
        {"topic": "Camas", "body": "Resumen ejecutivo de Camas."},
    )

    texto = _leer(result_path)
    assert "Resumen ejecutivo de Camas." in texto
    assert "municipio y ciudad" not in texto


def test_txt_es_utf8_con_bom_para_que_windows_lo_reconozca(tmp_path):
    """Sin BOM Windows abre el archivo como ANSI y las tildes salen corruptas."""
    output_file = tmp_path / "encoding.txt"

    result_path = TxtExporter.generate(str(output_file), {"topic": "Título", "body": "Contenido"})

    with open(result_path, "rb") as archivo:
        cabecera = archivo.read(3)

    assert cabecera == b"\xef\xbb\xbf"
    assert os.path.exists(result_path)


def test_txt_conserva_los_saltos_de_linea_del_body(tmp_path):
    """Los párrafos del body se mantienen tal cual, sin fusionarse."""
    output_file = tmp_path / "saltos.txt"

    result_path = TxtExporter.generate(
        str(output_file), {"topic": "Tema", "body": "Párrafo uno.\n\nPárrafo dos."}
    )

    texto = _leer(result_path)
    assert "Párrafo uno.\n\nPárrafo dos." in texto
