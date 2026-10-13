"""Convierte texto en Markdown (el que suele devolver la IA) en texto plano."""
import re


def _es_separador_de_tabla(linea: str) -> bool:
    """Detecta la línea de guiones de una tabla: |------|------|"""
    return re.fullmatch(r"\|[\s\-:|]+\|", linea) is not None


def _es_linea_separadora(linea: str) -> bool:
    """Detecta las líneas ---, *** o ___ que separan secciones."""
    return re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", linea) is not None


def _limpiar_linea(linea: str) -> str:
    """Quita los símbolos de Markdown de una sola línea."""
    linea = re.sub(r"^#{1,6}\s+", "", linea)  # títulos: ## Granada
    linea = re.sub(r"^>\s?", "", linea)  # citas: > texto
    linea = re.sub(r"^\*\s+", "- ", linea)  # listas con * pasan a -
    linea = re.sub(r"\*\*(.+?)\*\*", r"\1", linea)  # negrita: **texto**
    linea = re.sub(r"__(.+?)__", r"\1", linea)  # negrita: __texto__
    linea = re.sub(r"\*(.+?)\*", r"\1", linea)  # cursiva: *texto*
    linea = re.sub(r"`([^`]*)`", r"\1", linea)  # código: `texto`
    linea = re.sub(r"\[\[(\d+)\]\]\(#[^)]*\)", r"[\1]", linea)  # referencias: [[1]](#ref1)
    linea = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", linea)  # enlaces
    return linea


def _convertir_fila_de_tabla(linea: str) -> str:
    """Pasa '| a | b |' a 'a - b'."""
    celdas = [celda.strip() for celda in linea.strip("|").split("|")]
    return " - ".join(celdas)


def markdown_to_plain_text(texto: str) -> str:
    """Devuelve el texto sin símbolos de Markdown, conservando párrafos y listas."""
    lineas_resultado = []

    for linea in texto.split("\n"):
        linea = linea.rstrip()

        if _es_separador_de_tabla(linea):
            continue  # la línea |---|---| no aporta nada
        if _es_linea_separadora(linea):
            lineas_resultado.append("")
        elif linea.startswith("|"):
            lineas_resultado.append(_limpiar_linea(_convertir_fila_de_tabla(linea)))
        else:
            lineas_resultado.append(_limpiar_linea(linea))

    resultado = "\n".join(lineas_resultado)
    return re.sub(r"\n{3,}", "\n\n", resultado)  # como mucho una línea en blanco