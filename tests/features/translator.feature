# language: es
Característica: Traducción del contenido con DeepTranslateService
  Como usuario del Content Enricher
  Quiero elegir un idioma de destino
  Para leer el contenido investigado y enriquecido en ese idioma

  # La API de MyMemory siempre está simulada: los tests no gastan cuota.

  # --- Traducción ---------------------------------------------------------

  @exitoso
  Escenario: Traducir una frase corta al idioma elegido
    Dado el texto "Hola, buenos días."
    Cuando lo traduzco al idioma "inglés"
    Entonces obtengo el texto traducido "Hello, good morning."
    Y la API recibe el código de idioma "en-GB"

  @exitoso
  Escenario: Traducir el contenido enriquecido y el resumen
    Dado un contenido enriquecido y su resumen
    Cuando traduzco los dos textos al idioma "francés"
    Entonces obtengo los dos textos traducidos

  @exitoso
  Escenario: Traducir un texto largo dividido en trozos
    Dado un texto de más de 500 caracteres
    Cuando lo traduzco al idioma "en-GB"
    Entonces la API recibe varios trozos de 400 caracteres como máximo
    Y la traducción une los trozos en el mismo orden

  @exitoso
  Escenario: Conservar los párrafos del texto
    Dado el texto "Primer párrafo.\n\nSegundo párrafo."
    Cuando lo traduzco al idioma "inglés"
    Entonces la traducción mantiene los saltos de línea

  @exitoso
  Escenario: Mostrar la traducción en la terminal
    Dado el texto traducido "Hello, good morning."
    Cuando muestro la traducción
    Entonces la terminal muestra "=== CONTENIDO TRADUCIDO ==="
    Y la terminal muestra "Hello, good morning."

  @exitoso
  Escenario: Enviar a MyMemory el email opcional del .env
    Dado que el archivo .env tiene MYMEMORY_EMAIL "alumno@ejemplo.com"
    Cuando traduzco el texto "Hola." al idioma "inglés"
    Entonces MyMemory recibe el origen "es-ES", el destino "en-GB" y el email

  @fallido
  Escenario: Traducir a un idioma no válido
    Dado el texto "Hola."
    Cuando intento traducirlo al idioma "klingon"
    Entonces se muestra el error "no existe o está mal escrito"
    Y no se llama a la API de traducción

  @fallido
  Escenario: Traducir un texto vacío
    Dado el texto "   "
    Cuando intento traducirlo al idioma "inglés"
    Entonces se muestra el error "No hay ningún texto que traducir"
    Y no se llama a la API de traducción

  @fallido
  Escenario: Superar el límite de peticiones
    Dado que la API responde "demasiadas peticiones"
    Cuando intento traducir el texto "Hola." al idioma "inglés"
    Entonces se muestra el error "límite de peticiones"

  @fallido
  Escenario: Agotar la cuota diaria de MyMemory
    Dado que la API devuelve el aviso "MYMEMORY WARNING: YOU USED ALL AVAILABLE FREE TRANSLATIONS FOR TODAY"
    Cuando intento traducir el texto "Hola." al idioma "inglés"
    Entonces se muestra el error "cuota diaria"

  @fallido
  Escenario: La API tarda demasiado en responder
    Dado que la API no responde a tiempo
    Cuando intento traducir el texto "Hola." al idioma "inglés"
    Entonces se muestra el error "ha tardado demasiado"

  @fallido
  Escenario: No hay conexión con el servicio de traducción
    Dado que no hay conexión a internet
    Cuando intento traducir el texto "Hola." al idioma "inglés"
    Entonces se muestra el error "Revisa tu conexión"

  @fallido
  Escenario: Un fragmento sin espacios demasiado largo
    Dado una palabra de 600 letras sin espacios
    Cuando intento traducirla al idioma "inglés"
    Entonces se muestra el error "demasiado largo"

  @fallido
  Escenario: Usar "auto" como idioma de origen
    Cuando creo el servicio con el idioma de origen "auto"
    Entonces se muestra el error "no existe o está mal escrito"

  # --- Troceado de textos --------------------------------------------------

  @exitoso
  Escenario: Trocear un texto corto
    Dado el texto "Hola. ¿Qué tal?"
    Cuando lo divido en trozos de 400 caracteres
    Entonces obtengo 1 trozo igual al texto

  @exitoso
  Escenario: Trocear un texto largo por frases
    Dado un texto de 20 frases iguales
    Cuando lo divido en trozos de 400 caracteres
    Entonces obtengo varios trozos de 400 caracteres como máximo
    Y ningún trozo corta una frase

  @exitoso
  Escenario: Trocear una frase sola más larga que el límite
    Dado una frase de 120 palabras sin puntos intermedios
    Cuando lo divido en trozos de 400 caracteres
    Entonces obtengo varios trozos de 400 caracteres como máximo
    Y ninguna palabra queda cortada

  @fallido
  Escenario: Trocear un texto vacío
    Dado el texto ""
    Cuando lo divido en trozos de 400 caracteres
    Entonces obtengo una lista vacía

  # --- Validación del idioma -----------------------------------------------

  @exitoso
  Esquema del escenario: Escribir un idioma válido
    Cuando escribo el idioma <entrada>
    Entonces el idioma se considera válido
    Y obtengo el código "<código>"

    Ejemplos:
      | entrada        | código | caso                         |
      | "español"      | es-ES  | nombre en español            |
      | "espanol"      | es-ES  | nombre en español sin tilde  |
      | "  INGLÉS  "   | en-GB  | mayúsculas y espacios        |
      | "french"       | fr-FR  | nombre en inglés             |
      | "de-DE"        | de-DE  | código de MyMemory           |

  @fallido
  Esquema del escenario: Escribir un idioma con errores
    Cuando escribo el idioma <entrada>
    Entonces el idioma se considera no válido
    Y se muestra el error "<mensaje>"

    Ejemplos:
      | entrada    | mensaje                     | caso                       |
      | "espanil"  | no existe o está mal escrito | una letra mal              |
      | "3spañol"  | contiene números            | número colado              |
      | "123"      | contiene números            | solo números               |
      | ""         | No has escrito ningún idioma | vacío                      |
      | "mesa"     | no existe o está mal escrito | texto que no es un idioma  |

  @exitoso
  Escenario: Un intento fallido y después uno correcto
    Dado que el usuario escribe "espanil" y después "francés"
    Cuando se le pide el idioma
    Entonces se muestra el aviso "no existe o está mal escrito"
    Y el idioma elegido es "fr-FR"

  @fallido
  Escenario: Agotar los intentos
    Dado que el usuario escribe "3spañol", "123" y ""
    Cuando se le pide el idioma con 3 intentos
    Entonces se muestra el error "Has agotado los 3 intentos"
