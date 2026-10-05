"""Interfaz de línea de comandos del Content Enricher.

Flujo: tema → Wikipedia → IA → resumen → traducción → exportación (txt/pdf).
Esta capa solo se preocupa de mostrar resultados y pedir decisiones al usuario;
toda la lógica de negocio vive en ``src/pipeline.py``.
"""
import logging
from typing import Optional

from .enricher import AiContentEnricher
from .exporter import DocumentExporter
from .logging_config import setup_logging
from .pipeline import ContentPipeline

logger = logging.getLogger(__name__)

FORMATOS_VALIDOS = ("txt", "pdf")
RESPUESTAS_AFIRMATIVAS = ("", "s", "si", "sí", "y", "yes")


def _preguntar_texto(mensaje: str) -> str:
    """Pide un valor no vacío, repitiendo la pregunta si hace falta."""
    while True:
        respuesta = input(mensaje).strip()
        if respuesta:
            return respuesta
        print("⚠️  El valor no puede estar vacío. Inténtalo de nuevo.")


def _confirmar(mensaje: str, por_defecto: bool = True) -> bool:
    """Pregunta sí/no con reintento hasta obtener una respuesta válida."""
    while True:
        respuesta = input(f"{mensaje} (sí/no): ").strip().lower()
        if respuesta in RESPUESTAS_AFIRMATIVAS:
            return por_defecto
        if respuesta in ("n", "no"):
            return False
        print("⚠️  Responde 'sí' o 'no'.")


def _pedir_formato() -> str:
    """Pide el formato del informe hasta que sea 'txt' o 'pdf'."""
    while True:
        formato = input("➤ Formato del informe (txt / pdf): ").strip().lower()
        if formato in FORMATOS_VALIDOS:
            return formato
        print(f"⚠️  Formato no válido. Usa uno de: {', '.join(FORMATOS_VALIDOS)}.")


def _crear_enricher() -> Optional[AiContentEnricher]:
    """Crea el cliente de IA o degrada elegante si no hay credenciales."""
    try:
        return AiContentEnricher()
    except ValueError as error:
        logger.warning("IA no disponible: %s", error)
        print(f"⚠️  IA no disponible: {error}")
        print("   El informe se generará únicamente con el contenido de Wikipedia.\n")
        return None


def _mostrar_investigacion(investigacion: dict) -> None:
    print(f"\n=== TÍTULO: {investigacion['titulo']} ===\n")
    for indice, parrafo in enumerate(investigacion["parrafos"], 1):
        print(f"--- Párrafo {indice} ---")
        print(f"{parrafo}\n")


def _ejecutar() -> int:
    print("=" * 56)
    print("     CONTENT ENRICHER · INVESTIGACIÓN ASISTIDA")
    print("=" * 56)

    tema = _preguntar_texto("\n➤ Tema a investigar en Wikipedia: ")
    idioma = _preguntar_texto("➤ Idioma de traducción (ej. en, fr): ")
    logger.info("Solicitud recibida: tema='%s', idioma='%s'.", tema, idioma)

    pipeline = ContentPipeline(enricher=_crear_enricher())

    # 1. Investigación -------------------------------------------------
    print(f"\n[1/4] Buscando en Wikipedia: {tema}...")
    try:
        investigacion = pipeline.investigar(tema)
    except (ValueError, ConnectionError) as error:
        print(f"🔴 No se pudo investigar el tema: {error}")
        return 1

    _mostrar_investigacion(investigacion)

    # 2. Enriquecimiento -----------------------------------------------
    print("[2/4] Enriqueciendo el contenido con IA...")
    enriquecido = pipeline.enriquecer(investigacion["texto"])
    print(f"\n{enriquecido}\n")

    # 3. Resumen (extra ⭐) ---------------------------------------------
    resumen = ""
    if _confirmar("[3/4] ¿Generar un resumen del contenido enriquecido?", True):
        resumen = pipeline.resumir(enriquecido)
        if resumen:
            print(f"\n{resumen}\n")
        else:
            print("⚠️  No se generó resumen (IA no disponible).")
    else:
        logger.info("Resumen omitido por el usuario.")

    # 4. Traducción ------------------------------------------------------
    print(f"[4/4] Traduciendo al idioma '{idioma}'...")
    traducido = pipeline.traducir(enriquecido, idioma)
    if traducido:
        print(f"\n{traducido}\n")
    else:
        print("⚠️  Traducción pendiente: el módulo de traducción aún no está disponible.")
        print("   El informe se guardará con la sección de traducción vacía.\n")

    # 5. Exportación (extra ⭐) -------------------------------------------
    if not _confirmar("¿Guardar el informe en disco?", True):
        print("Informe descartado.")
        logger.info("Informe descartado por el usuario.")
        return 0

    formato = _pedir_formato()
    nombre = _preguntar_texto("➤ Nombre del archivo (sin extensión): ")

    content_data = pipeline.construir_content_data(
        titulo=investigacion["titulo"],
        texto_original=investigacion["texto"],
        texto_enriquecido=enriquecido,
        texto_traducido=traducido,
        resumen=resumen,
    )

    resultado, detalle = DocumentExporter(output_dir="output").export_content(
        file_name=nombre,
        output_format=formato,
        content_data=content_data,
    )

    print("-" * 56)
    if resultado:
        logger.info("Informe exportado a '%s'.", detalle)
        print("🟢 ESTADO: ÉXITO")
        print(f"📁 ARCHIVO GUARDADO EN: {detalle}")
    else:
        logger.error("Fallo al exportar: %s", detalle)
        print("🔴 ESTADO: FALLO")
        print(f"❌ DETALLE: {detalle}")
    print("-" * 56)
    return 0 if resultado else 1


def main() -> int:
    setup_logging()
    try:
        return _ejecutar()
    except (KeyboardInterrupt, EOFError):
        print("\nOperación cancelada por el usuario.")
        logger.info("Operación cancelada por el usuario.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
