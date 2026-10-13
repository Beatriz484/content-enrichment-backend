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


def ask_text(message: str) -> str:
    while True:
        answer = input(message).strip()
        if answer:
            return answer
        print("⚠️  El valor no puede estar vacío. Inténtalo de nuevo.")


def confirm(message: str, default: bool = True) -> bool:
    while True:
        answer = input(f"{message} (sí/no): ").strip().lower()
        if not answer:
            return default
        if answer in AFFIRMATIVE_ANSWERS:
            return True
        if answer in NEGATIVE_ANSWERS:
            return False
        print("⚠️  Responde 'sí' o 'no'.")


def ask_choice(message: str, options: Tuple[str, ...]) -> str:
    while True:
        answer = input(message).strip()
        if answer in options:
            return answer
        print(f"⚠️  Opción no válida. Por favor, introduce una de: {', '.join(options)}.")


def ask_language() -> Optional[str]:
    answer = input("➤ Idioma de traducción (ej. en, fr — Enter = original): ").strip()
    return answer.lower() if answer else None


def ask_format() -> str:
    while True:
        output_format = input("➤ Formato del informe (txt / pdf): ").strip().lower()
        if output_format in VALID_FORMATS:
            return output_format
        print(f"⚠️  Formato no válido. Usa uno de: {', '.join(VALID_FORMATS)}.")


def research_topic(topic: str) -> Dict[str, Any]:
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
    print(f"\n=== TÍTULO: {research['title']} ===\n")
    for index, paragraph in enumerate(research["paragraphs"], 1):
        print(f"--- Párrafo {index} ---")
        print(f"{paragraph}\n")


def show_section(label: str, content: str) -> None:
    print(f"=== {label} ===")
    print(f"{content}\n")


def enrich_content(enricher: AiContentEnricher, text: str) -> str:
    enriched = enricher.enrich_content(text)
    logger.info("IA: contenido enriquecido generado.")
    return enriched


def summarize_content(enricher: AiContentEnricher, text: str) -> str:
    summary = enricher.summarize_content(text)
    logger.info("IA: resumen generado.")
    return summary


def translate_content(
    translator: DeepTranslateTranslator,
    text: str,
    language: str,
) -> str:
    translated = translator.translate(text, language)
    logger.info("Traducción al idioma '%s' completada.", language)
    return translated


def export_report(title: str, content: str) -> int:
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


def _create_enricher() -> Optional[AiContentEnricher]:
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

    topic = ask_text("\n➤ Tema a investigar en Wikipedia: ")

    print(f"\n[1/5] Buscando en Wikipedia: {topic}...")
    try:
        research = research_topic(topic)
    except (ValueError, ConnectionError) as error:
        print(f"🔴 No se pudo investigar el tema: {error}")
        return 1
    show_investigation(research)
    logger.info("Opción capturada: tema='%s'.", topic)

    enricher = _create_enricher()
    if enricher:
        print("[2/5] Enriqueciendo el contenido con IA...")
        enriched = enrich_content(enricher, research["text"])
        show_section("CONTENIDO ENRIQUECIDO (IA)", enriched)

        print("¿Deseas conservar el contenido enriquecido por IA o el original de Wikipedia?")
        print("  1. Texto original de Wikipedia")
        print("  2. Contenido enriquecido por IA")

        if ask_choice("➤ Elige una opción (1 / 2): ", ("1", "2")) == "1":
            enriched = research["text"]
            print("✓ Se mantendrá el texto original de Wikipedia.\n")
        else:
            print("✓ Se continuará con el contenido enriquecido por IA.\n")
    else:
        enriched = ""
        print("[2/5] Enriquecimiento omitido: no hay credenciales de IA.")

    want_summary = False
    if enricher:
        want_summary = confirm("➤ ¿Generar un resumen del contenido con IA?", False)
        logger.info("Opción capturada: resumen=%s.", want_summary)

    summary = ""
    if want_summary:
        print("[3/5] Generando el resumen con IA...")
        summary = summarize_content(enricher, enriched or research["text"])
        show_section("RESUMEN (IA)", summary)
    else:
        print("[3/5] Resumen omitido (no se solicitó).")

    language = ask_language()
    logger.info("Opción capturada: idioma=%s.", language or "original")

    translated = ""
    if language:
        print(f"[4/5] Traduciendo el contenido al idioma '{language}'...")
        content = summary or enriched or research["text"]
        try:
            translated = translate_content(DeepTranslateTranslator(), content, language)
            show_section(f"CONTENIDO TRADUCIDO ({language.upper()})", translated)
        except ServiceUnavailableError as error:
            print(f"⚠️  Traducción omitida: {error}")
            logger.warning("Traducción omitida: %s", error)
    else:
        print("[4/5] Traducción omitida (idioma original).")

    print("[5/5] Exportación del informe.")
    final_content = translated or summary or enriched or research["text"]
    return export_report(research["title"], final_content)


def _setup_console() -> None:
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
