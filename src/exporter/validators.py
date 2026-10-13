import re
from typing import Any, Dict, Tuple


class ExportValidator:
    SUPPORTED_FORMATS = {"txt", "pdf"}
    REQUIRED_KEYS = {"topic", "body"}

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        cleaned = re.sub(r'[\\/*?:"<>|]', "", filename).strip()
        return cleaned if cleaned else "informe_investigacion"

    @classmethod
    def validate_inputs(
        cls,
        file_name: str,
        output_format: str,
        content_data: Dict[str, Any],
    ) -> Tuple[bool, str]:
        if not file_name or not file_name.strip():
            return False, "Error de Validación: El nombre del archivo no puede estar vacío."

        clean_format = output_format.strip().lower()
        if clean_format not in cls.SUPPORTED_FORMATS:
            return False, (
                f"Error de Validación: Formato '{output_format}' no permitido. "
                "Use 'txt' o 'pdf'."
            )

        if not isinstance(content_data, dict):
            return False, "Error de Validación: El contenido debe ser entregado en un diccionario válido."

        missing_keys = cls.REQUIRED_KEYS - set(content_data.keys())
        if missing_keys:
            return False, f"Error de Validación: Faltan datos obligatorios en el informe: {missing_keys}"

        return True, ""
