import sys
from pathlib import Path

# Permite resolver importaciones de 'src' independientemente de cómo se lance el script
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.enricher import AiContentEnricher
from src.logging_config import setup_logging


def run_manual_flow():
    print("=" * 60)
    print("INTERACTIVE LIVE DEMO: AI CONTENT ENRICHER")
    print("=" * 60)

    # 1. Solicita dinámicamente el texto al usuario por terminal
    original_text = ""
    while not original_text:
        original_text = input("\nIntroduce el texto o concepto a enriquecer: ").strip()
        if not original_text:
            print("⚠️ El texto no puede estar vacío. Por favor, escribe un concepto.")

    print("\n[Texto capturado dinámicamente]:")
    print(original_text)

    enricher = AiContentEnricher()

    # 2. Solicitud de enriquecimiento a la IA
    print("\n⏳ Conectando con la IA para enriquecer el texto (espera unos segundos)...")
    enriched_text = enricher.enrich_content(original_text)

    print("\n[Result returned by module]:")
    print(enriched_text)

    # 3. Pausa controlada para revisión pedagógica
    input("\n👉 Haz clic aquí y pulsa ENTER para elegir versión...")

    print("\nSystem question:")
    print("¿Qué versión quieres conservar?")
    print("Option 1: Enriquecida por la IA")
    print("Option 2: Original")

    # Bucle que evita que un ENTER en blanco se salte el menú
    choice = ""
    while choice not in ["1", "2"]:
        choice = input("Select an option (1 or 2): ").strip()
        if choice not in ["1", "2"]:
            print("[AVISO] Por favor, introduce '1' o '2' y pulsa ENTER.")

    # 5. Asignación definitiva en memoria
    if choice == "1":
        final_memory_text = enriched_text
        print("\n✓ Selected AI enriched text.")
    else:
        final_memory_text = original_text
        print("\n✓ Selected original text.")

    print("\n[Final text ready in memory for next step]:")
    print(final_memory_text)
    print("\n" + "=" * 60)


if __name__ == "__main__":
    setup_logging()
    run_manual_flow()