import os
from typing import Dict, Tuple, Any
from .validators import ExportValidator
from .txt_exporter import TxtExporter
from .pdf_exporter import PdfExporter


class DocumentExporter:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self._ensure_output_directory()

    def _ensure_output_directory(self) -> None:
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def export_content(
            self,
            file_name: str,
            output_format: str,
            content_data: Dict[str, Any]
    ) -> Tuple[bool, str]:
        # 1. Capa de Validación
        is_valid, error_msg = ExportValidator.validate_inputs(file_name, output_format, content_data)
        if not is_valid:
            return False, error_msg

        # 2. Preparación de Nombre y Ruta
        clean_format = output_format.strip().lower()
        safe_name = ExportValidator.sanitize_filename(file_name)

        if not safe_name.lower().endswith(f".{clean_format}"):
            full_name = f"{safe_name}.{clean_format}"
        else:
            full_name = safe_name

        file_path = os.path.join(self.output_dir, full_name)

        # 3. Capa de Proceso / Generación
        try:
            if clean_format == "txt":
                saved_path = TxtExporter.generate(file_path, content_data)
            elif clean_format == "pdf":
                saved_path = PdfExporter.generate(file_path, content_data)
            else:
                return False, f"Error: Formato '{clean_format}' no reconocido."

            return True, saved_path

        except PermissionError:
            return False, f"Error del Sistema: Permisos insuficientes para guardar en '{file_path}'."
        except Exception as error:
            return False, f"Error durante el proceso de exportación: {str(error)}"