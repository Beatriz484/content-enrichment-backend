from src.scraper import WikipediaScraper

if __name__ == "__main__":
    # Pedimos el tema directamente por la terminal
    tema = input("Introduce el tema que quieres buscar en Wikipedia: ")
    print(f"\nBuscando información sobre: {tema}...\n")

    try:
        scraper = WikipediaScraper(tema)
        resultado = scraper.extraer_contenido()

        print(f"=== TÍTULO: {resultado['titulo']} ===\n")

        for i, parrafo in enumerate(resultado['parrafos'], 1):
            print(f"--- Párrafo {i} ---")
            print(parrafo)
            print("\n")

    except Exception as e:
        print(f"Error: {e}")

