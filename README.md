# Content Enricher - Backend 🚀

**Content Enricher** es una herramienta desarrollada en Python diseñada para transformar información bruta en documentos de estudio claros, estructurados y enriquecidos. El sistema permite buscar un tema en Wikipedia, extraer su contenido clave, enriquecerlo y resumirlo mediante Inteligencia Artificial, traducirlo a diferentes idiomas y exportar **únicamente la variante solicitada** en formato `.txt` o `.pdf`.

---

## 🛠️ Tecnologías y Librerías

- **Lenguaje:** Python 3.10+
- **Scraping:** `beautifulsoup4`, `requests`
- **IA:** `openai` (API compatible con OpenAI)
- **Generación de PDF:** `reportlab`
- **Testing & Cobertura:** `pytest`, `pytest-cov`, `pytest-bdd`
- **Validaciones & Git Hooks:** `pre-commit` (Conventional Commits)
- **Variables de Entorno:** `python-dotenv`

---

## 📂 Estructura del Proyecto

```text
content-enrichment-backend/
├── docs/                         # Guías de estudio, historias de usuario y diagramas
│   ├── export_module_study_guide.md
│   ├── ai_content_enricher_study_guide.md
│   ├── historias_usuario.md
│   ├── flowchart.png
│   └── img.png
├── scripts/
│   └── check_models.py           # Diagnóstico de la conexión con la API de IA
├── src/                          # Código fuente principal
│   ├── __init__.py
│   ├── errors.py                 # Jerarquía de errores controlados del dominio
│   ├── options.py                # Esquema de opciones + matriz de validación
│   ├── prompts.py                # Formulario de opciones (solo diálogo con el usuario)
│   ├── main.py                   # Orquestador de la CLI (entrada/salida)
│   ├── pipeline.py               # ContentPipeline: matriz de control del flujo
│   ├── logging_config.py         # Logging a consola y a logs/app.log
│   ├── scraper.py                # Extracción desde Wikipedia (con búsqueda de respaldo)
│   ├── enricher.py               # Enriquecimiento y resúmenes con IA
│   ├── translator.py             # Contrato de traducción (HU-04, pendiente de entrega)
│   └── exporter/                 # Paquete de exportación (TXT / PDF)
│       ├── document_exporter.py  # Orquestador de la exportación
│       ├── validators.py         # Validación de entradas y saneo de nombres
│       ├── pdf_fonts.py          # Fuente Unicode y preparación de texto del PDF
│       ├── txt_exporter.py       # Generación de TXT (UTF-8 con BOM)
│       └── pdf_exporter.py       # Generación de PDF (ReportLab)
├── tests/                        # Suite de pruebas automáticas
│   ├── features/                 # Escenarios Gherkin
│   │   ├── scraper.feature
│   │   ├── options_matrix.feature
│   │   └── export.feature
│   ├── test_exporter/
│   ├── test_options.py           # Esquema y matriz de validación
│   ├── test_matrix.py            # Las 8 combinaciones de salida
│   ├── test_options_matrix_bdd.py
│   ├── test_export_bdd.py
│   ├── test_pipeline.py
│   ├── test_prompts.py
│   ├── test_translator.py
│   └── ...
├── .pre-commit-config.yaml
├── requirements.txt              # Dependencias de ejecución
├── requirements-dev.txt          # Dependencias de desarrollo
└── README.md
```

## 📚 Documentación del Proyecto

- 📤 [Guía del Módulo de Exportación (TXT / PDF)](docs/export_module_study_guide.md)
- 🤖 [Guía del Módulo AiContentEnricher](docs/ai_content_enricher_study_guide.md)
- 🗂️ [Product Backlog e Historias de Usuario](docs/historias_usuario.md)

## ⚙️ Instalación y Configuración Local

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
# Solo para ejecutar la aplicación
pip install -r requirements.txt

# Para desarrollar (tests, cobertura y hooks de git)
pip install -r requirements-dev.txt
```

**4. Configurar variables de entorno**

Crea un archivo `.env` en la raíz del proyecto a partir de `.env.example`:

```bash
OPENAI_API_KEY=tu_clave_de_openai_aqui
OPENAI_BASE_URL=https://api.groq.com/openai/v1
AI_MODEL=qwen/qwen3.8-27b
```

> 💡 Puedes verificar la configuración con `python scripts/check_models.py`.

> ⚠️ **Sin `OPENAI_API_KEY` la aplicación sigue funcionando**, pero solo para la
> variante *texto original* y sin resumen. Si eliges "enriquecido" o "resumen"
> sin credenciales, el sistema lo indica **antes** de hacer ninguna petición y
> no genera ningún archivo.

---

## 🎛️ Formulario de opciones de respuesta

Al arrancar (`python -m src.main`) la CLI recorre este formulario:

```text
➤ Tema a investigar en Wikipedia
➤ Modo de contenido
   [1] Solo texto original (tal cual Wikipedia)
   [2] Contenido enriquecido con IA
➤ ¿Generar un resumen del contenido elegido? (sí/no)
➤ Idioma de traducción (ej. en, fr — Enter = original)
```

Después de mostrar el resultado en terminal:

```text
¿Guardar el informe en disco? ➤ Formato (txt / pdf) ➤ Nombre del archivo
```

---

## 🧭 Matriz de control de flujo

Las opciones se reducen a **dos ejes independientes** más una transformación final:

| Eje | Valores |
|---|---|
| **A · Modo de contenido** | `original` · `enriquecido` |
| **B · Resumen** | `no` · `sí` |
| **C · Idioma** | `ninguno` · `"xx"` (se aplica **siempre al final**) |

Las 6 variaciones del documento de requisitos:

| # | Caso | A | B | C | Contenido del archivo |
|---|---|---|---|---|---|
| 1 | Consulta simple | original | no | no | texto de Wikipedia |
| 2 | Solo texto original | original | no | no | texto de Wikipedia |
| 3 | Solo contenido enriquecido | enriquecido | no | no | texto enriquecido |
| 4 | Solo resumen | cualquiera | **sí** | no | **solo** el resumen |
| 5 | Enriquecido + resumen | enriquecido | **sí** | no | enriquecido **+** resumen |
| 6 | Con traducción | cualquiera | cualquiera | **sí** | la variante ya traducida |

La implementación es una secuencia fija y sin condicionales anidados
(`src/pipeline.py::procesar`):

```python
base     = enriquecer(texto) if modo == ENRICHED else texto   # eje A
cuerpo   = resumir(base) if resumir else base                 # eje B
cuerpo   = traducir(cuerpo, idioma) if idioma else cuerpo     # eje C
```

> **Regla de exportación:** el archivo recibe **solo** `{"topic", "body"}`.
> No puede incluir el texto original ni notas que no se pidieron: el
> exportador no tiene acceso a nada más.

---

## 🛑 Convenciones de Git y Commits

Este repositorio exige que todos los commits se realicen en inglés y siguiendo el formato Conventional Commits (`feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`).

**Activar el hook de validación local**

```bash
python -m pre_commit install --hook-type commit-msg
```

**Ejemplos de commits válidos:**

```text
feat: add wikipedia scraper logic for top 5 paragraphs
fix: handle timeout connection in translator service
test: add unit tests for pdf exporter
docs: update setup instructions in README
```

---

## 🧪 Ejecución de Pruebas (Testing)

```bash
# Pruebas unitarias y BDD sin red (por defecto)
pytest

# Escenarios Gherkin que consultan Wikipedia en tiempo real
pytest -m integration

# Reporte de cobertura
pytest --cov=src --cov-report=term-missing
```

**Estado actual: 100 % de cobertura sobre `src/`.**

La documentación Gherkin (`tests/features/`) cubre los dos tipos de caso que
exige el documento de requisitos:

| Fichero | Contenido |
|---|---|
| `scraper.feature` | Extracción correcta y artículo inexistente |
| `options_matrix.feature` | Las 6 variaciones (`@exitoso`) y sus rechazos (`@fallido`) |
| `export.feature` | Exportación exclusiva (`@exitoso`) y validaciones (`@fallido`) |

---

## 🚀 Uso de la Aplicación

```bash
python -m src.main
```

```text
➤ Tema a investigar en Wikipedia      (requerido)
➤ Modo de contenido                  [1] original · [2] enriquecido
➤ ¿Generar un resumen?               (sí / no)
➤ Idioma de traducción               (Enter = mantener idioma original)
[1/3] Wikipedia → título + 5 párrafos en pantalla
[2/3] Matriz de control → variante seleccionada en pantalla
[3/3] Exportación → ¿Guardar? ➤ formato (txt / pdf) ➤ nombre
🟢 ESTADO: ÉXITO → output/<nombre>.<ext>
```

---

## 📝 Sistema de Logs (⭐)

Cada ejecución registra el proceso completo en `logs/app.log`:

```text
[2026-10-06 13:09:48] [INFO] src.prompts: Opciones capturadas: tema='camas', modo='original', resumen=False, idioma=original.
[2026-10-06 13:09:48] [INFO] src.pipeline: Wikipedia: extraídos 5 párrafos de 'Camas'.
[2026-10-06 13:09:48] [INFO] src.pipeline: Variante resuelta: 'original'.
[2026-10-06 13:09:48] [INFO] __main__: Informe exportado a 'output\informe.txt'.
```

La configuración vive en `src/logging_config.py` (`setup_logging()`).

---

## 🔌 Módulo de traducción (pendiente — HU-04)

`src/translator.py` entrega el **contrato** que la pipeline ya consume:

```python
class DeepTranslateTranslator:
    disponible = ...
    def translate(self, text: str, target_language: str) -> str: ...
```

Mientras no esté implementado, pedir un idioma hace fallar la validación
**antes** de procesar, con el mensaje: *"el módulo de traducción aún no está
disponible"*. Para integrarlo: implementar `translate()` en esa clase y
pasarla a `ContentPipeline(translator=DeepTranslateTranslator())`.

---

## 🐛 Solución de problemas

| Síntoma | Causa | Solución |
|---|---|---|
| "No enriqueció nada" | Falta `.env` con `OPENAI_API_KEY` | `python scripts/check_models.py` |
| El PDF sale con caracteres raros | Fuente sin cobertura Unicode | Resuelto: `src/exporter/pdf_fonts.py` registra una TTF del sistema |
| El TXT se abre con tildes rotas en Windows | Falta el BOM UTF-8 | Resuelto: se escribe con `utf-8-sig` |
| "el módulo de traducción no está disponible" | HU-04 sin entregar | Comportamiento esperado hasta que el equipo la integre |
