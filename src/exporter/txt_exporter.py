from typing import Dict, Any

from .titles import NOTA_TRADUCCION_PENDIENTE, titulos_del_informe


class TxtExporter:

    @staticmethod
    def generate(file_path: str, content_data: Dict[str, Any]) -> str:
        titulos = titulos_del_informe(content_data)
        traducido = str(content_data.get("translated_text") or "").strip()

        with open(file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write("=" * 60 + "\n")
            txt_file.write(f"INFORME DE INVESTIGACIÓN: {content_data.get('topic')}\n")
            txt_file.write("=" * 60 + "\n\n")

            txt_file.write(f"{titulos['original'].upper()}\n")
            txt_file.write("-" * 40 + "\n")
            txt_file.write(f"{content_data.get('raw_text')}\n\n")

            txt_file.write(f"{titulos['enriquecimiento'].upper()}\n")
            txt_file.write("-" * 40 + "\n")
            txt_file.write(f"{content_data.get('enriched_text')}\n\n")

            txt_file.write(f"{titulos['traduccion'].upper()}\n")
            txt_file.write("-" * 40 + "\n")
            if traducido:
                txt_file.write(f"{content_data.get('translated_text')}\n\n")
            else:
                txt_file.write(f"{NOTA_TRADUCCION_PENDIENTE}\n\n")

            # Sección opcional: solo se escribe si la IA generó resumen
            resumen = str(content_data.get("summary") or "").strip()
            if resumen:
                txt_file.write("4. RESUMEN EJECUTIVO (IA)\n")
                txt_file.write("-" * 40 + "\n")
                txt_file.write(f"{resumen}\n\n")

            txt_file.write("=" * 60 + "\n")
            txt_file.write("Informe generado exitosamente por Content Enricher Backend.\n")

        return file_path