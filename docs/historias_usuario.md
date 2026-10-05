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
