import sys
from pathlib import Path

# Añadir la raíz al PATH para que reconozca el paquete 'src'
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.exporter import DocumentExporter

if __name__ == "__main__":
    print("==================================================")
    print("       SISTEMA DE GENERACIÓN DE INFORMES          ")
    print("==================================================")

    # 1. Inicializar el orquestador (creará la carpeta output en la raíz)
    exporter = DocumentExporter(output_dir="output")

    # 2. Solicitar datos reales al usuario por consola
    user_filename = input("➤ Ingrese el nombre del archivo (ej. mi_reporte): ").strip()
    user_format = input("➤ Elija el formato (txt / pdf): ").strip()

    # 3. Datos simulados del flujo
    sample_data = {
        "topic": "Procesamiento del Lenguaje Natural",
        "raw_text": "El NLP es un campo de la IA enfocado en la interacción entre computadoras y humanos...",
        "enriched_text": "Resumen IA:\nPermite el análisis sintáctico y semántico de textos.\nUtiliza modelos Transformers.",
        "translated_text": "AI Summary:\nEnables syntactic and semantic analysis of texts.\nUtilizes Transformers models."
    }

    # 4. Ejecutar el proceso de exportación real
    print("\nProcesando y generando archivo...")
    is_success, response = exporter.export_content(
        file_name=user_filename,
        output_format=user_format,
        content_data=sample_data
    )

    # 5. Mostrar resultados en pantalla
    print("\n--------------------------------------------------")
    if is_success:
        print("🟢 ESTADO: ÉXITO")
        print(f"📁 ARCHIVO GUARDADO EN: {response}")
    else:
        print("🔴 ESTADO: FALLO")
        print(f"❌ DETALLE: {response}")
    print("--------------------------------------------------")