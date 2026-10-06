# Product Backlog e Historias de Usuario

## Historia de Usuario: Módulo Scraper de Wikipedia

* **ID:** HU-01
* **Título:** Extracción automática de contenido de Wikipedia.
* **Prioridad:** Alta
* **Historia de Usuario:**
  > Como usuario del sistema backend, quiero introducir el tema de un artículo para que el sistema busque automáticamente en Wikipedia, valide su existencia y extraiga los primeros 5 párrafos estructurados junto a su título.

### Criterios de Aceptación:
- [x] El sistema permite introducir un tema de búsqueda.
- [x] Si el artículo existe, extrae el título y los primeros 5 párrafos de manera limpia.
- [x] Si el artículo no existe o hay un error de conexión, lanza una excepción controlada.
- [x] El comportamiento está validado mediante pruebas automatizadas (BDD con `pytest-bdd`).
- [x] Si el tema no coincide con el título del artículo, se lanza una búsqueda de respaldo en la API de Wikipedia.
- [x] Los párrafos se normalizan en origen (espacios duros `&nbsp;` y espacios repetidos) para que no aparezcan corruptos en el TXT/PDF.
- [x] Tests unitarios sin red (`tests/test_scraper.py`) y escenarios BDD marcados como integración (`pytest -m integration`).

---

## Historia de Usuario: Formulario de Opciones de Respuesta y Matriz de Control

* **ID:** HU-02
* **Título:** Elegir exactamente qué salida se quiere recibir.
* **Prioridad:** Alta
* **Estado:** Entregada
* **Historia de Usuario:**
  > Como usuario del sistema, quiero elegir el modo de contenido (texto original o enriquecido), si deseo resumen y a qué idioma traducir, para recibir exactamente la salida que pedí y nada más.

### Criterios de Aceptación:
- [x] La CLI solicita tema, modo de contenido, resumen e idioma antes de empezar (`src/prompts.py`).
- [x] El esquema de datos está modelado con un `dataclass` inmutable en `src/options.py`.
- [x] La validación devuelve **todos** los errores a la vez, no solo el primero.
- [x] La validación se ejecuta **antes** de cualquier petición a la red.
- [x] La matriz cubre las 6 variaciones del documento: consulta simple, solo original, solo enriquecido, solo resumen, enriquecido + resumen y cualquiera de ellas traducida.
- [x] El orden del procesamiento es fijo: `base → resumen → traducción` (`src/pipeline.py::procesar`).
- [x] El archivo exportado contiene **exclusivamente** el título y la variante pedida.
- [x] Pedir IA sin credenciales o traducción sin módulo es un rechazo explícito, nunca una degradación silenciosa.
- [x] Validado con `tests/test_options.py`, `tests/test_matrix.py` y `tests/features/options_matrix.feature` (escenarios `@exitoso` y `@fallido`).

---

## Historia de Usuario: Integración del Flujo Completo (Pipeline + CLI)

* **ID:** HU-03
* **Título:** Investigar, procesar y exportar en un solo flujo.
* **Prioridad:** Alta
* **Historia de Usuario:**
  > Como usuario del sistema, quiero introducir un tema en la terminal para obtener un informe final en `.txt` o `.pdf` con exactamente la variante que he elegido, sin salir de la aplicación.

### Criterios de Aceptación:
- [x] La CLI solicita las opciones del formulario antes de empezar.
- [x] Muestra los resultados de Wikipedia en la terminal antes de pedir acciones adicionales.
- [x] Muestra cada paso realmente ejecutado (enriquecido, resumen, traducido).
- [x] Pregunta si se desea guardar, el formato (`txt`/`pdf`) y el nombre del archivo (⭐).
- [x] La lógica vive en `src/pipeline.py`; `src/main.py` solo orquesta la entrada/salida.
- [x] La CLI no falla por codificación en Windows (entrada/salida UTF-8 con reemplazo seguro).
- [x] Validado con `tests/test_main.py` (sin red ni IA real).

### Criterios pendientes:
- [ ] Traducción al idioma elegido (ver HU-05).

---

## Historia de Usuario: Sistema de Logs (⭐)

* **ID:** HU-04
* **Título:** Registro del proceso en archivo de log.
* **Prioridad:** Media
* **Historia de Usuario:**
  > Como desarrollador, quiero que el sistema registre cada paso del proceso en un archivo para poder auditar qué ocurrió en cada ejecución.

### Criterios de Aceptación:
- [x] Cada ejecución escribe en `logs/app.log` (creado automáticamente).
- [x] Se registra el formulario, la validación, la extracción, el procesamiento y la exportación.
- [x] Salida simultánea a consola y archivo, con formato `[fecha] [nivel] módulo: mensaje`.
- [x] Configuración centralizada en `src/logging_config.py`.
- [x] El archivo de log está excluido del repositorio en `.gitignore`.
- [x] Validado con `tests/test_logging_config.py`.

---

## Historia de Usuario: Traducción de Contenido

* **ID:** HU-05
* **Título:** Traducción de la variante elegida al idioma seleccionado.
* **Prioridad:** Alta
* **Estado:** Contrato entregado · implementación pendiente (asignada al equipo)
* **Historia de Usuario:**
  > Como usuario del sistema, quiero traducir la salida que he elegido al idioma que he seleccionado para poder consultarlo en otro idioma.

### Criterios de Aceptación:
- [ ] El sistema traduce el contenido usando la API de DeepTranslate.
- [ ] El contenido traducido se muestra en la terminal.
- [ ] El contenido traducido es el que se exporta al archivo.
- [x] El contrato está definido en `src/translator.py` (`translate(text, target_language) -> str`).
- [x] La integración está preparada: basta inyectar `ContentPipeline(translator=DeepTranslateTranslator())`.
- [x] Mientras no esté disponible, la validación rechaza la opción **antes** de procesar y explica el motivo.
- [x] Escenario Gherkin documentado: *"Pido traducir con el traductor aún no disponible"* (`@fallido`).

---

## Historia de Usuario: Generación de Archivos (⭐)

* **ID:** HU-06
* **Título:** Exportación exclusiva de la variante solicitada en TXT o PDF.
* **Prioridad:** Alta
* **Historia de Usuario:**
  > Como usuario, quiero que el archivo guardado contenga únicamente lo que he pedido, con un nombre que yo elijo.

### Criterios de Aceptación:
- [x] El usuario elige el formato (`txt` / `pdf`) y el nombre del archivo.
- [x] El archivo contiene **solo** el título y el cuerpo de la variante elegida: sin texto original adicional ni notas no solicitadas.
- [x] El TXT se escribe en UTF-8 **con BOM** para que Windows lo reconozca.
- [x] El PDF registra una fuente Unicode del sistema: los caracteres fuera de Helvetica (`ĭ`, `ē`, `²`, emojis) dejan de salir rotos.
- [x] El texto se escapa como XML antes de componer el PDF: las secuencias `<...>` del texto de Wikipedia ya no desaparecen.
- [x] El nombre de archivo se sanea (sin caracteres prohibidos por el SO).
- [x] Validado con `tests/test_exporter/` y `tests/features/export.feature` (`@exitoso` y `@fallido`).

---

## Historia de Usuario: Enriquecimiento con IA

* **ID:** HU-07
* **Título:** Enriquecer y resumir el contenido con inteligencia artificial.
* **Prioridad:** Alta
* **Estado:** Entregada (requiere `OPENAI_API_KEY` en `.env`)
* **Historia de Usuario:**
  > Como usuario, quiero que el sistema amplíe la información con IA y pueda resumirla, para obtener documentos de estudio más útiles.

### Criterios de Aceptación:
- [x] El sistema enriquece el texto con IA y lo muestra en la terminal.
- [x] El sistema genera resúmenes del contenido elegido (⭐).
- [x] Un fallo de la API se propaga como `AiError`: **nunca** se devuelve el original haciéndose pasar por enriquecido.
- [x] Sin credenciales, la opción "enriquecido" o "resumen" se rechaza en la validación con un mensaje accionable.
- [x] La clave, la URL base y el modelo (`AI_MODEL`) se configuran por variables de entorno.
- [x] `scripts/check_models.py` diagnostica la configuración en una ejecución.
- [x] Validado con `tests/test_enricher.py` (sin llamadas reales).

---

## Historia de Usuario: Pruebas automatizadas (⭐)

* **ID:** HU-08
* **Título:** Cobertura del 100 % y casos Gherkin de success y failed.
* **Prioridad:** Alta
* **Estado:** Entregada

### Criterios de Aceptación:
- [x] Todos los casos de test están documentados en formato Gherkin.
- [x] Existen escenarios de éxito (`@exitoso`) y de fallo controlado (`@fallido`).
- [x] Tests unitarios e integración sin salir de la CLI.
- [x] Cobertura del **100 %** sobre `src/` (`pytest --cov=src`).
- [x] Las pruebas que pegan a servicios externos van marcadas con `@pytest.mark.integration`.
