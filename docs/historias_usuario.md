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
- [x] Si el tema no coincide con el título del artículo, se lanza una búsqueda de respaldo en la API de Wikipedia para localizar el artículo más relevante.
- [x] Tests unitarios sin red (`tests/test_scraper.py`) y escenarios BDD marcados como integración (`pytest -m integration`).

---

## Historia de Usuario: Integración del Flujo Completo (Pipeline + CLI)

* **ID:** HU-02
* **Título:** Investigar, enriquecer, resumir y exportar en un solo flujo.
* **Prioridad:** Alta
* **Historia de Usuario:**
  > Como usuario del sistema, quiero introducir un tema y un idioma en la terminal para obtener un informe final en `.txt` o `.pdf` con el contenido original, enriquecido y traducido, sin salir de la aplicación.

### Criterios de Aceptación:
- [x] La CLI solicita el tema y el idioma de traducción antes de empezar.
- [x] Muestra los resultados de Wikipedia en la terminal antes de pedir acciones adicionales.
- [x] Enriquece el contenido con IA y lo muestra en pantalla.
- [x] Permite generar un resumen del contenido enriquecido (⭐) y mostrarlo.
- [x] Pregunta si se desea guardar, el formato (`txt`/`pdf`) y el nombre del archivo (⭐).
- [x] Sin `OPENAI_API_KEY` el flujo continúa con el contenido original (degradación elegante).
- [x] La lógica vive en `src/pipeline.py`; `src/main.py` solo maneja la entrada/salida del usuario.
- [x] Validado con `tests/test_pipeline.py` (sin red ni IA real).

### Criterios pendientes:
- [ ] Traducción al idioma elegido (ver HU-04).

---

## Historia de Usuario: Sistema de Logs (⭐)

* **ID:** HU-03
* **Título:** Registro del proceso en archivo de log.
* **Prioridad:** Media
* **Historia de Usuario:**
  > Como desarrollador, quiero que el sistema registre cada paso del proceso en un archivo para poder auditar qué ocurrió en cada ejecución.

### Criterios de Aceptación:
- [x] Cada ejecución escribe en `logs/app.log` (creado automáticamente).
- [x] Se registra la solicitud, la extracción de Wikipedia, la IA, la traducción y la exportación.
- [x] Salida simultánea a consola y archivo, con formato `[fecha] [nivel] módulo: mensaje`.
- [x] Configuración centralizada en `src/logging_config.py`.
- [x] El archivo de log está excluido del repositorio en `.gitignore`.
- [x] Validado con `tests/test_logging_config.py`.

---

## Historia de Usuario: Traducción de Contenido

* **ID:** HU-04
* **Título:** Traducción del contenido enriquecido al idioma elegido.
* **Prioridad:** Alta
* **Estado:** En desarrollo (módulo asignado al equipo)
* **Historia de Usuario:**
  > Como usuario del sistema, quiero que el contenido enriquecido se traduzca al idioma que he elegido para poder consultarlo en otro idioma.

### Criterios de Aceptación:
- [ ] El sistema traduce el contenido usando la API de traducción acordada por el equipo.
- [ ] El contenido traducido se muestra en la terminal.
- [ ] El contenido traducido se incluye en la sección 3 del informe.
- [x] Integración preparada: basta inyectar el módulo en `ContentPipeline(translator=...)` con la interfaz `translate(text, target_language) -> str`.
- [x] Mientras no esté disponible, la sección 3 queda vacía y la CLI muestra el aviso correspondiente.
