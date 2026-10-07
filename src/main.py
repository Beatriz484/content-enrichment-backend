"""Interfaz de línea de comandos del Content Enricher.

Flujo: tema → Wikipedia → enriquecimiento IA → resumen (si se pide) →
traducción (siempre la última petición) → exportación de **un único resultado**.

Cada decisión del usuario se pregunta en el momento en el que le toca: el tema
abre el proceso, el resumen se ofrece tras ver el contenido enriquecido y el
idioma se pide justo antes de traducir. El archivo final recibe el último
eslabón de la cadena realmente generado, sin preguntar qué partes guardar.

Esta capa **solo** muestra resultados y pide decisiones al usuario. La lógica de
cada servicio vive en su módulo: ``src/scraper.py`` (extracción),
``src/enricher.py`` (IA), ``src/translator.py`` (traducción) y
``src/exporter/`` (archivos). El diálogo con el usuario vive aquí mismo, de
forma simplificada, para no dispersar la CLI en varios ficheros.
"""
import logging
import sys
from typing import Any, Dict, Optional, Tuple

from .enricher import AiContentEnricher
from .errors import ServiceUnavailableError
from .exporter import DocumentExporter
from .logging_config import setup_logging
from .scraper import WikipediaScraper
from .translator import DeepTranslateTranslator

logger = logging.getLogger(__name__)

VALID_FORMATS: Tuple[str, ...] = ("txt", "pdf")
AFFIRMATIVE_ANSWERS: Tuple[str, ...] = ("s", "si", "sí", "y", "yes")
NEGATIVE_ANSWERS: Tuple[str, ...] = ("n", "no")
RULE = "-" * 56


# --- Diálogo con el usuario -------------------------------------------------

def ask_text(message: str) -> str:
    """Pide un valor no vacío, repitiendo la pregunta si hace falta."""
    while True:
        answer = input(message).strip()
        if answer:
            return answer
        print("⚠️  El valor no puede estar vacío. Inténtalo de nuevo.")


def confirm(message: str, default: bool = True) -> bool:
    """Pregunta sí/no con reintento hasta obtener una respuesta válida.

    Un ``Enter`` aplica ``default``; una respuesta explícita manda siempre
    sobre ese valor por defecto.
    """
    while True:
        answer = input(f"{message} (sí/no): ").strip().lower()
        if not answer:
            return default
        if answer in AFFIRMATIVE_ANSWERS:
            return True
        if answer in NEGATIVE_ANSWERS:
            return False
        print("⚠️  Responde 'sí' o 'no'.")


def ask_language() -> Optional[str]:
    """Pide el idioma de traducción. ``Enter`` mantiene el idioma original."""
    answer = input("➤ Idioma de traducción (ej. en, fr — Enter = original): ").strip()
    return answer.lower() if answer else None


def ask_format() -> str:
    """Pide el formato del informe hasta que sea 'txt' o 'pdf'."""
    while True:
        output_format = input("➤ Formato del informe (txt / pdf): ").strip().lower()
        if output_format in VALID_FORMATS:
            return output_format
        print(f"⚠️  Formato no válido. Usa uno de: {', '.join(VALID_FORMATS)}.")


# --- Pasos del flujo --------------------------------------------------------

def research_topic(topic: str) -> Dict[str, Any]:
    """Extrae título y primeros párrafos de Wikipedia.

    Returns:
        ``{"title": str, "paragraphs": list[str], "text": str}``

    Raises:
        ValueError: El artículo no existe.
        ConnectionError: Fallo de conexión con Wikipedia.
    """
    try:
        result = WikipediaScraper(topic).extract_content()
    except (ValueError, ConnectionError) as error:
        logger.error("Wikipedia: %s", error)
        raise

    paragraphs = result["paragraphs"]
    logger.info(
        "Wikipedia: extraídos %s párrafos de '%s'.",
        len(paragraphs),
        result["title"],
    )
    return {
        "title": result["title"],
        "paragraphs": paragraphs,
        "text": "\n\n".join(paragraphs),
    }


def show_investigation(research: Dict[str, Any]) -> None:
    """Muestra en terminal el título y los párrafos extraídos."""
    print(f"\n=== TÍTULO: {research['title']} ===\n")
    for index, paragraph in enumerate(research["paragraphs"], 1):
        print(f"--- Párrafo {index} ---")
        print(f"{paragraph}\n")


def show_section(label: str, content: str) -> None:
    """Muestra en terminal una sección de contenido con su rótulo."""
    print(f"=== {label} ===")
    print(f"{content}\n")


def enrich_content(enricher: AiContentEnricher, text: str) -> str:
    """Amplía el texto con IA y deja constancia en el log."""
    enriched = enricher.enrich_content(text)
    logger.info("IA: contenido enriquecido generado.")
    return enriched


def summarize_content(enricher: AiContentEnricher, text: str) -> str:
    """Genera un resumen del texto con IA y deja constancia en el log."""
    summary = enricher.summarize_content(text)
    logger.info("IA: resumen generado.")
    return summary


def translate_content(
    translator: DeepTranslateTranslator,
    text: str,
    language: str,
) -> str:
    """Traduce el texto al idioma indicado y deja constancia en el log.

    Raises:
        ServiceUnavailableError: mientras ``src/translator.py`` no esté entregado.
    """
    translated = translator.translate(text, language)
    logger.info("Traducción al idioma '%s' completada.", language)
    return translated


# --- Exportación ------------------------------------------------------------

def export_report(title: str, content: str) -> int:
    """Pide si guardar, en qué formato y con qué nombre, y escribe el archivo.

    El informe es **unicamente** el resultado final de la cadena de procesado:
    no se pregunta qué partes incluir porque solo hay una respuesta posible.
    """
    if not confirm("¿Guardar el informe en disco?", True):
        print("Informe descartado.")
        logger.info("Informe descartado por el usuario.")
        return 0

    output_format = ask_format()
    file_name = ask_text("➤ Nombre del archivo (sin extensión): ")

    success, detail = DocumentExporter(output_dir="output").export_content(
        file_name=file_name,
        output_format=output_format,
        content_data={"topic": title, "body": content.strip()},
    )

    print(RULE)
    if success:
        logger.info("Informe exportado a '%s'.", detail)
        print("🟢 ESTADO: ÉXITO")
        print(f"📁 ARCHIVO GUARDADO EN: {detail}")
    else:
        logger.error("Fallo al exportar: %s", detail)
        print("🔴 ESTADO: FALLO")
        print(f"❌ DETALLE: {detail}")
    print(RULE)
    return 0 if success else 1


# --- Orquestación -----------------------------------------------------------

def _create_enricher() -> Optional[AiContentEnricher]:
    """Crea el cliente de IA o lo deja en ``None`` si faltan credenciales.

    En ese caso se avisa en la terminal y el flujo continúa solo con el texto
    original: sin IA no hay enriquecimiento ni resumen.
    """
    try:
        return AiContentEnricher()
    except ValueError as error:
        logger.warning("IA no disponible: %s", error)
        print(f"⚠️  IA no disponible: {error}")
        print("   El flujo continuará solo con el texto original.")
        return None


def _run() -> int:
    print("=" * 56)
    print("     CONTENT ENRICHER · INVESTIGACIÓN ASISTIDA")
    print("=" * 56)

    # 1. Interacción: solo el tema abre el proceso ---------------------------
    topic = ask_text("\n➤ Tema a investigar en Wikipedia: ")

    # 2. Scraping ------------------------------------------------------------
    print(f"\n[1/5] Buscando en Wikipedia: {topic}...")
    try:
        research = research_topic(topic)
    except (ValueError, ConnectionError) as error:
        print(f"🔴 No se pudo investigar el tema: {error}")
        return 1
    show_investigation(research)
    logger.info("Opción capturada: tema='%s'.", topic)

    # 3. Enriquecimiento IA --------------------------------------------------
    # Los resultados de Wikipedia ya están en pantalla: ahora sí se piden
    # las acciones adicionales (primero el resumen, luego el idioma).
    enricher = _create_enricher()
    if enricher:
        print("[2/5] Enriqueciendo el contenido con IA...")
        enriched = enrich_content(enricher, research["text"])
        show_section("CONTENIDO ENRIQUECIDO (IA)", enriched)
    else:
        enriched = ""
        print("[2/5] Enriquecimiento omitido: no hay credenciales de IA.")

    # 4. Resumen (extra) -----------------------------------------------------
    want_summary = False
    if enricher:
        want_summary = confirm("➤ ¿Generar un resumen del contenido con IA?", False)
        logger.info("Opción capturada: resumen=%s.", want_summary)

    summary = ""
    if want_summary:
        print("[3/5] Generando el resumen con IA...")
        # El resumen se calcula sobre el contenido enriquecido, si existe.
        summary = summarize_content(enricher, enriched or research["text"])
        show_section("RESUMEN (IA)", summary)
    else:
        print("[3/5] Resumen omitido (no se solicitó).")

    # 5. Traducción: la última petición del usuario y el último proceso ------
    language = ask_language()
    logger.info("Opción capturada: idioma=%s.", language or "original")

    translated = ""
    if language:
        print(f"[4/5] Traduciendo el contenido al idioma '{language}'...")
        # La traducción se aplica siempre al final, sobre el contenido resultante.
        content = summary or enriched or research["text"]
        try:
            translated = translate_content(DeepTranslateTranslator(), content, language)
            show_section(f"CONTENIDO TRADUCIDO ({language.upper()})", translated)
        except ServiceUnavailableError as error:
            print(f"⚠️  Traducción omitida: {error}")
            logger.warning("Traducción omitida: %s", error)
    else:
        print("[4/5] Traducción omitida (idioma original).")

    # 6. Exportación: un único resultado ------------------------------------
    print("[5/5] Exportación del informe.")
    # El archivo recibe el último eslabón realmente generado de la cadena
    # traducción → resumen → enriquecido → texto original.
    final_content = translated or summary or enriched or research["text"]
    return export_report(research["title"], final_content)


def _setup_console() -> None:
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
    _setup_console()
    setup_logging()
    try:
        return _run()
    except (KeyboardInterrupt, EOFError):
        print("\nOperación cancelada por el usuario.")
        logger.info("Operación cancelada por el usuario.")
        return 130


if __name__ == "__main__":  # pragma: no cover - punto de entrada, no se importa en tests
    raise SystemExit(main())
