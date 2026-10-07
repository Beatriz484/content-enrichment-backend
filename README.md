# Content Enricher - Backend 🚀

**Content Enricher** es una herramienta desarrollada en Python diseñada para transformar información bruta en documentos de estudio claros, estructurados y enriquecidos. El sistema busca un tema en Wikipedia, extrae su contenido clave, lo enriquece y lo resume mediante Inteligencia Artificial, lo traduce a diferentes idiomas —siempre en ese orden y **la traducción como última petición**— y exporta **un único resultado**, el de la última etapa ejecutada, en formato `.txt` o `.pdf`.

---

## 🛠️ Tecnologías y Librerías

- **Lenguaje:** Python 3.10+
- **Scraping:** `beautifulsoup4`, `requests`
- **IA:** `openai` (API compatible con OpenAI)
- **Traducción:** `deep-translator` (servicio MyMemory, sin clave de API)
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
│   ├── translator.py             # Traducción con deep-translator / MyMemory (HU-05)
│   ├── language_validator.py     # Validación del idioma que escribe el usuario
│   ├── text_splitter.py          # Troceado de textos largos para MyMemory
│   ├── translation_errors.py     # Errores controlados del servicio de traducción
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

Al arrancar (`python -m src.main`) la CLI pide **solo el tema** y arranca el
proceso. Las decisiones restantes se preguntan **en el momento en que les toca**,
siempre después de mostrar los resultados de la búsqueda:

```text
➤ Tema a investigar en Wikipedia      (única pregunta inicial)
[1/5] Buscando en Wikipedia      → título + 5 párrafos en pantalla
[2/5] Enriquecimiento con IA     → contenido enriquecido en pantalla
➤ ¿Generar un resumen del contenido con IA? (sí/no)
[3/5] Resumen (extra)            → resumen con ChatGPT en pantalla
➤ Idioma de traducción (ej. en, fr — Enter = original)   ← última petición
[4/5] Traducción                 → contenido traducido en pantalla
[5/5] Exportación                → ¿Guardar? ➤ formato (txt/pdf) ➤ nombre
```

Cada paso que no se ejecuta se indica explícitamente (sin IA, sin resumen
solicitado o con el idioma original).

---

## 📦 Qué se exporta

El informe contiene **un único resultado**: el último eslabón realmente
generado de la cadena. No se pregunta qué partes guardar porque solo hay una
respuesta posible:

```python
base      = enriquecer(texto)               # si hay credenciales de IA
resumen   = resumir(base)                   # solo si se pidió
traducido = traducir(resumen or base)       # solo si se pidió idioma
final     = traducido or resumen or base or texto   # ← lo que se guarda
```

| Parte del archivo | Contenido |
|---|---|
| `TÍTULO` | Título del artículo de Wikipedia |
| Cuerpo | `final`: la traducción si existe; si no, el resumen, el contenido enriquecido o el texto original |

El diálogo de exportación se reduce a tres decisiones: **¿Guardar?**, **formato**
(`txt` / `pdf`) y **nombre** del archivo. El paquete `src/exporter/` recibe
`{"topic", "body"}` y no tiene acceso a nada más.

> **Regla de exportación:** el archivo recibe **solo** lo que el usuario pidió,
> sin secciones adicionales ni notas no solicitadas.

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
[1/5] Wikipedia → título + 5 párrafos en pantalla
[2/5] Enriquecimiento con IA → contenido enriquecido en pantalla
➤ ¿Generar un resumen?               (sí / no)
[3/5] Resumen (extra) → resumen en pantalla
➤ Idioma de traducción                (Enter = mantener idioma original)
[4/5] Traducción → contenido traducido en pantalla
[5/5] Exportación → ¿Guardar? ➤ formato (txt / pdf) ➤ nombre
🟢 ESTADO: ÉXITO → output/<nombre>.<ext>
```

---

## 📝 Sistema de Logs (⭐)

Cada ejecución registra el proceso completo en `logs/app.log`:

```text
[2026-10-06 13:09:48] [INFO] src.main: Opción capturada: tema='camas'.
[2026-10-06 13:09:48] [INFO] src.main: Wikipedia: extraídos 5 párrafos de 'Camas'.
[2026-10-06 13:09:48] [INFO] src.main: IA: contenido enriquecido generado.
[2026-10-06 13:09:48] [INFO] src.main: Opción capturada: resumen=False.
[2026-10-06 13:09:48] [INFO] src.main: Opción capturada: idioma=original.
[2026-10-06 13:09:48] [INFO] src.main: Informe exportado a 'output\informe.txt'.
```

La configuración vive en `src/logging_config.py` (`setup_logging()`).

---

## 🔌 Módulo de traducción (HU-05)

`src/translator.py` entrega la clase que la CLI invoca:

```python
from src.translator import DeepTranslateTranslator

service = DeepTranslateTranslator()          # origen "es-ES" (es.wikipedia.org)
texto_traducido = service.translate(texto, "en")   # "en", "inglés", "en-GB"...
```

- Se aplica **siempre al final** del flujo, sobre el contenido resultante
  (resumen → enriquecido → original), y lo traducido es lo que se exporta.
- El texto se trocea solo por párrafos y frases para respetar el límite de
  MyMemory (menos de 500 caracteres por petición).
- Acepta el nombre en español (`inglés`), en inglés (`english`) o el código de
  MyMemory (`en-GB`), sin importar mayúsculas ni tildes.
- Los errores de red, de idioma o de cuota llegan a la CLI como
  `TranslationServiceError` y se muestran como *"Traducción omitida: …"*:
  la aplicación nunca se cae por un fallo del traductor.

### Cuota diaria de MyMemory (⭐)

MyMemory es gratuita y **no necesita clave de API**, pero limita a **5.000
caracteres al día por IP**. Un artículo de Wikipedia de cinco párrafos ronda los
3.500, de modo que **sin configurar el email solo cabe una o dos traducciones al
día**; la siguiente devuelve el aviso *"Se ha superado el límite de peticiones de
MyMemory"*.

Para subir la cuota a **50.000 caracteres al día**, añade tu correo en el
`.env` (el servicio lo usa como identificador, no es un secreto):

```bash
MYMEMORY_EMAIL=tu_correo@example.com
```

> La cuota se reinicia al día siguiente. `.env.example` ya incluye la variable
> y la lectura es opcional: si está vacía, la traducción funciona igual pero
> con menos margen.

---

## 🐛 Solución de problemas

| Síntoma | Causa | Solución |
|---|---|---|
| "No enriqueció nada" | Falta `.env` con `OPENAI_API_KEY` | Revisa `.env` (`OPENAI_API_KEY` y `OPENAI_BASE_URL`) |
| El PDF sale con caracteres raros | Fuente sin cobertura Unicode | Resuelto: `src/exporter/pdf_fonts.py` registra una TTF del sistema |
| El TXT se abre con tildes rotas en Windows | Falta el BOM UTF-8 | Resuelto: se escribe con `utf-8-sig` |
| "Traducción omitida" | Cuota diaria de MyMemory agotada (5.000 caracteres/día) | Espera a que se reinicie o añade `MYMEMORY_EMAIL` en `.env` (50.000/día) |

## 👥 Equipo de Desarrollo

<div align="center">

<table style="border-collapse: collapse; text-align: center;">
  <thead>
    <tr>
      <th align="center" width="20%">
        <a href="https://github.com/oscarperezGR">
          <img src="https://github.com/oscarperezGR.png" width="90" height="90" style="border-radius: 50%; object-fit: cover;" alt="Óscar Pérez" />
        </a><br>
        <sub><b>Óscar Pérez</b></sub>
      </th>
      <th align="center" width="20%">
        <a href="https://github.com/Beatriz484">
          <img src="https://github.com/Beatriz484.png" width="90" height="90" style="border-radius: 50%; object-fit: cover;" alt="Beatriz Íñiguez" />
        </a><br>
        <sub><b>Beatriz Íñiguez</b></sub>
      </th>
      <th align="center" width="20%">
        <a href="https://github.com/simonlopez25">
          <img src="https://github.com/simonlopez25.png" width="90" height="90" style="border-radius: 50%; object-fit: cover;" alt="Simón López" />
        </a><br>
        <sub><b>Simón López</b></sub>
      </th>
      <th align="center" width="20%">
        <a href="https://github.com/apariciodiazpatricia-cell">
          <img src="https://github.com/apariciodiazpatricia-cell.png" width="90" height="90" style="border-radius: 50%; object-fit: cover;" alt="Patricia Aparicio" />
        </a><br>
        <sub><b>Patricia Aparicio</b></sub>
      </th>
      <th align="center" width="20%">
        <a href="https://github.com/margaritabellidoroig">
          <img src="https://github.com/margaritabellidoroig.png" width="90" height="90" style="border-radius: 50%; object-fit: cover;" alt="Margarita Bellido" />
        </a><br>
        <sub><b>Margarita Bellido</b></sub>
      </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center" valign="middle">
        <a href="https://github.com/oscarperezGR"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" /></a><br>
        <a href="https://www.linkedin.com/in/oscareduardoperezrodriguez/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white" /></a>
      </td>
      <td align="center" valign="middle">
        <a href="https://github.com/Beatriz484"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" /></a><br>
        <a href="https://www.linkedin.com/in/beatriz-iniguez-cascales-dev/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white" /></a>
      </td>
      <td align="center" valign="middle">
        <a href="https://github.com/simonlopez25"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" /></a><br>
        <a href="https://www.linkedin.com/in/simon-lopez25/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white" /></a>
      </td>
      <td align="center" valign="middle">
        <a href="https://github.com/apariciodiazpatricia-cell"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" /></a><br>
        <a href="https://www.linkedin.com/in/patriciaapariciodiaz/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white" /></a>
      </td>
      <td align="center" valign="middle">
        <a href="https://github.com/margaritabellidoroig"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" /></a><br>
        <img src="https://img.shields.io/badge/Rol-Developer-333333?style=flat-square" />
      </td>
    </tr>
  </tbody>
</table>

</div>
