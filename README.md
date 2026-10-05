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
├── docs/                     # Diagramas (flowchart.png) y escenarios Gherkin (.feature)
│   ├── flowchart.png
│   └── tests.feature
├── src/                      # Código fuente principal
│   ├── __init__.py
│   ├── main.py               # Punto de entrada de la aplicación CLI
│   ├── scraper.py            # Extracción de datos desde Wikipedia
│   ├── enricher.py           # Enriquecimiento y resúmenes con IA
│   ├── translator.py         # Integración con la API de traducción
│   └── exporter.py           # Generación de archivos en PDF y TXT
├── tests/                    # Suite de pruebas automáticas (100% Cobertura)
│   ├── __init__.py
│   ├── test_scraper.py
│   ├── test_enricher.py
│   ├── test_translator.py
│   └── test_exporter.py
├── .gitignore                # Exclusión de archivos temporales y entornos
├── .pre-commit-config.yaml   # Reglas de validación para mensajes de commit
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Documentación principal
```

## ⚙️ Instalación y Configuración Local
Sigue estos pasos para clonar e instalar el proyecto en tu máquina local:

1. Clonar el repositorio
Bash
git clone [https://github.com/Beatriz484/content-enrichment-backend.git](https://github.com/Beatriz484/content-enrichment-backend.git)
cd content-enrichment-backend
2. Crear y activar el entorno virtual
En Linux / macOS:
Bash
python3 -m venv venv
source venv/bin/activate
En Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
3. Instalar dependencias
Bash
pip install -r requirements.txt
4. Configurar variables de entorno
Crea un archivo .env en la raíz del proyecto tomando como referencia el archivo .env.example (si aplica) e ingresa tus credenciales/API keys:

Fragmento de código
API_KEY_IA=tu_api_key_aqui
API_KEY_TRANSLATOR=tu_api_key_aqui

## 🛑 Convenciones de Git y Commits
Este repositorio exige que todos los commits se realicen en inglés y siguiendo el formato Conventional Commits (feat:, fix:, docs:, test:, chore:, etc.).

Activar el hook de validación local
Al clonar el proyecto por primera vez, debes ejecutar en tu terminal:

Bash
python -m pre_commit install --hook-type commit-msg
A partir de este momento, Git validará automáticamente que no se puedan realizar commits en español o con un formato incorrecto.

Ejemplos de commits válidos:

feat: add wikipedia scraper logic for top 5 paragraphs

fix: handle timeout connection in translator service

test: add unit tests for pdf exporter

docs: update setup instructions in README

## 🧪 Ejecución de Pruebas (Testing)
Para ejecutar la suite de pruebas unitarias e integración con pytest y verificar la cobertura de código:

Bash
# Ejecutar todas las pruebas
pytest

# Ejecutar reporte de cobertura
pytest --cov=src --cov-report=term-missing
🚀 Uso de la Aplicación
Para iniciar la interfaz interactiva por terminal (CLI), ejecuta:

Bash
python -m src.main
