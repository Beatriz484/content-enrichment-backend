# Content Enricher - Backend 🚀

**Content Enricher** es una herramienta desarrollada en Python diseñada para transformar información bruta en documentos de estudio claros, estructurados y enriquecidos. El sistema permite buscar un tema en Wikipedia, extraer su contenido clave, enriquecerlo y resumirlo mediante Inteligencia Artificial, traducirlo a diferentes idiomas y exportar el resultado final en formatos listos para su uso (`.txt` o `.pdf`).

---

## 🛠️ Tecnologías y Librerías

- **Lenguaje:** Python 3.10+
- **Scraping:** `beautifulsoup4`, `requests`
- **Generación de PDF:** `reportlab`
- **Testing & Cobertura:** `pytest`, `pytest-cov`, `pytest-mock`
- **Validaciones & Git Hooks:** `pre-commit` (Conventional Commits)
- **Variables de Entorno:** `python-dotenv`

---

## 📂 Estructura del Proyecto

El proyecto sigue una arquitectura modular y orientada a objetos (POO) alineada con los principios SOLID:

```text
content-enrichment-backend/
├── docs/                         # Guías de estudio, historias de usuario y diagramas
│   ├── export_module_study_guide.md       # Guía del módulo de exportación (TXT / PDF)
│   ├── ai_content_enricher_study_guide.md # Guía del módulo AiContentEnricher
│   ├── historias_usuario.md
│   ├── flowchart.png
│   ├── img.png
│   └── tests.feature
├── src/                          # Código fuente principal
│   ├── __init__.py
│   ├── main.py                   # CLI interactiva (solo entrada/salida de usuario)
│   ├── pipeline.py               # ContentPipeline: investigar → IA → resumen → traducción
│   ├── logging_config.py         # Logging a consola y a logs/app.log
│   ├── scraper.py                # Extracción de datos desde Wikipedia (con búsqueda de respaldo)
│   ├── enricher.py               # Enriquecimiento y resúmenes con IA
│   ├── translator.py             # Traducción (módulo en desarrollo por el equipo)
│   └── exporter/                 # Paquete de exportación (TXT / PDF)
│       ├── __init__.py           # Expone DocumentExporter
│       ├── document_exporter.py  # Orquestador de la exportación
│       ├── validators.py         # Validación de entradas y saneo de nombres
│       ├── titles.py             # Rótulos coherentes de cada sección del informe
│       ├── txt_exporter.py       # Generación de TXT (UTF-8)
│       └── pdf_exporter.py       # Generación de PDF (ReportLab)
├── tests/                        # Suite de pruebas automáticas
│   ├── __init__.py
│   ├── test_scraper.py           # Scraper con peticiones simuladas (sin red)
│   ├── test_scraper_bdd.py       # Escenarios BDD (pytest -m integration)
│   ├── features/scraper.feature  # Escenarios Gherkin del scraper
│   ├── test_enricher.py          # Enriquecimiento y resumen con mocks
│   ├── test_pipeline.py          # Orquestador del flujo completo
│   ├── test_main.py              # CLI con dependencias simuladas
│   ├── test_logging_config.py    # Configuración del archivo de log
│   └── test_exporter/            # Tests del módulo de exportación
│       ├── __init__.py
│       ├── test_document_exporter.py
│       ├── test_validators.py
│       ├── test_txt_exporter.py
│       └── test_pdf_exporter.py
├── examples/                     # Scripts de demostración y utilidades
│   ├── demo_enricher_flow.py
│   ├── demo_exporter.py
│   └── check_models.py
├── .gitignore                    # Exclusión de archivos temporales y entornos
├── .pre-commit-config.yaml       # Reglas de validación para mensajes de commit
├── requirements.txt              # Dependencias del proyecto
└── README.md                     # Documentación principal
```

## 📚 Documentación del Proyecto

- 📤 [Guía del Módulo de Exportación (TXT / PDF)](docs/export_module_study_guide.md)
- 🤖 [Guía del Módulo AiContentEnricher](docs/ai_content_enricher_study_guide.md)

## ⚙️ Instalación y Configuración Local
Sigue estos pasos para clonar e instalar el proyecto en tu máquina local:

**1. Clonar el repositorio**

```bash
git clone https://github.com/Beatriz484/content-enrichment-backend.git
cd content-enrichment-backend
```

**2. Crear y activar el entorno virtual**

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**3. Instalar dependencias**

```bash
pip install -r requirements.txt
```
**4. Configurar variables de entorno**

Crea un archivo `.env` en la raíz del proyecto a partir de `.env.example`:

```bash
OPENAI_API_KEY=tu_clave_de_openai_aqui
OPENAI_BASE_URL=https://api.groq.com/openai/v1
```

> 💡 Sin `OPENAI_API_KEY` la aplicación funciona igualmente: avisa por pantalla y omite el enriquecimiento con IA.

## 🛑 Convenciones de Git y Commits

Este repositorio exige que todos los commits se realicen en inglés y siguiendo el formato Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, etc.).

**Activar el hook de validación local**

Al clonar el proyecto por primera vez, debes ejecutar en tu terminal:

```bash
python -m pre_commit install --hook-type commit-msg
```

A partir de este momento, Git validará automáticamente que no se puedan realizar commits en español o con un formato incorrecto.

**Ejemplos de commits válidos:**

```text
feat: add wikipedia scraper logic for top 5 paragraphs
fix: handle timeout connection in translator service
test: add unit tests for pdf exporter
docs: update setup instructions in README
```

## 🧪 Ejecución de Pruebas (Testing)

Para ejecutar la suite de pruebas unitarias e integración con pytest y verificar la cobertura de código:

```bash
# Pruebas unitarias (sin red, rápidas)
pytest

# Solo los escenarios BDD que consultan Wikipedia en tiempo real
pytest -m integration

# Reporte de cobertura
pytest --cov=src --cov-report=term-missing
```

Las pruebas que pegan a servicios externos van marcadas con `@pytest.mark.integration` y **no** se ejecutan en el `pytest` por defecto.

---

## 🚀 Uso de la Aplicación

Para iniciar la interfaz interactiva por terminal (CLI), ejecuta:

```bash
python -m src.main
```

Flujo completo que sigue la CLI:

```text
➤ Tema a investigar en Wikipedia      (requerido)
➤ Idioma de traducción                (requerido)
[1/4] Wikipedia → título + 5 párrafos en pantalla
[2/4] IA        → contenido enriquecido en pantalla
[3/4] Resumen   → resumen ejecutivo (opcional, ⭐)
[4/4] Traducción→ ⚠️ pendiente mientras src/translator.py está en desarrollo
¿Guardar?  ➤ formato (txt / pdf) ➤ nombre del archivo
🟢 ESTADO: ÉXITO → output/<nombre>.<ext>
```

- **Sin `OPENAI_API_KEY`** la ejecución continúa: se avisa por pantalla y el informe se genera solo con el contenido de Wikipedia (degradación elegante).
- El nombre del archivo se sanea automáticamente (sin caracteres prohibidos por el SO).

---

## 📝 Sistema de Logs (⭐)

Cada ejecución registra el proceso completo en `logs/app.log` (directorio ignorado por git):

```text
[2026-10-05 16:00:14] [INFO] __main__: Solicitud recibida: tema='...', idioma='en'.
[2026-10-05 16:00:15] [INFO] src.pipeline: Wikipedia: extraídos 5 párrafos de '...'.
[2026-10-05 16:00:15] [WARNING] src.pipeline: Traducción pendiente: el módulo 'src/translator.py' aún no está disponible.
[2026-10-05 16:00:15] [INFO] __main__: Informe exportado a 'output/informe.pdf'.
```

La configuración vive en `src/logging_config.py` (`setup_logging()`): salida simultánea a consola y a archivo.

---

## 🔌 Módulo de traducción (en desarrollo)

`src/translator.py` está pendiente de entrega por parte del equipo. La pipeline ya lo detecta automáticamente: basta con inyectar un objeto con esta interfaz en `ContentPipeline(translator=...)`:

```python
def translate(self, text: str, target_language: str) -> str: ...
```

Hasta entonces, `ContentPipeline.traducir()` devuelve `""`, la CLI muestra el aviso y la sección 3 del informe se queda vacía.
