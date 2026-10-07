# language: es
Característica: Exportación exclusiva de la variante solicitada
  Como usuario del Content Enricher
  Quiero que el archivo guardado contenga únicamente lo que pedí
  Para no recibir el texto original ni notas que no he solicitado

  @exitoso
  Escenario: Guardar solo la variante pedida en TXT
    Dado un informe con título "Mujer" y cuerpo "Resumen traducido al francés"
    Cuando exporto el informe en formato "txt"
    Entonces el archivo se crea correctamente
    Y el archivo contiene el título "Mujer"
    Y el archivo contiene el cuerpo "Resumen traducido al francés"
    Y el archivo no contiene "Texto original"

  @exitoso
  Escenario: Guardar solo la variante pedida en PDF
    Dado un informe con título "Mujer" y cuerpo "Contenido enriquecido"
    Cuando exporto el informe en formato "pdf"
    Entonces el archivo se crea correctamente
    Y el informe entregado al exportador solo contiene título y cuerpo

  @exitoso
  Escenario: El TXT se guarda en UTF-8 reconocible por Windows
    Dado un informe con título "Camas" y cuerpo "Contenido con tildes: investigación"
    Cuando exporto el informe en formato "txt"
    Entonces el archivo se crea correctamente
    Y el archivo empieza por la marca UTF-8

  @exitoso
  Escenario: El PDF soporta caracteres fuera del repertorio de Helvetica
    Dado un informe con título "Mujer" y cuerpo "Del latín mulĭer, -ēris: 11,66 km²"
    Cuando exporto el informe en formato "pdf"
    Entonces el archivo se crea correctamente

  @fallido
  Escenario: Exportar con un formato no soportado
    Dado un informe con título "Camas" y cuerpo "Contenido"
    Cuando intento exportar en formato "docx"
    Entonces la exportación falla con el mensaje "no permitido"
    Y no se crea ningún archivo

  @fallido
  Escenario: Exportar sin nombre de archivo
    Dado un informe con título "Camas" y cuerpo "Contenido"
    Cuando intento exportar con el nombre "   " en formato "txt"
    Entonces la exportación falla con el mensaje "no puede estar vacío"
    Y no se crea ningún archivo

  @fallido
  Escenario: Exportar un informe sin cuerpo
    Dado un informe con título "Camas"
    Cuando intento exportar en formato "txt"
    Entonces la exportación falla con el mensaje "Faltan datos obligatorios"
    Y no se crea ningún archivo
