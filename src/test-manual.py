from src.scraper import WikipediaScraper

if __name__ == "__main__":
    print("--- PRUEBA MANUAL DEL SCRAPER ---")
    tema_prueba = input("Introduce un tema para buscar en Wikipedia: ")

    try:
        buscador = WikipediaScraper(tema_prueba)
        print(f"\nBuscando información sobre '{tema_prueba}'...")
        resultado = buscador.extraer_contenido()

        print(f"\n[TÍTULO]: {resultado['titulo']}\n")
        print(f"[PÁRRAFOS EXTRAÍDOS ({len(resultado['parrafos'])} en total)]:\n")

        for i, parrafo in enumerate(resultado['parrafos'], 1):
            print(f"--- Párrafo {i} ---")
            print(parrafo)
            print()

    except Exception as e:
        print(f"\n[ERROR]: {e}")
