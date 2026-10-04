import sys
from pathlib import Path

# Permite resolver importaciones de 'src' independientemente de cómo se lance el script
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.enricher import AiContentEnricher


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
    print("\nSending text to AI...")
    enriched_text = enricher.enrich_content(original_text)

    print("\n[Result returned by module]:")
    print(enriched_text)

    # 3. Pausa controlada para revisión pedagógica
    input("\nPause: Press ENTER to continue...")

    # 4. Decisión interactiva del usuario
    print("\nSystem question:")
    print("¿Qué versión quieres conservar?")
    print("Option 1: Enriquecida por la IA")
    print("Option 2: Original")

    choice = input("Select an option (1 or 2): ").strip()

    # 5. Asignación definitiva en memoria
    if choice == "1":
        final_memory_text = enriched_text
        print("\n✔ Selected AI enriched text.")
    else:
        final_memory_text = original_text
        print("\n✔ Selected original text.")

    print("\n[Final text ready in memory for next step]:")
    print(final_memory_text)
    print("\n" + "=" * 60)


if __name__ == "__main__":
    run_manual_flow()