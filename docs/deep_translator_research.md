# Investigación: `deep_translator` y MyMemory

Notas de la subtarea "investigar y documentar la librería". Todo lo que aparece
aquí se ha comprobado leyendo el código instalado en `.venv`
(`deep_translator/mymemory.py`, `base.py`, `validate.py` y `exceptions.py`)
y con una petición real.

- **Versión instalada:** `deep-translator==1.11.4` (Python 3.14, funciona sin problemas).
- **Clase usada:** `MyMemoryTranslator(source, target, proxies=None, **kwargs)`.
- **API real:** `GET http://api.mymemory.translated.net/get` con los
  parámetros `q` (texto), `langpair` (`origen|destino`) y `de` (email).
- **Sin clave de API.** MyMemory es gratuita.

## Códigos de idioma

- MyMemory **no** usa códigos cortos como `en` o `fr`. Usa códigos con región:
  `en-GB`, `es-ES`, `fr-FR`, `de-DE`, `zh-CN`…
- `MyMemoryTranslator("en")` lanza `LanguageNotSupportedException`.
- También acepta el nombre en inglés y en minúsculas: `english`, `french`…
- Lista completa (nombre → código):

  ```python
  MyMemoryTranslator(source="es-ES", target="en-GB").get_supported_languages(as_dict=True)
  ```

## Idioma de origen `auto`

- La librería **acepta** `source="auto"` sin quejarse (es su valor por defecto).
- Pero la **API de MyMemory lo rechaza**. Prueba real:

  ```text
  'AUTO' IS AN INVALID SOURCE LANGUAGE . EXAMPLE: LANGPAIR=EN|IT ...
  ```

  Además devuelve ese error **como si fuera la traducción** (respuesta 200).
- **Decisión:** el idioma de origen es configurable en `DeepTranslateTranslator`
  y vale `es-ES` por defecto, porque el scraper lee de `es.wikipedia.org`.

## Límite de texto por petición

- `translate()` llama a `is_input_valid(text, max_chars=500)`, que comprueba
  `len(text) < 500`. Es decir, cuenta **caracteres** (no bytes) y el máximo
  real son **499**.
- Si se supera, lanza `NotValidLength`.
- La documentación de MyMemory habla de 500 **bytes**, y las tildes y la `ñ`
  ocupan 2 bytes en UTF-8. Por eso troceamos con un margen: **400 caracteres**.
- `translate_batch()` existe, pero solo traduce una lista de textos uno a uno
  (no trocea). El troceado lo hacemos nosotros con `split_text`.

## Email opcional

- `email` se recibe por `**kwargs` y se envía como parámetro `de`.
- Sirve para subir el límite diario gratuito de MyMemory. Si no se pasa, funciona igual.
- En el proyecto se lee de la variable `MYMEMORY_EMAIL` del `.env`.

## Timeout

- La librería **no permite fijar un timeout**: llama a `requests.get(...)` sin
  el parámetro `timeout` y no hay ninguna opción para pasarlo.
- No lo inventamos. Capturamos los errores de red de `requests`:
  `requests.exceptions.Timeout` y `requests.exceptions.ConnectionError`.

## Excepciones que nos interesan

| Situación | Qué lanza la librería |
|---|---|
| Respuesta HTTP 429 (demasiadas peticiones) | `TooManyRequests` |
| Otra respuesta HTTP fuera de 2xx | `RequestError` |
| Texto de 500 caracteres o más | `NotValidLength` |
| Idioma no soportado | `LanguageNotSupportedException` |
| Red caída / sin respuesta | `requests.exceptions.ConnectionError` / `Timeout` |

Otros detalles del código:

- Si se agota la cuota diaria, MyMemory responde con código 200 y un texto que
  empieza por `MYMEMORY WARNING`. El servicio lo detecta y lo trata como límite de peticiones.
- Si origen y destino son iguales, devuelve el texto sin llamar a la API.
- Un texto vacío se devuelve tal cual, sin llamar a la API.
