# 📤 Guía de Estudio: Módulo de Exportación (TXT / PDF)

> **Proyecto:** `content-enrichment-backend`
> **Módulo:** `src/exporter/`
> **Tests:** `tests/test_exporter/`
> **Stack:** Python · `reportlab` (PDF) · escritura nativa UTF-8 con BOM (TXT) · `pytest`
> **Última actualización:** 2026-10-06

> ### ⚠️ Estado actual tras la iteración de la matriz de control
>
> Esta guía describe la primera versión del módulo. Los siguientes puntos han
> cambiado y son los vigentes:
>
> | Antes | Ahora |
> |---|---|
> | Se exportaban siempre las secciones 1-4 | El archivo contiene **solo** `{"topic", "body"}` |
> | `titles.py` con rótulos por estado de la IA | **Eliminado** (`src/exporter/titles.py`) |
> | `examples/demo_exporter.py` | **Eliminado** (duplicaba la CLI) |
> | TXT en UTF-8 sin BOM | UTF-8 **con BOM** (`utf-8-sig`) para que Windows lo reconozca |
> | PDF en Helvetica puro (caracteres rotos) | `pdf_fonts.py` registra una TTF Unicode del sistema + fallback de normalización |
> | Texto sin escapar a `Paragraph` | Texto escapado como XML (`<...>` deja de desaparecer) |
>
> **Documentación vigente:** `README.md` (matriz de control) y
> `docs/historias_usuario.md` (HU-06).

---

## 1. 🎯 ¿Qué es este módulo?

El módulo `exporter` es la **capa final del pipeline** de `content-enrichment-backend`. Transforma el **contenido enriquecido** (investigación original, texto enriquecido por IA y traducción) en un **informe descargable** en:

- **`.txt`** → texto plano estructurado, codificado en **UTF-8**.
- **`.pdf`** → documento formateado con **ReportLab**, con estilos jerárquicos.

Ambos formatos comparten la misma estructura y consumen el mismo **contrato de datos** (`content_data`), lo que garantiza consistencia total entre salidas.

---

## 2. 💡 ¿Para qué sirve?

| Objetivo | Descripción |
|----------|-------------|
| **Exportar** | Convertir el contenido enriquecido a TXT o PDF. |
| **Estandarizar** | Un único `content_data` alimenta ambos formatos. |
| **Validar** | Comprobar nombre, formato y estructura antes de generar. |
| **Sanear** | Limpiar nombres de archivo con caracteres prohibidos por el SO. |
| **Ser testeable** | Cada componente tiene su suite aislada en `tests/test_exporter/`. |

---

## 3. 🏗️ Arquitectura y Flujo de Datos

```text
content_data (Dict[str, Any])
        │
        ▼
┌───────────────────────────────┐
│  ExportValidator              │  ← Valida nombre, formato y claves
│  .validate_inputs()           │
└───────────────┬───────────────┘
                │  (True / False, msg)
                ▼
┌───────────────────────────────┐
│  DocumentExporter             │  ← Orquesta la exportación
│  .export_content()            │
└───────┬───────────────┬───────┘
        │               │
        ▼               ▼
┌───────────────┐ ┌───────────────┐
│  TxtExporter  │ │  PdfExporter  │
│  .generate()  │ │  .generate()  │
└──────┬────────┘ └──────┬────────┘
       ▼                 ▼
   archivo.txt       archivo.pdf
```

**Contrato de datos** (`content_data`):

| Clave | Tipo | Descripción |
|-------|------|-------------|
| `topic` | `str` | Título del informe. |
| `raw_text` | `str` | Contenido original extraído. |
| `enriched_text` | `str` | Contenido enriquecido por IA. |
| `translated_text` | `str` | Contenido traducido (vacío mientras el traductor está en desarrollo). |
| `summary` | `str` | **Opcional.** Resumen ejecutivo: si está vacío, se omite la sección 4. |
| `enriched_with_ai` | `bool` | **Opcional.** `True` si la IA realmente enriqueció el texto. Si no viene, se infiere comparando `enriched_text` con `raw_text`. |

Las cuatro primeras claves son **obligatorias**: forman el conjunto `REQUIRED_KEYS` del validador. `summary` y `enriched_with_ai` no lo son, por lo que su ausencia no bloquea la exportación.

**Títulos coherentes:** las secciones no prometen lo que no ocurrió (ver `titles.py`):

| Situación | Título de la sección 2 |
|---|---|
| La IA actuó | `2. CONTENIDO ENRIQUECIDO (IA)` |
| Sin API key o fallo de IA | `2. CONTENIDO SIN ENRIQUECER (IA NO DISPONIBLE)` |

| Situación | Título de la sección 3 |
|---|---|
| Hay texto traducido | `3. CONTENIDO TRADUCIDO` |
| Traductor pendiente | `3. CONTENIDO TRADUCIDO (PENDIENTE)` + nota explicativa |

El diccionario lo construye `src/main.py` (`compose_body()` y `export_report()`), que es quien alimenta al exportador en el flujo real de la CLI.

---

## 4. 📁 Estructura de Archivos

### 4.1 Código fuente (`src/exporter/`)

```text
src/exporter/
├── __init__.py           # Expone DocumentExporter vía __all__
├── document_exporter.py  # Orquestador principal
├── pdf_exporter.py       # Exportación a PDF (ReportLab)
├── titles.py             # Rótulos coherentes de cada sección del informe
├── txt_exporter.py       # Exportación a TXT (UTF-8 nativo)
└── validators.py         # ExportValidator (validación + saneo)
```

### 4.2 Tests (`tests/test_exporter/`)

```text
tests/test_exporter/
├── __init__.py                  # Convierte la carpeta en paquete
├── test_document_exporter.py    # Orquestador y flujo completo (4 tests)
├── test_pdf_exporter.py         # Generación de PDF (4 tests)
├── test_titles.py               # Rótulos coherentes de las secciones (7 tests)
├── test_txt_exporter.py         # Generación de TXT (5 tests)
└── test_validators.py           # Reglas de validación y saneo (7 tests)
```

### 4.3 Script de demostración

```text
examples/demo_exporter.py    # Interfaz por consola en examples/
```

Pide nombre y formato al usuario, construye un `sample_data` de ejemplo (tema NLP) y llama al orquestador.

---

## 5. 🔍 Descripción de cada componente

### 5.1 `validators.py` — `ExportValidator`

Encargado de **blindar la entrada** antes de tocar el sistema de archivos. No tiene estado: todo son `@staticmethod` / `@classmethod`.

```python
class ExportValidator:
    SUPPORTED_FORMATS = {"txt", "pdf"}
    REQUIRED_KEYS = {"topic", "raw_text", "enriched_text", "translated_text"}

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        cleaned = re.sub(r'[\\/*?:"<>|]', "", filename).strip()
        return cleaned if cleaned else "informe_investigacion"

    @classmethod
    def validate_inputs(cls, file_name, output_format, content_data) -> Tuple[bool, str]:
        ...
```

- **`SUPPORTED_FORMATS = {"txt", "pdf"}`** → formato de salida admitido.
- **`REQUIRED_KEYS = {"topic", "raw_text", "enriched_text", "translated_text"}`** → claves mínimas del contrato.
- **`sanitize_filename(filename)`** → elimina los caracteres prohibidos por el SO (`\ / * ? : " < > |`) con la expresión regular `r'[\\/*?:"<>|]'`, aplica `.strip()` y devuelve `"informe_investigacion"` si el resultado queda vacío.
- **`validate_inputs(file_name, output_format, content_data) -> (bool, str)`** → ejecuta 4 comprobaciones **en este orden**:
  1. Nombre no vacío (o solo espacios).
  2. Formato dentro de `SUPPORTED_FORMATS` (se normaliza con `.strip().lower()`).
  3. `content_data` es `dict`.
  4. No faltan claves de `REQUIRED_KEYS` (se calcula `REQUIRED_KEYS - set(content_data.keys())`).

  Si todo pasa, devuelve `(True, "")`.

> ⚠️ El orden importa: un nombre vacío se rechaza **antes** de mirar el contenido, por eso `validate_inputs("", "txt", {})` devuelve el error de nombre y no el de claves.

### 5.2 `document_exporter.py` — `DocumentExporter`

Orquestador. Es el único punto de entrada público del módulo.

```python
DocumentExporter(output_dir: str = "output")
```

- **`__init__`** → guarda el `output_dir` y llama a `_ensure_output_directory()`, que crea el directorio con `os.makedirs(..., exist_ok=True)` si no existe (evita `FileNotFoundError`).

**Flujo de `export_content(file_name, output_format, content_data) -> Tuple[bool, str]`:**

1. **Validación** → `ExportValidator.validate_inputs()`; si falla, retorna `(False, msg)` sin crear nada.
2. **Preparación** → formato normalizado (`.strip().lower()`), nombre saneado con `sanitize_filename()` y extensión añadida si falta (`f"{safe_name}.{clean_format}"`), luego se construye la ruta con `os.path.join(self.output_dir, full_name)`.
3. **Generación** → delega en `TxtExporter.generate()` o `PdfExporter.generate()`.

**Errores capturados:**

| Excepción | Retorno |
|-----------|---------|
| `PermissionError` | `Error del Sistema: Permisos insuficientes para guardar en '<ruta>'.` |
| Cualquier otra `Exception` | `Error durante el proceso de exportación: <detalle>` |

Retorno **consistente**: siempre una tupla `(bool, str)` — éxito + ruta, o fallo + mensaje.

### 5.3 `txt_exporter.py` — `TxtExporter`

Clase con un único `@staticmethod generate(file_path, content_data) -> str`. Escribe en **UTF-8 explícito** con separadores visuales:

```text
============================================================
INFORME DE INVESTIGACIÓN: {topic}
============================================================

1. CONTENIDO ORIGINAL (EXTRAÍDO)
----------------------------------------
{raw_text}

2. CONTENIDO ENRIQUECIDO (IA)                ← título real de la sección
----------------------------------------
{enriched_text}

3. CONTENIDO TRADUCIDO                       ← título real de la sección
----------------------------------------
{translated_text}

============================================================
Informe generado exitosamente por Content Enricher Backend.
```

**Los títulos de las secciones 2 y 3 son dinámicos** y los decide `titles.py`:

```text
2. CONTENIDO ENRIQUECIDO (IA)                    ← la IA actuó
2. CONTENIDO SIN ENRIQUECER (IA NO DISPONIBLE)   ← sin API key o fallo de IA

3. CONTENIDO TRADUCIDO                           ← hay texto traducido
3. CONTENIDO TRADUCIDO (PENDIENTE)               ← traductor aún no integrado
                                                   (+ nota: "El módulo de traducción aún no está disponible; ...")
```

- Encabezado: `"=" * 60`.
- Secciones numeradas separadas por `"-" * 40`.
- Los rótulos se escriben en mayúsculas (`.upper()` sobre los títulos comunes a TXT y PDF).
- **Sección 4 opcional**: si `content_data["summary"]` no está vacío, escribe `4. RESUMEN EJECUTIVO (IA)` antes del pie; si está vacío, el informe termina en la sección 3.
- Pie con `"=" * 60` y mensaje final.
- Devuelve `file_path` para que el orquestador lo reenvíe al llamador.

### 5.4 `pdf_exporter.py` — `PdfExporter`

Clase con `@staticmethod generate(file_path, content_data) -> str` basada en ReportLab:

- **`SimpleDocTemplate`** con `pagesize=letter` y márgenes de `0.75 * inch` en los cuatro lados.
- **Tres estilos personalizados** construidos sobre `getSampleStyleSheet()`:

| Estilo | Basado en | Tamaño | Espaciado |
|--------|-----------|--------|-----------|
| `PdfTitle` | `Heading1` | 16 pt / leading 20 | `spaceAfter=12` |
| `PdfSectionHeader` | `Heading2` | 12 pt / leading 16 | `spaceBefore=10`, `spaceAfter=6` |
| `PdfBody` | `Normal` | 9 pt / leading 13 | `spaceAfter=10` |

- Construye el `story`: título en negrita (`<b>Informe de Investigación:</b> {topic}`), un `Spacer(1, 10)` y las secciones con los **mismos rótulos dinámicos** que el TXT (`1. Contenido Original (Extraído)`, `2. Contenido Enriquecido (IA)` o `2. Contenido Sin Enriquecer (IA no disponible)`, `3. Contenido Traducido` o `3. Contenido Traducido (pendiente)`).
- Convierte saltos de línea con `.replace('\n', '<br/>')` para que ReportLab (que interpreta HTML básico en `Paragraph`) los renderice.
- **Sección 4 opcional**: si `content_data["summary"]` no está vacío, añade `4. Resumen Ejecutivo (IA)` con el mismo estilo de sección antes de `document.build(story)`.
- `document.build(story)` y retorno de `file_path`.

### 5.5 `titles.py` — Rótulos coherentes del informe

Fuente única de verdad de los títulos, compartida por TXT y PDF, para que ambos formatos digan exactamente lo mismo:

```python
def ia_actuo(content_data) -> bool            # bandera enriched_with_ai o comparación de textos
def hay_traduccion(content_data) -> bool      # hay contenido traducido real
def titulos_del_informe(content_data) -> Dict[str, str]  # rótulo de cada sección
NOTA_TRADUCCION_PENDIENTE                     # texto de la sección 3 pendiente
```

- **`ia_actuo()`** → usa `content_data["enriched_with_ai"]` si existe; si no, compara `enriched_text` con `raw_text` (si son iguales, la IA no llegó a actuar).
- **`hay_traduccion()`** → `translated_text` con `.strip()`, para detectar el caso del traductor pendiente.
- El objetivo es **coherencia**: el informe nunca afirma que algo se hizo con IA si no se hizo.

### 5.6 `__init__.py`

```python
from .document_exporter import DocumentExporter

__all__ = ["DocumentExporter"]
```

Expone **solo** el orquestador, para que el consumidor use la API de alto nivel:

```python
from src.exporter import DocumentExporter
```

### 5.7 Script de consola (`examples/demo_exporter.py`)

1. Inserta la raíz del proyecto en `sys.path` para que Python reconozca el paquete `src`.
2. Imprime el encabezado `SISTEMA DE GENERACIÓN DE INFORMES`.
3. Pide al usuario **nombre** y **formato** (`txt` / `pdf`).
4. Construye un `sample_data` simulado (tema: *Procesamiento del Lenguaje Natural*) con las 4 claves.
5. Llama a `DocumentExporter(output_dir="output").export_content(...)`.
6. Imprime el resumen con emojis: `🟢 ESTADO: ÉXITO` + ruta, o `🔴 ESTADO: FALLO` + detalle.

---

## 6. 🧪 Suite de Tests

### 6.1 Propósito

Verificar de forma **aislada** que cada capa del exportador funciona y que las regresiones se detectan automáticamente. Hoy la suite contiene **27 tests, todos en verde**.

### 6.2 Herramientas

- **`pytest`** como runner (`pytest.ini` define `testpaths = tests` y `pythonpath = .`).
- **`tmp_path`** → directorio temporal por test, sin archivos residuales ni colisiones.
- **`os.path`** → verificar existencia y tamaño del archivo generado.
- Lectura directa del TXT en `encoding="utf-8"` para comprobar el contenido.

### 6.3 Casos de prueba reales

#### `test_validators.py` — 7 tests

| Test | Escenario | Aserción |
|------|-----------|----------|
| `test_sanitize_filename_valid` | `"informe_2026"` | Sin cambios: `== "informe_2026"` |
| `test_sanitize_filename_invalid_chars` | `"informe/final?2026:v1*<>"` | `== "informefinal2026v1"` (se eliminan `/ ? : * < >`) |
| `test_sanitize_filename_empty_returns_default` | `"   "` y `"???"` | `== "informe_investigacion"` |
| `test_validate_inputs_success` | Datos completos + formato `"pdf"` | `(True, "")` |
| `test_validate_inputs_empty_filename` | Nombre `""` | `False` + `"no puede estar vacío"` |
| `test_validate_inputs_unsupported_format` | Formato `"docx"` | `False` + `"no permitido"` |
| `test_validate_inputs_missing_keys` | `{"topic": "IA"}` (faltan 3 claves) | `False` + `"Faltan datos obligatorios"` |

#### `test_document_exporter.py` — 4 tests

| Test | Escenario | Aserción |
|------|-----------|----------|
| `test_document_exporter_initialization` | `output_dir` inexistente dentro de `tmp_path` | El directorio se crea automáticamente |
| `test_export_content_txt_success` | Flujo completo con formato `"txt"` | `True`, la ruta termina en `informe_test.txt` y el archivo existe |
| `test_export_content_pdf_success` | Flujo completo con formato `"pdf"` | `True`, la ruta termina en `informe_test.pdf` y el archivo existe |
| `test_export_content_validation_failure` | Formato `"doc"` con `content_data = {}` | `False` + `"Error de Validación"` y **no** se crea ningún archivo |

#### `test_txt_exporter.py` — 5 tests

| Test | Escenario | Aserción |
|------|-----------|----------|
| `test_txt_exporter_generate_success` | Datos completos | El archivo existe y contiene: el título `INFORME DE INVESTIGACIÓN: Python Testing`, las 3 secciones (`1. CONTENIDO ORIGINAL (EXTRAÍDO)`, `2. CONTENIDO ENRIQUECIDO (IA)`, `3. CONTENIDO TRADUCIDO`) y el texto original |
| `test_txt_exporter_incluye_resumen_cuando_existe` | Datos con `summary` | Aparece `4. RESUMEN EJECUTIVO (IA)` y su contenido |
| `test_txt_exporter_omite_resumen_si_es_vacio` | `summary: ""` | **No** aparece `4. RESUMEN` y se conserva la sección 3 |
| `test_txt_exporter_titula_sin_ia_cuando_no_hubo_enriquecimiento` | `enriched_text == raw_text` | Aparece `2. CONTENIDO SIN ENRIQUECER (IA NO DISPONIBLE)` y **no** `2. CONTENIDO ENRIQUECIDO (IA)` |
| `test_txt_exporter_marca_traduccion_pendiente_si_esta_vacia` | `translated_text: ""` | Aparece `3. CONTENIDO TRADUCIDO (PENDIENTE)` con la nota del módulo pendiente |

#### `test_pdf_exporter.py` — 4 tests

| Test | Escenario | Aserción |
|------|-----------|----------|
| `test_pdf_exporter_generate_success` | Datos completos | El archivo existe y `os.path.getsize() > 0` (ReportLab no lanza excepciones) |
| `test_pdf_exporter_sin_ia_genera_archivo` | `enriched_text == raw_text` y sin traducción | El PDF se construye con los títulos honestos |
| `test_pdf_exporter_con_resumen_genera_archivo` | Datos con `summary` | El PDF se construye con la sección 4 sin errores y pesa más de 0 |
| `test_pdf_exporter_sin_resumen_genera_archivo` | `summary: ""` | El PDF se construye omitiendo la sección 4 |

> En PDF solo se verifica la existencia y el tamaño: el contenido va comprimido en el flujo del documento, así que la comprobación textual se hace sobre el TXT, que sí se lee en UTF-8.

#### `test_titles.py` — 7 tests

| Test | Escenario | Aserción |
|------|-----------|----------|
| `test_titulo_de_enriquecimiento_cuando_la_ia_actuo` | Textos distintos | `2. Contenido Enriquecido (IA)` e `ia_actuo() is True` |
| `test_titulo_de_enriquecimiento_sin_ia` | `enriched_text == raw_text` | `2. Contenido Sin Enriquecer (IA no disponible)` |
| `test_bandera_explicita_manda_sobre_la_comparacion` | `enriched_with_ai=False` con textos distintos | La bandera manda: `ia_actuo() is False` |
| `test_titulo_de_traduccion_cuando_hay_contenido` | `translated_text` con contenido | `3. Contenido Traducido` |
| `test_titulo_de_traduccion_pendiente_si_no_hay_texto` | `translated_text: ""` | `3. Contenido Traducido (pendiente)` |
| `test_nota_de_traduccion_pendiente` | Constante `NOTA_TRADUCCION_PENDIENTE` | El texto explica que el módulo no está disponible |
| `test_titulos_de_original_y_resumen` | Cualquier caso | Secciones 1 y 4 con su redacción fija |

### 6.4 Ejemplo de test real

```python
# tests/test_exporter/test_txt_exporter.py
import os
from src.exporter.txt_exporter import TxtExporter

def test_txt_exporter_generate_success(tmp_path):
    output_file = tmp_path / "test_report.txt"
    sample_data = {
        "topic": "Python Testing",
        "raw_text": "Texto extraído de prueba.",
        "enriched_text": "Texto enriquecido por IA.",
        "translated_text": "Translated text for testing."
    }

    result_path = TxtExporter.generate(str(output_file), sample_data)
    assert os.path.exists(result_path)

    with open(result_path, "r", encoding="utf-8") as file:
        content = file.read()
        assert "INFORME DE INVESTIGACIÓN: Python Testing" in content
        assert "1. CONTENIDO ORIGINAL (EXTRAÍDO)" in content
        assert "Texto extraído de prueba." in content
        assert "2. CONTENIDO ENRIQUECIDO (IA)" in content
        assert "3. CONTENIDO TRADUCIDO" in content
```

### 6.5 Cómo ejecutar los tests

```bash
# Toda la suite del exportador (27 tests)
pytest tests/test_exporter/ -v

# Con cobertura
pytest tests/test_exporter/ --cov=src/exporter --cov-report=term-missing

# Un módulo específico
pytest tests/test_exporter/test_pdf_exporter.py -v
```

---

## 7. 🚀 Ejemplos de uso

### 7.1 Desde código

```python
from src.exporter.document_exporter import DocumentExporter

content_data = {
    "topic": "Energías renovables",
    "raw_text": "Texto original extraído...",
    "enriched_text": "Resumen enriquecido por IA...",
    "translated_text": "Translated content...",
}

exporter = DocumentExporter(output_dir="output")
ok, path = exporter.export_content("informe_energias", "pdf", content_data)
print(ok, path)  # True output/informe_energias.pdf
```

### 7.2 Desde consola (script demo)

```text
==================================================
       SISTEMA DE GENERACIÓN DE INFORMES
==================================================
➤ Ingrese el nombre del archivo (ej. mi_reporte): reporte_nlp
➤ Elija el formato (txt / pdf): pdf

Procesando y generando archivo...
--------------------------------------------------
🟢 ESTADO: ÉXITO
📁 ARCHIVO GUARDADO EN: output/reporte_nlp.pdf
--------------------------------------------------
```

```bash
python examples/demo_exporter.py
```

---

## 8. ⚠️ Errores comunes y manejo

| Error | Origen | Mensaje |
|-------|--------|---------|
| Nombre vacío | `validate_inputs` | `Error de Validación: El nombre del archivo no puede estar vacío.` |
| Formato no permitido | `validate_inputs` | `Error de Validación: Formato '<x>' no permitido. Use 'txt' o 'pdf'.` |
| `content_data` no es `dict` | `validate_inputs` | `Error de Validación: El contenido debe ser entregado en un diccionario válido.` |
| Faltan claves | `validate_inputs` | `Error de Validación: Faltan datos obligatorios en el informe: {...}` |
| Sin permisos | `export_content` | `Error del Sistema: Permisos insuficientes para guardar en '<path>'.` |
| Otra excepción | `export_content` | `Error durante el proceso de exportación: <detalle>` |

---

## 9. ✅ Buenas prácticas aplicadas

- **UTF-8 explícito** en todas las escrituras y lecturas de archivos.
- **Separación en capas**: validación → orquestación → generación.
- **Contrato único de datos** (`content_data`) compartido entre TXT y PDF.
- **Saneo de nombres** para prevenir rutas peligrosas (`\ / * ? : " < > |`).
- **Retorno consistente** `(bool, str)` en el orquestador.
- **Directorios auto-creados** para evitar `FileNotFoundError`.
- **Tests aislados con `tmp_path`**, sin efectos colaterales.
- **API pública mínima**: `__init__.py` solo expone `DocumentExporter`.

---

## 10. 📚 Referencias

- [ReportLab – Documentación oficial](https://docs.reportlab.com/)
- [Pytest – Documentación oficial](https://docs.pytest.org/)
- [PEP 263 – Encoding declarations](https://peps.python.org/pep-0263/)
- [Python `pathlib`](https://docs.python.org/3/library/pathlib.html)

Ubicación: `docs/export_module_study_guide.md`
