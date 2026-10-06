"""Tests del esquema de datos y de la matriz de validación de opciones."""
import pytest

from src.options import (
    ContentMode,
    OutputOptions,
    Variant,
    validar,
)


def _opciones(**cambios):
    base = {"tema": "python", "content_mode": ContentMode.ORIGINAL}
    base.update(cambios)
    return OutputOptions(**base)


# --- Esquema de datos -------------------------------------------------------

def test_el_esquema_tiene_valores_por_defecto():
    """Resumen, idioma, formato y nombre son opcionales."""
    opciones = OutputOptions(tema="python", content_mode=ContentMode.ORIGINAL)

    assert opciones.resumir is False
    assert opciones.idioma is None
    assert opciones.formato is None
    assert opciones.nombre is None


def test_el_esquema_es_inmutable():
    """Las opciones ya validadas no deben poder alterarse por accidente."""
    opciones = _opciones()

    with pytest.raises(Exception):
        opciones.tema = "otro"


@pytest.mark.parametrize(
    "valor,esperado",
    [
        ("original", ContentMode.ORIGINAL),
        (" ENRICHED ", ContentMode.ENRICHED),
        ("enriquecido", ContentMode.ENRICHED),
    ],
)
def test_content_mode_desde_acepta_variantes_de_entrada(valor, esperado):
    """La respuesta cruda de la CLI se normaliza a un modo del enum."""
    assert ContentMode.desde(valor) is esperado


def test_content_mode_desde_rechaza_valores_desconocidos():
    """Un modo inexistente produce un error con las opciones válidas."""
    with pytest.raises(ValueError, match="Modo de contenido no válido"):
        ContentMode.desde("resumido")


# --- Resolución de variante -------------------------------------------------

@pytest.mark.parametrize(
    "modo,resumir,esperada",
    [
        (ContentMode.ORIGINAL, False, Variant.ORIGINAL),
        (ContentMode.ORIGINAL, True, Variant.ORIGINAL_SUMMARY),
        (ContentMode.ENRICHED, False, Variant.ENRICHED),
        (ContentMode.ENRICHED, True, Variant.ENRICHED_SUMMARY),
    ],
)
def test_variante_es_el_producto_de_los_dos_ejes(modo, resumir, esperada):
    """Los ejes A y B son independientes: 2 × 2 = 4 variantes."""
    assert _opciones(content_mode=modo, resumir=resumir).variante is esperada


@pytest.mark.parametrize("variante", list(Variant))
def test_toda_variante_tiene_un_rotulo_legible(variante):
    """La variante se comunica al usuario con un texto, nunca con un código crudo."""
    assert variante.titulo.strip()
    assert variante.titulo != variante.value


def test_requiere_ia_solo_si_se_pide_enriquecer_o_resumir():
    """La variante original no necesita credenciales de IA."""
    assert _opciones().requiere_ia is False
    assert _opciones(content_mode=ContentMode.ENRICHED).requiere_ia is True
    assert _opciones(resumir=True).requiere_ia is True


# --- Matriz de validación ---------------------------------------------------

def test_validacion_correcta_no_devuelve_errores():
    """La combinación soportada pasa sin avisos."""
    assert validar(_opciones(), ia_disponible=True, traductor_disponible=False) == []


def test_tema_vacio_es_rechazado():
    """La matriz obliga a investigar un tema concreto."""
    errores = validar(_opciones(tema="   "), True, False)

    assert any("tema" in error.lower() for error in errores)


def test_modo_enriquecido_sin_ia_es_rechazado():
    """Failed: no se promete enriquecimiento que no se puede entregar."""
    errores = validar(_opciones(content_mode=ContentMode.ENRICHED), False, False)

    assert any("El modo 'enriquecido' necesita IA" in error for error in errores)


def test_resumen_sin_ia_es_rechazado():
    """Failed: el resumen también depende de la IA."""
    errores = validar(_opciones(resumir=True), False, False)

    assert any("resumen necesita IA" in error for error in errores)


def test_traduccion_sin_traductor_es_rechazado():
    """Failed: el traductor aún no está implementado por el equipo."""
    errores = validar(_opciones(idioma="fr"), True, False)

    assert any("traducción" in error for error in errores)


def test_traduccion_con_traductor_es_aceptada():
    """En cuanto se integre DeepTranslate la combinación pasa."""
    assert validar(_opciones(idioma="fr"), True, True) == []


@pytest.mark.parametrize("formato", ["txt", "pdf"])
def test_formatos_soportados_son_txt_y_pdf(formato):
    """Los dos formatos exigidos por el documento de requisitos."""
    opciones = _opciones(formato=formato, nombre="informe")

    assert validar(opciones, True, False) == []


def test_formato_no_soportado_es_rechazado():
    """Failed: solo se aceptan txt y pdf."""
    errores = validar(_opciones(formato="docx", nombre="informe"), True, False)

    assert any("no soportado" in error for error in errores)


def test_nombre_de_archivo_vacio_es_rechazado():
    """Failed: el documento exige elegir el nombre del archivo."""
    errores = validar(_opciones(formato="txt", nombre="  "), True, False)

    assert any("nombre del archivo" in error for error in errores)


def test_la_validacion_acumula_todos_los_errores():
    """El usuario recibe el listado completo, no solo el primer problema."""
    opciones = OutputOptions(
        tema="",
        content_mode=ContentMode.ENRICHED,
        resumir=True,
        idioma="fr",
        formato="docx",
        nombre="",
    )

    errores = validar(opciones, ia_disponible=False, traductor_disponible=False)

    # tema + modo + resumen + idioma + formato + nombre
    assert len(errores) == 6
