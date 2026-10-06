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
├── src/                          # Código fuente principal
│   ├── __init__.py
│   ├── main.py                   # CLI: diálogo con el usuario y orquestación del flujo
│   ├── errors.py                 # Errores controlados del dominio
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
│   │   └── export.feature
│   ├── test_exporter/
│   ├── test_export_bdd.py
│   ├── test_main.py              # Flujo completo de la CLI (sin red ni IA real)
│   ├── test_scraper.py
│   ├── test_enricher.py
│   ├── test_translator.py
│   └── ...
├── .pre-commit-config.yaml
├── requirements.txt              # Dependencias de ejecución y desarrollo
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
# Incluye la aplicación, los tests, la cobertura y los hooks de git
pip install -r requirements.txt
```

**4. Configurar variables de entorno**

Crea un archivo `.env` en la raíz del proyecto a partir de `.env.example`:

```bash
OPENAI_API_KEY=tu_clave_de_openai_aqui
OPENAI_BASE_URL=https://api.groq.com/openai/v1
AI_MODEL=qwen/qwen3.8-27b
```

> 💡 Si la IA no arranca, revisa que `.env` define `OPENAI_API_KEY` y
> `OPENAI_BASE_URL`: la CLI lo comprueba al arrancar.

> ⚠️ **Sin `OPENAI_API_KEY` la aplicación sigue funcionando**: el flujo se
> continúa solo con el texto original y la terminal avisa de que se omiten el
> enriquecimiento y el resumen. No se genera ningún archivo a medias.

---

## 🎛️ Flujo de la aplicación

Al arrancar (`python -m src.main`) la CLI solicita primero los datos de interacción:

```text
➤ Tema a investigar en Wikipedia
➤ Idioma de traducción (ej. en, fr — Enter = original)
➤ ¿Generar un resumen del contenido con IA? (sí/no)
```

Y a continuación ejecuta el flujo, mostrando cada paso en terminal:

```text
[1/5] Buscando en Wikipedia      → título + 5 párrafos en pantalla
[2/5] Enriquecimiento con IA     → contenido enriquecido en pantalla
[3/5] Resumen (extra)            → resumen con ChatGPT en pantalla
[4/5] Traducción                 → contenido traducido en pantalla
[5/5] Exportación                → ¿Guardar? ➤ qué partes ➤ formato (txt/pdf) ➤ nombre
```

Cada paso que no se ejecuta se indica explícitamente (sin IA, sin resumen
solicitado o con el idioma original).

---

## 📦 Qué se exporta

Al final del flujo la CLI pregunta **qué partes del informe guardar** y solo
ofrece las que se generaron realmente:

| Sección | Disponible cuando |
|---|---|
| Texto original | Siempre |
| Contenido enriquecido (IA) | Si hay credenciales de IA |
| Resumen (IA) | Si se pidió generar el resumen |
| Traducción | Si se pidió idioma y el traductor está entregado |

Se pueden elegir varias a la vez (separadas por comas) y después el formato
(`txt` / `pdf`) y el nombre del archivo. El orden de procesamiento es fijo:

```python
base     = enriquecer(texto)          # si hay IA
resumen  = resumir(base)              # solo si se pidió
cuerpo   = resumen or base
traducido = traducir(cuerpo, idioma)  # si se pidió idioma: siempre al final
```

Las secciones elegidas se componen en el cuerpo del archivo (con su rótulo
cuando hay más de una) y se entregan al exportador como `{"topic", "body"}`:

> **Regla de exportación:** el archivo recibe **solo** lo que el usuario pidió.
> El paquete `src/exporter/` no tiene acceso a nada más.

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
| `export.feature` | Exportación exclusiva (`@exitoso`) y validaciones (`@fallido`) |

---

## 🚀 Uso de la Aplicación

```bash
python -m src.main
```

```text
➤ Tema a investigar en Wikipedia      (requerido)
➤ Idioma de traducción               (Enter = mantener idioma original)
➤ ¿Generar un resumen?               (sí / no)
[1/5] Wikipedia → título + 5 párrafos en pantalla
[2/5] Enriquecimiento con IA → contenido enriquecido en pantalla
[3/5] Resumen (extra) → resumen en pantalla
[4/5] Traducción → contenido traducido en pantalla
[5/5] Exportación → ¿Guardar? ➤ qué partes ➤ formato (txt / pdf) ➤ nombre
🟢 ESTADO: ÉXITO → output/<nombre>.<ext>
```

---

## 📝 Sistema de Logs (⭐)

Cada ejecución registra el proceso completo en `logs/app.log`:

```text
[2026-10-06 13:09:48] [INFO] src.main: Opciones capturadas: tema='camas', idioma=original, resumen=False.
[2026-10-06 13:09:48] [INFO] src.main: Wikipedia: extraídos 5 párrafos de 'Camas'.
[2026-10-06 13:09:48] [INFO] src.main: IA: contenido enriquecido generado.
[2026-10-06 13:09:48] [INFO] src.main: Informe exportado a 'output\informe.txt'.
```

La configuración vive en `src/logging_config.py` (`setup_logging()`).

---

## 🔌 Módulo de traducción (pendiente — HU-04)

`src/translator.py` entrega el **contrato** que la CLI consume:

```python
class DeepTranslateTranslator:
    def translate(self, text: str, target_language: str) -> str: ...
```

Mientras no esté implementado, `translate()` lanza
`ServiceUnavailableError` y la CLI lo informa con el mensaje
*"Traducción omitida: el módulo de traducción (DeepTranslate) aún no está
implementado"*, continuando con el contenido sin traducir. Para integrarlo:
basta con implementar `translate()` en esa clase, sin tocar el resto del flujo.

---

## 🐛 Solución de problemas

| Síntoma | Causa | Solución |
|---|---|---|
| "No enriqueció nada" | Falta `.env` con `OPENAI_API_KEY` | Revisa `.env` (`OPENAI_API_KEY` y `OPENAI_BASE_URL`) |
| El PDF sale con caracteres raros | Fuente sin cobertura Unicode | Resuelto: `src/exporter/pdf_fonts.py` registra una TTF del sistema |
| El TXT se abre con tildes rotas en Windows | Falta el BOM UTF-8 | Resuelto: se escribe con `utf-8-sig` |
| "Traducción omitida" | HU-04 sin entregar | Comportamiento esperado hasta que el equipo la integre |
