from src.exporter import DocumentExporter

if __name__ == "__main__":
    print("==================================================")
    print("       SISTEMA DE GENERACIÓN DE INFORMES          ")
    print("==================================================")

    # Inicializar orquestador
    exporter = DocumentExporter(output_dir="output")

    # Solicitar datos en consola
    user_filename = input("➤ Ingrese el nombre del archivo: ").strip()
    user_format = input("➤ Elija el formato (txt / pdf): ").strip()

    # Datos recopilados de la cadena
    sample_data = {
        "topic": "Procesamiento del Lenguaje Natural",
        "raw_text": "El NLP es un campo de la IA enfocado en la interacción entre computadoras y humanos...",
        "enriched_text": "Resumen IA:\n- Permite el análisis sintáctico y semántico de textos.\n- Utiliza modelos Transformers.",
        "translated_text": "AI Summary:\n- Enables syntactic and semantic analysis of texts.\n- Utilizes Transformers models."
    }

    # Ejecutar proceso
    is_success, response = exporter.export_content(
        file_name=user_filename,
        output_format=user_format,
        content_data=sample_data
    )

    print("\n--------------------------------------------------")
    if is_success:
        print("ESTADO: ÉXITO")
        print(f"ARCHIVO GUARDADO EN: {response}")
    else:
        print("ESTADO: FALLO")
        print(f"DETALLE: {response}")
    print("--------------------------------------------------")