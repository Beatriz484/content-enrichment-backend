from src.enricher import AiContentEnricher


def run_manual_flow():
    print("=" * 60)
    print("INTERACTIVE MANUAL FLOW: AI CONTENT ENRICHER")
    print("=" * 60)

    # 1. El sistema toma el texto guardado en la memoria
    original_text = (
        "La fotosíntesis es el proceso bioquímico mediante el cual las plantas, "
        "algas y ciertas bacterias convierten la energía solar en energía química."
    )
    print("\n[Current text in memory]:")
    print(original_text)

    enricher = AiContentEnricher()

    # 2. Enviar texto a la IA
    print("\nSending text to AI...")
    enriched_text = enricher.enrich_content(original_text)
    print("\n[Result returned by module]:")
    print(enriched_text)

    # 3. Pausa: 'Presiona ENTER para continuar'
    input("\nPause: Press ENTER to continue...")

    # 4. El sistema pregunta al usuario
    print("\nSystem question:")
    print("¿Qué versión quieres conservar?")
    print("Option 1: Enriquecida por la IA")
    print("Option 2: Original de Wikipedia")

    choice = input("Select an option (1 or 2): ").strip()

    # 5. Selección y resolución a memoria
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