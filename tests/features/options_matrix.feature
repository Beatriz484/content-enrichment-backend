# language: es
Característica: Matriz de control de las opciones de respuesta
  Como usuario del Content Enricher
  Quiero elegir el modo de contenido, el resumen y el idioma
  Para recibir exactamente la salida que pedí y nada más

  @exitoso
  Escenario: Consulta simple sin ninguna transformación
    Dado que investigué el tema "Python"
    Cuando elijo modo "original", resumen "no" e idioma "ninguno"
    Cuando valido las opciones seleccionadas
    Cuando aplico la matriz de control
    Entonces la variante resuelta es "Texto original"
    Y el cuerpo del informe es "Texto extraído de Wikipedia."

  @exitoso
  Escenario: Solo texto original
    Dado que investigué el tema "Camas"
    Cuando elijo modo "original", resumen "no" e idioma "ninguno"
    Cuando valido las opciones seleccionadas
    Cuando aplico la matriz de control
    Entonces la variante resuelta es "Texto original"
    Y el cuerpo del informe es "Texto extraído de Wikipedia."

  @exitoso
  Escenario: Solo contenido enriquecido
    Dado que investigué el tema "Camas"
    Cuando elijo modo "enriquecido", resumen "no" e idioma "ninguno"
    Cuando valido las opciones seleccionadas
    Cuando aplico la matriz de control
    Entonces la variante resuelta es "Contenido enriquecido"
    Y el cuerpo del informe es "Contenido ampliado por IA."

  @exitoso
  Escenario: Solo resumen del texto original
    Dado que investigué el tema "Camas"
    Cuando elijo modo "original", resumen "sí" e idioma "ninguno"
    Cuando valido las opciones seleccionadas
    Cuando aplico la matriz de control
    Entonces la variante resuelta es "Resumen del texto original"
    Y el cuerpo del informe es "Resumen del contenido."

  @exitoso
  Escenario: Contenido enriquecido con resumen
    Dado que investigué el tema "Camas"
    Cuando elijo modo "enriquecido", resumen "sí" e idioma "ninguno"
    Cuando valido las opciones seleccionadas
    Cuando aplico la matriz de control
    Entonces la variante resuelta es "Contenido enriquecido + resumen"
    Y el cuerpo del informe es "Resumen del contenido."

  @exitoso
  Escenario: Traducción de la variante elegida
    Dado que investigué el tema "Camas"
    Dado que el traductor está disponible
    Cuando elijo modo "enriquecido", resumen "sí" e idioma "fr"
    Cuando valido las opciones seleccionadas
    Cuando aplico la matriz de control
    Entonces la variante resuelta es "Contenido enriquecido + resumen"
    Y el cuerpo del informe es "Contenido traducido al idioma solicitado."

  @exitoso
  Escenario: El informe nunca arrastra el texto original no pedido
    Dado que investigué el tema "Camas"
    Cuando elijo modo "enriquecido", resumen "sí" e idioma "ninguno"
    Cuando valido las opciones seleccionadas
    Cuando aplico la matriz de control
    Entonces el cuerpo del informe es "Resumen del contenido."
    Y el informe no contiene "Texto extraído de Wikipedia."

  @fallido
  Escenario: Pido enriquecer sin credenciales de IA
    Dado que investigué el tema "Camas"
    Dado que no hay credenciales de IA
    Cuando elijo modo "enriquecido", resumen "no" e idioma "ninguno"
    Cuando valido las opciones seleccionadas
    Entonces el sistema informa que "El modo 'enriquecido' necesita IA"
    Y no se genera ningún informe

  @fallido
  Escenario: Pido un resumen sin credenciales de IA
    Dado que investigué el tema "Camas"
    Dado que no hay credenciales de IA
    Cuando elijo modo "original", resumen "sí" e idioma "ninguno"
    Cuando valido las opciones seleccionadas
    Entonces el sistema informa que "El resumen necesita IA"
    Y no se genera ningún informe

  @fallido
  Escenario: Pido traducir con el traductor aún no disponible
    Dado que investigué el tema "Camas"
    Cuando elijo modo "original", resumen "no" e idioma "fr"
    Cuando valido las opciones seleccionadas
    Entonces el sistema informa que "el módulo de traducción"
    Y no se genera ningún informe

  @fallido
  Escenario: Pido un tema vacío
    Dado que investigué el tema "   "
    Cuando elijo modo "original", resumen "no" e idioma "ninguno"
    Cuando valido las opciones seleccionadas
    Entonces el sistema informa que "El tema a investigar no puede estar vacío"
    Y no se genera ningún informe

  @fallido
  Escenario: Ningún servicio disponible para una variante que lo exige
    Dado que investigué el tema "Camas"
    Dado que no hay credenciales de IA
    Cuando elijo modo "enriquecido", resumen "sí" e idioma "fr"
    Cuando valido las opciones seleccionadas
    Entonces el sistema informa que "El modo 'enriquecido' necesita IA"
    Y el sistema informa que "El resumen necesita IA"
    Y el sistema informa que "el módulo de traducción"
    Y no se genera ningún informe
