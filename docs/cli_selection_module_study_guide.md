# Guía de Módulo: Selección de Fuente de Contenido (CLI)

## Descripción General
Este módulo añade un punto de decisión interactivo dentro del pipeline de ejecución principal (`src/main.py`), permitiendo al usuario decidir qué variante del contenido continuará hacia las etapas posteriores de resumen, traducción y exportación documental.

---

## Ubicación y Flujo en la Arquitectura

1. **Investigación:** Extracción de párrafos desde Wikipedia (`WikipediaScraper`).
2. **Enriquecimiento IA:** Generación de contenido enriquecido mediante el cliente IA (`AiContentEnricher`).
3. **Punto de Selección (Nuevo):**
   - **Opción 1:** Conservar el texto original de Wikipedia.
   - **Opción 2:** Conservar el contenido enriquecido por IA.
4. **Etapas Posteriores:**
   - Resumen ejecutivo (opcional).
   - Traducción multilingüe (opcional).
   - Generación del informe final en formato TXT o PDF (`DocumentExporter`).

---

## Implementación Técnica

### 1. `src/main.py`
Se integra la función interactiva `ask_choice` dentro del bloque condicional `if enricher:`:

```python
if enricher:
    print("[2/5] Enriqueciendo el contenido con IA...")
    enriched = enrich_content(enricher, research["text"])
    show_section("CONTENIDO ENRIQUECIDO (IA)", enriched)

    print("¿Deseas conservar el contenido enriquecido por IA o el original de Wikipedia?")
    print("  1. Texto original de Wikipedia")
    print("  2. Contenido enriquecido por IA")

    if ask_choice("➤ Elige una opción (1 / 2): ", ("1", "2")) == "1":
        enriched = research["text"]
        print("✓ Se mantendrá el texto original de Wikipedia.\n")
    else:
        print("✓ Se continuará con el contenido enriquecido por IA.\n")
else:
    enriched = ""
    print("[2/5] Enriquecimiento omitido: no hay credenciales de IA.")
```
## 2. Comportamiento ante Fallbacks
Si no existen credenciales de IA (OPENAI_API_KEY), el menú interactivo se omite de forma transparente y el pipeline continúa con el texto extraído originalmente.

La validación restringe la entrada estrictamente a los valores numéricos válidos (1 o 2), repitiendo la consulta ante entradas erróneas.

### Cobertura de Pruebas (tests/test_main.py)
Se actualizaron los mocks de consola (builtins.input) para suministrar la selección requerida en los flujos completos con IA activa.

Se incorporó la prueba unitaria test_export_saves_original_wikipedia_if_chosen para asegurar que la elección de la opción 1 descarte el texto sintetizado y conserve la versión base de Wikipedia.



