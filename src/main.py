"""Interfaz de línea de comandos del Content Enricher.

Flujo: formulario → validación → Wikipedia → matriz de control → exportación.

Esta capa **solo** muestra resultados y pide decisiones. La lógica de negocio
vive en ``src/options.py`` (esquema y validación) y ``src/pipeline.py``
(matriz de control); el diálogo con el usuario, en ``src/prompts.py``.
"""
import logging
import sys
from typing import Optional

from .enricher import AiContentEnricher
from .errors import ContentEnricherError
from .exporter import DocumentExporter
from .logging_config import setup_logging
from .options import OutputOptions, validar
from .pipeline import ContentPipeline, Resultado
from .prompts import confirmar, pedir_exportacion, pedir_opciones

logger = logging.getLogger(__name__)


def _crear_enricher() -> Optional[AiContentEnricher]:
    """Crea el cliente de IA o lo deja en ``None`` si faltan credenciales.

    No imprime nada: si el usuario pidió una variante que necesita IA, la
    matriz de validación ya informa con un mensaje accionable.
    """
    try:
        return AiContentEnricher()
    except ValueError as error:
        logger.warning("IA no disponible: %s", error)
        return None


def _mostrar_investigacion(investigacion: dict) -> None:
    print(f"\n=== TÍTULO: {investigacion['titulo']} ===\n")
    for indice, parrafo in enumerate(investigacion["parrafos"], 1):
        print(f"--- Párrafo {indice} ---")
        print(f"{parrafo}\n")


def _mostrar_resultado(resultado: Resultado) -> None:
    """Imprime solo los pasos que la variante elegida llegó a ejecutar."""
    print(f"➤ Variante seleccionada: {resultado.variante}\n")
    for rotulo, texto in resultado.pasos:
        print(f"=== {rotulo} ===")
        print(f"{texto}\n")


def _exportar(opciones: OutputOptions, resultado: Resultado) -> int:
    """Pide formato y nombre, y escribe el archivo con la variante exacta."""
    if not confirmar("¿Guardar el informe en disco?", True):
        print("Informe descartado.")
        logger.info("Informe descartado por el usuario.")
        return 0

    opciones = pedir_exportacion(opciones)
    formato = opciones.formato or ""
    nombre = opciones.nombre or ""

    exito, detalle = DocumentExporter(output_dir="output").export_content(
        file_name=nombre,
        output_format=formato,
        content_data=resultado.informe,
    )

    print("-" * 56)
    if exito:
        logger.info("Informe exportado a '%s'.", detalle)
        print("🟢 ESTADO: ÉXITO")
        print(f"📁 ARCHIVO GUARDADO EN: {detalle}")
    else:
        logger.error("Fallo al exportar: %s", detalle)
        print("🔴 ESTADO: FALLO")
        print(f"❌ DETALLE: {detalle}")
    print("-" * 56)
    return 0 if exito else 1


def _ejecutar() -> int:
    print("=" * 56)
    print("     CONTENT ENRICHER · INVESTIGACIÓN ASISTIDA")
    print("=" * 56)

    # 1. Formulario de opciones de respuesta ----------------------------
    opciones = pedir_opciones()

    # 2. Servicios disponibles y matriz de control ----------------------
    # Solo se necesita el cliente de IA si la variante elegida la exige.
    enricher = _crear_enricher() if opciones.requiere_ia else None
    pipeline = ContentPipeline(enricher=enricher)

    errores = validar(
        opciones,
        ia_disponible=enricher is not None,
        traductor_disponible=pipeline.translator is not None,
    )
    if errores:
        print("\n🔴 Las opciones seleccionadas no son válidas:")
        for error in errores:
            print(f"   • {error}")
        logger.error("Opciones rechazadas: %s", " | ".join(errores))
        return 1

    # 3. Investigación ---------------------------------------------------
    print(f"\n[1/3] Buscando en Wikipedia: {opciones.tema}...")
    try:
        investigacion = pipeline.investigar(opciones.tema)
    except (ValueError, ConnectionError) as error:
        print(f"🔴 No se pudo investigar el tema: {error}")
        return 1

    _mostrar_investigacion(investigacion)

    # 4. Matriz de control ------------------------------------------------
    print("[2/3] Procesando la variante seleccionada...")
    try:
        resultado = pipeline.procesar(investigacion, opciones)
    except ContentEnricherError as error:
        print(f"🔴 No se pudo generar el contenido: {error}")
        logger.error("Procesamiento abortado: %s", error)
        return 1

    _mostrar_resultado(resultado)

    # 5. Exportación -------------------------------------------------------
    print("[3/3] Exportación del informe.")
    return _exportar(opciones, resultado)


def _configurar_consola() -> None:
    """Evita que la CLI se rompa al redirigir la salida en Windows.

    En Windows, cuando stdout/stdin van por tubería (no por consola), Python
    usa la codificación regional (p. ej. cp1252) y los caracteres del interfaz
    (➤, 🟢, tildes) lanzan UnicodeEncodeError. Se fuerza UTF-8 con reemplazo
    seguro para que la aplicación nunca falle por codificación.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass

    stdin_reconfigure = getattr(sys.stdin, "reconfigure", None)
    if stdin_reconfigure:
        try:
            stdin_reconfigure(errors="replace")
        except (ValueError, OSError):
            pass


def main() -> int:
    _configurar_consola()
    setup_logging()
    try:
        return _ejecutar()
    except (KeyboardInterrupt, EOFError):
        print("\nOperación cancelada por el usuario.")
        logger.info("Operación cancelada por el usuario.")
        return 130


if __name__ == "__main__":  # pragma: no cover - punto de entrada, no se importa en tests
    raise SystemExit(main())
