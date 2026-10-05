from typing import Dict, Any


class TxtExporter:

    @staticmethod
    def generate(file_path: str, content_data: Dict[str, Any]) -> str:
        with open(file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write("=" * 60 + "\n")
            txt_file.write(f"INFORME DE INVESTIGACIÓN: {content_data.get('topic')}\n")
            txt_file.write("=" * 60 + "\n\n")

            txt_file.write("1. CONTENIDO ORIGINAL (EXTRAÍDO)\n")
            txt_file.write("-" * 40 + "\n")
            txt_file.write(f"{content_data.get('raw_text')}\n\n")

            txt_file.write("2. CONTENIDO ENRIQUECIDO Y RESUMIDO (IA)\n")
            txt_file.write("-" * 40 + "\n")
            txt_file.write(f"{content_data.get('enriched_text')}\n\n")

            txt_file.write("3. CONTENIDO TRADUCIDO\n")
            txt_file.write("-" * 40 + "\n")
            txt_file.write(f"{content_data.get('translated_text')}\n\n")

            txt_file.write("=" * 60 + "\n")
            txt_file.write("Informe generado exitosamente por Content Enricher Backend.\n")

        return file_path