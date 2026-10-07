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

## Historia de Usuario: Interacción por etapas y resultado único de exportación

* **ID:** HU-02
* **Título:** Cada decisión en su momento, un solo resultado al final.
* **Prioridad:** Alta
* **Estado:** Entregada
* **Historia de Usuario:**
  > Como usuario del sistema, quiero indicar primero el tema y que cada decisión (resumen e idioma) se me pregunte en el momento en que le toca, para recibir un único resultado final con lo último que he pedido y nada más.

### Criterios de Aceptación:
- [x] La CLI pide **solo el tema** al arrancar; el resumen se pregunta tras ver el contenido enriquecido y el idioma justo antes de traducir (la **última petición**). El diálogo vive en `src/main.py`.
- [x] La extracción de Wikipedia se muestra en terminal **antes** de solicitar cualquier acción adicional.
- [x] Cada pregunta repite la entrada hasta recibir un valor válido (texto no vacío, sí/no, formato `txt`/`pdf`).
- [x] El orden del procesamiento es fijo: `base → resumen → traducción`, y la traducción se aplica **siempre al final**.
- [x] El archivo exportado contiene **exclusivamente** el título y el resultado final (traducción, resumen, contenido enriquecido o texto original): no se eligen secciones.
- [x] Sin credenciales de IA la CLI avisa y continúa con el texto original; sin traductor entregado avisa y omite la traducción: nunca una degradación silenciosa.
- [x] Validado con `tests/test_main.py` (sin red ni IA real).

---

## Historia de Usuario: Integración del Flujo Completo (Pipeline + CLI)

* **ID:** HU-03
* **Título:** Investigar, procesar y exportar en un solo flujo.
* **Prioridad:** Alta
* **Historia de Usuario:**
  > Como usuario del sistema, quiero introducir un tema en la terminal para obtener un informe final en `.txt` o `.pdf` con el resultado de lo que he pedido, sin salir de la aplicación.

### Criterios de Aceptación:
- [x] La CLI solicita solo el tema al empezar; resumen e idioma se preguntan en su momento, tras mostrar la búsqueda.
- [x] Muestra los resultados de Wikipedia en la terminal antes de pedir acciones adicionales.
- [x] Muestra cada paso realmente ejecutado (enriquecido, resumen, traducido) e indica los pasos omitidos.
- [x] Pregunta si desea guardar, el formato `txt`/`pdf` y el nombre del archivo (⭐); el archivo recibe **un único resultado**.
- [x] La lógica vive en cada módulo (`scraper`, `enricher`, `translator`, `exporter`); `src/main.py` solo orquesta la entrada/salida.
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
- [x] Se registran las opciones capturadas, la extracción, el procesamiento y la exportación.
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
- [x] La integración está preparada: `src/main.py` invoca `DeepTranslateTranslator().translate(...)`.
- [x] Mientras no esté disponible, la CLI avisa con el motivo (*"Traducción omitida"*) y continúa con el contenido sin traducir.
- [x] Validado con `tests/test_main.py::test_flow_reports_unavailable_translation` y `tests/test_translator.py`.

---

## Historia de Usuario: Generación de Archivos (⭐)

* **ID:** HU-06
* **Título:** Exportación de un único resultado en TXT o PDF.
* **Prioridad:** Alta
* **Historia de Usuario:**
  > Como usuario, quiero que el archivo guardado contenga únicamente lo que he pedido —el resultado final—, con un nombre que yo elijo.

### Criterios de Aceptación:
- [x] El usuario confirma si desea guardar, elige el formato (`txt` / `pdf`) y el nombre del archivo; no se le pregunta qué partes incluir.
- [x] El cuerpo del archivo es **un solo resultado**: la traducción si se pidió; si no, el resumen, el contenido enriquecido o el texto original.
- [x] El archivo contiene **solo** el título y ese cuerpo: sin texto original adicional ni notas no solicitadas.
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
- [x] Un fallo de la API se registra en el log (`IA no disponible`) y no interrumpe el flujo.
- [x] Sin credenciales, la CLI avisa al arrancar, omite enriquecimiento y resumen y continúa con el texto original.
- [x] La clave y la URL base se configuran por variables de entorno.
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
