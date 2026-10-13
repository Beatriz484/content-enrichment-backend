import logging
import sys
from typing import Any, Dict

from .errors import ServiceUnavailableError
from .exporter import DocumentExporter
from .logging_config import setup_logging
from .pipeline import (
    _create_enricher,
    enrich_content,
    get_topic_suggestions,
    research_topic,
    summarize_content,
    translate_content,
)
from .prompts import (
    RULE,
    ask_choice,
    ask_format,
    ask_text,
    ask_translation_language,
    confirm,
    show_investigation,
    show_section,
)
from .translation import DeepTranslateTranslator

logger = logging.getLogger(__name__)


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


def _run() -> int:
    print("=" * 56)
    print("     CONTENT ENRICHER · INVESTIGACIÓN ASISTIDA")
    print("=" * 56)

    topic = ask_text("\n➤ Tema a investigar en Wikipedia: ")

    while True:
        print(f"\n[1/5] Buscando en Wikipedia: {topic}...")
        try:
            research = research_topic(topic)

            # Si se extrajo el artículo pero está vacío (página de desambiguación)
            if not research["text"].strip():
                print(f"⚠️  '{topic}' es una página de desambiguación o no contiene texto.")

                # Obtenemos opciones alternativas de la API de Wikipedia
                opciones = get_topic_suggestions(topic, limit=5)

                if opciones:
                    print("Elige una de las opciones disponibles:")
                    for i, op in enumerate(opciones, 1):
                        print(f"  {i}. {op}")
                    print("  0. Escribir otro tema manualmente")

                    val_opciones = tuple(str(i) for i in range(len(opciones) + 1))
                    eleccion = ask_choice(f"\n➤ Elige una opción (0-{len(opciones)}): ", val_opciones)

                    if eleccion == "0":
                        topic = ask_text("\n➤ Tema a investigar en Wikipedia: ")
                        continue
                    else:
                        topic = opciones[int(eleccion) - 1]
                        continue
                else:
                    topic = ask_text("\n➤ No hay alternativas. Escribe otro tema: ")
                    continue

            break
        except (ValueError, ConnectionError) as error:
            print(f"🔴 No se pudo investigar el tema: {error}")
            topic = ask_text("\n➤ Tema a investigar en Wikipedia: ")
            continue

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

    language = ask_translation_language()
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
