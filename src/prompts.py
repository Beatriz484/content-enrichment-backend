"""Formulario de opciones de respuesta: toda la interacción con el usuario.

Solo lee ``input()`` y escribe en pantalla. No contiene lógica de negocio:
esa vive en ``src/options.py`` (modelo + validación) y en ``src/pipeline.py``
(matriz de control), de modo que ambas se prueban sin simular la terminal.
"""
import logging
from dataclasses import replace
from typing import Optional

from .options import ContentMode, FORMATOS_VALIDOS, OutputOptions

logger = logging.getLogger(__name__)

RESPUESTAS_AFIRMATIVAS = ("s", "si", "sí", "y", "yes")
RESPUESTAS_NEGATIVAS = ("n", "no")


def preguntar_texto(mensaje: str) -> str:
    """Pide un valor no vacío, repitiendo la pregunta si hace falta."""
    while True:
        respuesta = input(mensaje).strip()
        if respuesta:
            return respuesta
        print("⚠️  El valor no puede estar vacío. Inténtalo de nuevo.")


def confirmar(mensaje: str, por_defecto: bool = True) -> bool:
    """Pregunta sí/no con reintento hasta obtener una respuesta válida.

    Un ``Enter`` aplica ``por_defecto``; una respuesta explícita manda siempre
    sobre ese valor por defecto.
    """
    while True:
        respuesta = input(f"{mensaje} (sí/no): ").strip().lower()
        if not respuesta:
            return por_defecto
        if respuesta in RESPUESTAS_AFIRMATIVAS:
            return True
        if respuesta in RESPUESTAS_NEGATIVAS:
            return False
        print("⚠️  Responde 'sí' o 'no'.")


def pedir_modo() -> ContentMode:
    """Pide el modo de contenido hasta obtener un modo válido."""
    print("\n➤ Modo de contenido:")
    print("   [1] Solo texto original (tal cual Wikipedia)")
    print("   [2] Contenido enriquecido con IA")
    while True:
        respuesta = input("   Elige (1 / 2): ").strip()
        if respuesta in ("1", "2"):
            return ContentMode.ORIGINAL if respuesta == "1" else ContentMode.ENRICHED
        print("⚠️  Responde 1 o 2.")


def pedir_idioma() -> Optional[str]:
    """Pide el idioma de traducción. ``Enter`` mantiene el idioma original."""
    respuesta = input("➤ Idioma de traducción (ej. en, fr — Enter = original): ").strip()
    return respuesta.lower() if respuesta else None


def pedir_formato() -> str:
    """Pide el formato del informe hasta que sea 'txt' o 'pdf'."""
    while True:
        formato = input("➤ Formato del informe (txt / pdf): ").strip().lower()
        if formato in FORMATOS_VALIDOS:
            return formato
        print(f"⚠️  Formato no válido. Usa uno de: {', '.join(FORMATOS_VALIDOS)}.")


def pedir_opciones() -> OutputOptions:
    """Recorre el formulario completo y devuelve las opciones capturadas."""
    print("\n" + "─" * 56)
    print("     FORMULARIO DE OPCIONES DE RESPUESTA")
    print("─" * 56)
    tema = preguntar_texto("\n➤ Tema a investigar en Wikipedia: ")
    modo = pedir_modo()
    resumen = confirmar("➤ ¿Generar un resumen del contenido elegido?", False)
    idioma = pedir_idioma()
    logger.info(
        "Opciones capturadas: tema='%s', modo='%s', resumen=%s, idioma=%s.",
        tema,
        modo.value,
        resumen,
        idioma or "original",
    )
    return OutputOptions(tema=tema, content_mode=modo, resumir=resumen, idioma=idioma)


def pedir_exportacion(opciones: OutputOptions) -> OutputOptions:
    """Añade formato y nombre de archivo a las opciones ya capturadas."""
    return replace(
        opciones,
        formato=pedir_formato(),
        nombre=preguntar_texto("➤ Nombre del archivo (sin extensión): "),
    )
