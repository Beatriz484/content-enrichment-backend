<<<<<<< HEAD
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
=======
"""Generación del archivo TXT con la variante exacta solicitada.

Se escribe en UTF-8 **con BOM** (``utf-8-sig``): sin él, Windows abre el
archivo como ANSI y las tildes aparecen corruptas ("INVESTIGACIN").
"""
from typing import Any, Dict

SEPARADOR = "=" * 60


class TxtExporter:
    @staticmethod
    def generate(file_path: str, content_data: Dict[str, Any]) -> str:
        """Escribe título y cuerpo de la variante pedida. Nada más."""
        with open(file_path, "w", encoding="utf-8-sig") as txt_file:
            txt_file.write(f"{SEPARADOR}\n")
            txt_file.write(f"TÍTULO: {content_data['topic']}\n")
            txt_file.write(f"{SEPARADOR}\n\n")
            txt_file.write(f"{str(content_data['body']).strip()}\n")

        return file_path
>>>>>>> dev
