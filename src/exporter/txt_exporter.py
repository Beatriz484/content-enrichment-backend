from typing import Any, Dict

from .plain_text import markdown_to_plain_text

SEPARADOR = "=" * 60


class TxtExporter:
    @staticmethod
    def generate(file_path: str, content_data: Dict[str, Any]) -> str:
        body = markdown_to_plain_text(str(content_data["body"]).strip())

        with open(file_path, "w", encoding="utf-8-sig") as txt_file:
            txt_file.write(f"{SEPARADOR}\n")
            txt_file.write(f"TÍTULO: {content_data['topic']}\n")
            txt_file.write(f"{SEPARADOR}\n\n")
            txt_file.write(f"{body}\n")

        return file_path