<div align="center">

  <!-- Banner con efecto typing dinámico en tonos cyberpunk (verde neón y negro) -->
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=28&duration=3000&pause=1000&color=00FF66&center=true&vCenter=true&width=750&height=90&lines=CONTENT+ENRICHER+-+BACKEND;Wikipedia+Scraping+%E2%86%92+AI+Enrichment;Smart+Translation+%E2%86%92+PDF%2FTXT+Export;Automated+Knowledge+Pipeline" alt="Content Enricher Dynamic Banner" />

  <p align="center">
    <strong>Pipeline inteligente de extracción, enriquecimiento con IA y traducción multilingüe</strong>
  </p>

  <!-- Badges dinámicas del stack tecnológico -->
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/OpenAI-ChatGPT_API-00A67E?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI" />
    <img src="https://img.shields.io/badge/Wikipedia-Scraping-gray?style=for-the-badge&logo=wikipedia&logoColor=white" alt="Wikipedia" />
    <img src="https://img.shields.io/badge/Deep_Translate-Multilingual-0052CC?style=for-the-badge&logo=google-translate&logoColor=white" alt="Translator" />
    <img src="https://img.shields.io/badge/Pytest-100%25_Coverage-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest" />
  </p>

  <!-- Flujo visual del pipeline del proyecto -->
  <code>🌐 Wikipedia Scraper</code> ➜ <code>🤖 AI Enricher / Summarize</code> ➜ <code>🌍 Translator</code> ➜ <code>📄 PDF / TXT Exporter</code>

</div>

---

# Content Enricher - Backend 🚀

**Content Enricher** es una herramienta desarrollada en Python diseñada para transformar información bruta en documentos de estudio claros, estructurados y enriquecidos. El sistema busca un tema en Wikipedia, extrae su contenido clave, lo enriquece y lo resume mediante Inteligencia Artificial, lo traduce a diferentes idiomas —siempre en ese orden y **la traducción como última petición**— y exporta **un único resultado**, el de la última etapa ejecutada, en formato `.txt` o `.pdf`.

---

## 🛠️ Tecnologías y Librerías

- **Lenguaje:** Python 3.10+
- **Scraping:** `beautifulsoup4`, `requests`
- **IA:** `openai` (API compatible con OpenAI)
- **Traducción:** `deep-translator` (servicio MyMemory, sin clave de API)
- **Generación de PDF:** `reportlab`
- **Testing & Cobertura:** `pytest`, `pytest-cov`
- **Validaciones & Git Hooks:** `pre-commit` (Conventional Commits)
- **Variables de Entorno:** `python-dotenv`

---

## 📂 Estructura del Proyecto

```text
content-enrichment-backend/
├── main.py                         # Punto de entrada: se ejecuta con `python main.py`
├── src/                            # Código fuente principal
│   ├── __init__.py
│   ├── cli.py                      # Orquestación del flujo (main, pasos 1/5 a 5/5)
│   ├── prompts.py                  # Diálogo con el usuario (entrada y muestra por consola)
│   ├── pipeline.py                 # Etapas del proceso: Wikipedia, IA y traducción
│   ├── errors.py                   # Errores controlados del dominio
│   ├── logging_config.py           # Logging a consola y a logs/app.log
│   ├── scraper.py                  # Extracción desde Wikipedia (con búsqueda de respaldo)
│   ├── enricher.py                 # Enriquecimiento y resúmenes con IA
│   ├── translation/                # Paquete de traducción (HU-05)
│   │   ├── __init__.py
│   │   ├── translator.py           # Traducción con deep-translator / MyMemory
│   │   ├── language_validator.py   # Validación del idioma que escribe el usuario
│   │   ├── text_splitter.py        # Troceado de textos largos para MyMemory
│   │   └── translation_errors.py   # Errores controlados del servicio de traducción
│   └── exporter/                   # Paquete de exportación (TXT / PDF)
│       ├── document_exporter.py    # Orquestador de la exportación
│       ├── validators.py           # Validación de entradas y saneo de nombres
│       ├── pdf_fonts.py            # Fuente Unicode y preparación de texto del PDF
│       ├── txt_exporter.py         # Generación de TXT (UTF-8 con BOM)
│       └── pdf_exporter.py         # Generación de PDF (ReportLab)
├── tests/                          # Suite de pruebas (Gherkin embebido en cada test)
│   ├── test_exporter/
│   │   ├── __init__.py
│   │   ├── test_document_exporter.py   # Orquestación y errores controlados
│   │   ├── test_pdf_exporter.py        # Exportación exclusiva a PDF
│   │   ├── test_pdf_fonts.py           # Fuente Unicode y saneo de texto
│   │   ├── test_txt_exporter.py        # Exportación exclusiva a TXT (UTF-8 con BOM)
│   │   └── test_validators.py          # Validación de nombre, formato y contenido
│   ├── test_translation/
│   │   ├── __init__.py
│   │   ├── test_deep_translate_service.py  # Traducción y errores de MyMemory
│   │   ├── test_language_validator.py      # Idiomas válidos, inválidos e intentos
│   │   ├── test_text_splitter.py           # Troceado de textos largos
│   │   └── test_translator.py              # Contrato del traductor
│   ├── test_cli.py                 # Flujo completo de la CLI (sin red ni IA real)
│   ├── test_enricher.py            # Enriquecimiento y resúmenes con IA
│   ├── test_logging_config.py      # Archivo de log y configuración
│   ├── test_pipeline.py            # Etapas del proceso
│   ├── test_prompts.py             # Diálogo con el usuario
│   └── test_scraper.py             # Wikipedia con mock + 2 escenarios en vivo
├── .pre-commit-config.yaml
├── requirements.txt                # Dependencias de ejecución y desarrollo
├── pytest.ini                      # Rutas, marcadores y selección por defecto
└── README.md
```

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

Crea un archivo `.env` en la raíz del proyecto con estas variables:

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

Al arrancar (`python main.py`) la CLI pide **solo el tema** y arranca el
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
# Pruebas unitarias sin red (por defecto)
pytest

# Escenarios Gherkin que consultan Wikipedia en tiempo real
pytest -m integration

# Reporte de cobertura
pytest --cov=src --cov-report=term-missing
```

**Estado actual: 100 % de cobertura sobre `src/`.**

### Convención Gherkin embebida en los tests

**No existe la carpeta `tests/features/`**: cada test lleva dentro su escenario
Gherkin en inglés, de modo que el escenario y su implementación no pueden
desincronizarse ni queda la duda de a qué test corresponde cada fichero
`.feature`.

El `Feature` se escribe **una sola vez** en la cabecera del módulo y cada
función de test lleva su `Scenario`:

```python
r"""Feature: TXT export of the requested variant

  As a Content Enricher user
  I want the TXT file to contain exactly the variant I asked for
  So that I never receive text or notes that I did not request
"""


def test_txt_exports_only_title_and_body(tmp_path):
    r"""@successful

    Scenario: Save only the requested variant to TXT
        Given a report with title "Python Testing" and body "Únicamente la variante solicitada."
        When I export the report in "txt" format
        Then the file is created successfully
        And the file contains the title "Python Testing"
        And the file contains no section that was not requested
    """
    ...
```

**Reglas de la convención**

- Los docstrings son **raw** (`r"""`): datos como `\n` o `\xa0` se quedan
  literales, igual que los vería un fichero `.feature` de verdad.
- La prosa va **en inglés**; los datos de ejemplo se quedan en español porque
  son las cadenas reales que escribe el producto y traducirlos rompería las
  aserciones.
- Un escenario = una función de test, y siempre es **un único flujo**
  `Given → When → Then → And` (nunca se encadenan dos `Given` en el mismo
  escenario).
- Los casos con muchos ejemplos se escriben como `Scenario Outline` con su
  tabla `Examples`, en paralelo al `@pytest.mark.parametrize` del test. Los
  valores de entrada van entrecomillados para que Gherkin no les recorte los
  espacios.

**Etiquetas de escenario** — los dos tipos de caso que exige el documento de
requisitos:

| Etiqueta Gherkin | Significado |
|---|---|
| `@successful` | Caso feliz: lo que debe ocurrir cuando todo va bien |
| `@failure` | Rechazo controlado: validación denegada, error de red, cuota agotada, artículo inexistente… |

**Marcador de ejecución**

| Marcador | Significado |
|---|---|
| `@pytest.mark.integration` | Pega a servicios externos (Wikipedia real). Desactivado por defecto; se lanza con `pytest -m integration` |

---

## 🚀 Uso de la Aplicación

```bash
python main.py
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
[2026-10-06 13:09:48] [INFO] src.cli: Opción capturada: tema='camas'.
[2026-10-06 13:09:48] [INFO] src.pipeline: Wikipedia: extraídos 5 párrafos de 'Camas'.
[2026-10-06 13:09:48] [INFO] src.pipeline: IA: contenido enriquecido generado.
[2026-10-06 13:09:48] [INFO] src.cli: Opción capturada: resumen=False.
[2026-10-06 13:09:48] [INFO] src.cli: Opción capturada: idioma=original.
[2026-10-06 13:09:48] [INFO] src.cli: Informe exportado a 'output\informe.txt'.
```

La configuración vive en `src/logging_config.py` (`setup_logging()`).

---

## 🔌 Módulo de traducción (HU-05)

`src/translation/translator.py` entrega la clase que la CLI invoca:

```python
from src.translation import DeepTranslateTranslator

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

> La cuota se reinicia al día siguiente. La lectura de la variable es
> opcional: si está vacía, la traducción funciona igual pero con menos
> margen.

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
