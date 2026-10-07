# Guía del servicio de traducción (DeepTranslateTranslator)

Traduce el contenido enriquecido y el resumen al idioma que elige el usuario,
usando `deep_translator` (`MyMemoryTranslator`). Solo traduce: no investiga,
no enriquece y no exporta.

Detalles de la librería: [deep_translator_research.md](deep_translator_research.md).

## Archivos

| Archivo | Qué contiene |
|---|---|
| `src/translator.py` | Clase `DeepTranslateTranslator` (traducir y mostrar) |
| `src/language_validator.py` | Validación del idioma y `ask_language` |
| `src/text_splitter.py` | `split_text`: trocea textos largos |
| `src/translation_errors.py` | Errores propios del servicio |

## Interfaz (lo único de lo que deben depender los demás módulos)

```python
from src.translator import DeepTranslateTranslator

service = DeepTranslateTranslator()  # origen "es-ES" por defecto
texto_traducido = service.translate(texto, "inglés")
```

- `translate(text, target_language) -> str`
  - `text`: cualquier longitud. Se trocea solo y se conservan los párrafos.
  - `target_language`: nombre en español (`"inglés"`, `"frances"`), nombre en
    inglés (`"english"`) o código de MyMemory (`"en-GB"`). Da igual si va en
    mayúsculas o con espacios.
  - Devuelve el texto traducido.
- `show_translation(translated_text, title="CONTENIDO TRADUCIDO")`: imprime
  `=== TÍTULO ===` y el texto, igual que la CLI.

Para traducir el contenido enriquecido y el resumen, se llama dos veces:

```python
enriquecido_traducido = service.translate(enriquecido, idioma)
resumen_traducido = service.translate(resumen, idioma)
service.show_translation(enriquecido_traducido)
service.show_translation(resumen_traducido, "RESUMEN TRADUCIDO")
```

## Pedir el idioma al usuario

```python
from src.language_validator import ask_language

codigo = ask_language()   # devuelve, por ejemplo, "fr-FR"
```

Pide el idioma hasta 3 veces. Si se escribe mal (`"espanil"`, `"3spañol"`,
vacío…), muestra el motivo y lo vuelve a pedir. No sugiere idiomas parecidos.
Si se agotan los intentos, lanza `InvalidLanguageError`.

> Ojo: MyMemory no acepta códigos cortos como `en` o `fr`. Usa `en-GB`,
> `fr-FR`… o el nombre del idioma.

## Errores

Todos heredan de `TranslationServiceError`. Basta con capturar ese tipo y
mostrar `str(error)` al usuario: los mensajes ya están en español.

| Error | Cuándo |
|---|---|
| `InvalidLanguageError` | Idioma vacío, con números o inexistente |
| `EmptyTextError` | No hay texto que traducir |
| `RateLimitError` | Límite de peticiones o cuota diaria agotada |
| `TranslationTimeoutError` | MyMemory tarda demasiado en responder |
| `NoConnectionError` | Sin conexión o error del servidor |
| `TextTooLongError` | Fragmento sin espacios de 500 caracteres o más |

```python
from src.translation_errors import TranslationServiceError

try:
    traducido = service.translate(texto, idioma)
except TranslationServiceError as error:
    print(f"🔴 No se pudo traducir: {error}")
```

## Configuración (.env)

```bash
# Opcional: sube el límite diario gratuito de MyMemory
MYMEMORY_EMAIL=
```

No hace falta clave de API. Sin email también funciona.

## Pruebas

```bash
.venv\Scripts\python.exe -m pytest --cov=src --cov-report=term-missing
```

Los tests nunca llaman a MyMemory: el método `_call_mymemory` se simula.
Escenarios Gherkin: `tests/features/translator.feature`.
