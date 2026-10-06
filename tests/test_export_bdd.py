"""Escenarios Gherkin de la exportación exclusiva (TXT y PDF)."""
import os

from pytest_bdd import given, parsers, scenarios, then, when

from src.exporter import DocumentExporter

scenarios("features/export.feature")


def _leer_texto(ruta):
    with open(ruta, "r", encoding="utf-8-sig") as archivo:
        return archivo.read()


# --- Dado --------------------------------------------------------------------

@given(
    parsers.parse('un informe con título "{titulo}" y cuerpo "{cuerpo}"'),
    target_fixture="contexto",
)
def informe_completo(titulo, cuerpo, tmp_path):
    return {"directorio": tmp_path, "informe": {"topic": titulo, "body": cuerpo}, "salida": None}


@given(parsers.parse('un informe con título "{titulo}"'), target_fixture="contexto")
def informe_sin_cuerpo(titulo, tmp_path):
    return {"directorio": tmp_path, "informe": {"topic": titulo}, "salida": None}


# --- Cuando ------------------------------------------------------------------

@when(parsers.parse('exporto el informe en formato "{formato}"'))
def exportar(contexto, formato):
    contexto["salida"] = DocumentExporter(output_dir=str(contexto["directorio"])).export_content(
        file_name="informe", output_format=formato, content_data=contexto["informe"]
    )


@when(parsers.parse('intento exportar en formato "{formato}"'))
def intentar_formato(contexto, formato):
    contexto["salida"] = DocumentExporter(output_dir=str(contexto["directorio"])).export_content(
        file_name="informe", output_format=formato, content_data=contexto["informe"]
    )


@when(parsers.parse('intento exportar con el nombre "{nombre}" en formato "{formato}"'))
def intentar_nombre(contexto, nombre, formato):
    contexto["salida"] = DocumentExporter(output_dir=str(contexto["directorio"])).export_content(
        file_name=nombre, output_format=formato, content_data=contexto["informe"]
    )


# --- Entonces -----------------------------------------------------------------

def _ruta_generada(contexto):
    exito, ruta = contexto["salida"]
    assert exito is True, ruta
    assert os.path.exists(ruta), ruta
    return ruta


@then("el archivo se crea correctamente")
def archivo_creado(contexto):
    _ruta_generada(contexto)


@then(parsers.parse('el archivo contiene el título "{texto}"'))
def archivo_contiene_titulo(contexto, texto):
    assert texto in _leer_texto(_ruta_generada(contexto))


@then(parsers.parse('el archivo contiene el cuerpo "{texto}"'))
def archivo_contiene_cuerpo(contexto, texto):
    contenido = _leer_texto(_ruta_generada(contexto))
    assert texto in contenido
    # El cuerpo aparece después del título, no fusionado con él
    assert contenido.index(texto) > contenido.index("TÍTULO:")


@then(parsers.parse('el archivo no contiene "{texto}"'))
def archivo_no_contiene(contexto, texto):
    assert texto not in _leer_texto(_ruta_generada(contexto))


@then("el archivo empieza por la marca UTF-8")
def archivo_con_bom(contexto):
    with open(_ruta_generada(contexto), "rb") as archivo:
        assert archivo.read(3) == b"\xef\xbb\xbf"


@then("el informe entregado al exportador solo contiene título y cuerpo")
def contrato_minimo(contexto):
    assert set(contexto["informe"]) == {"topic", "body"}


@then(parsers.parse('la exportación falla con el mensaje "{mensaje}"'))
def exportacion_falla(contexto, mensaje):
    exito, detalle = contexto["salida"]
    assert exito is False
    assert mensaje in detalle


@then("no se crea ningún archivo")
def ningun_archivo(contexto):
    assert os.listdir(contexto["directorio"]) == []
