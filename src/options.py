"""Opciones del formulario de salida y validación de la matriz de control.

Este módulo es **puro**: no lee ``input()`` ni toca la red. Recibe las
decisiones ya tomadas por el usuario y devuelve la lista completa de errores
(jamás solo el primero), de modo que la CLI pueda mostrarlos todos de una vez.

La matriz de control se reduce a dos ejes independientes:

    content_mode  ∈ {ORIGINAL, ENRICHED}     # eje A
    resumir       ∈ {False, True}             # eje B
    idioma        ∈ {None, "xx"}              # transformación final

El producto A × B genera las 4 variantes de contenido; ``idioma`` se aplica
siempre al final sobre la variante elegida. Con eso se cubren las 6
variaciones del documento de requisitos sin necesidad de un ``switch`` de 6
casos.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

FORMATOS_VALIDOS: Tuple[str, ...] = ("txt", "pdf")

# El usuario escribe en español; el valor del enum se mantiene en inglés.
ALIAS_EN_ESPANOL = {"enriquecido": "enriched"}


class ContentMode(Enum):
    """Modo de contenido elegido por el usuario (eje A)."""

    ORIGINAL = "original"
    ENRICHED = "enriched"

    @classmethod
    def desde(cls, valor: str) -> "ContentMode":
        """Convierte la respuesta cruda de la CLI en un modo válido.

        Acepta tanto el valor del enum (``enriched``) como su nombre en
        español (``enriquecido``).

        Raises:
            ValueError: si el valor no corresponde a ningún modo.
        """
        normalizado = valor.strip().lower()
        normalizado = ALIAS_EN_ESPANOL.get(normalizado, normalizado)
        try:
            return cls(normalizado)
        except ValueError:
            opciones = ", ".join(modo.value for modo in cls)
            raise ValueError(f"Modo de contenido no válido: '{valor}'. Usa uno de: {opciones}.")


class Variant(Enum):
    """Las 4 salidas de contenido posibles (producto eje A × eje B)."""

    ORIGINAL = "original"
    ORIGINAL_SUMMARY = "original_summary"
    ENRICHED = "enriched"
    ENRICHED_SUMMARY = "enriched_summary"

    @property
    def titulo(self) -> str:
        """Rótulo corto que identifica la variante en la terminal."""
        return {
            Variant.ORIGINAL: "Texto original",
            Variant.ORIGINAL_SUMMARY: "Resumen del texto original",
            Variant.ENRICHED: "Contenido enriquecido",
            Variant.ENRICHED_SUMMARY: "Contenido enriquecido + resumen",
        }[self]


@dataclass(frozen=True)
class OutputOptions:
    """Esquema de datos capturado por el formulario de opciones de respuesta.

    Attributes:
        tema: Tema a investigar en Wikipedia. Obligatorio y no vacío.
        content_mode: Si la salida es el texto original o el enriquecido por IA.
        resumir: ``True`` si además se quiere la síntesis del texto elegido.
        idioma: Código de traducción (``"en"``, ``"fr"``...). ``None`` mantiene
            el idioma original.
        formato: ``"txt"`` o ``"pdf"``. Solo se rellena si se va a exportar.
        nombre: Nombre del archivo (sin extensión). Solo al exportar.
    """

    tema: str
    content_mode: ContentMode
    resumir: bool = False
    idioma: Optional[str] = None
    formato: Optional[str] = None
    nombre: Optional[str] = None

    @property
    def variante(self) -> Variant:
        """Resuelve la variante exacta que debe terminar en pantalla y en el archivo."""
        prefijo = (
            Variant.ENRICHED
            if self.content_mode is ContentMode.ENRICHED
            else Variant.ORIGINAL
        )
        if not self.resumir:
            return prefijo
        return (
            Variant.ENRICHED_SUMMARY
            if prefijo is Variant.ENRICHED
            else Variant.ORIGINAL_SUMMARY
        )

    @property
    def requiere_ia(self) -> bool:
        """La IA es obligatoria si se pidió enriquecer o resumir."""
        return self.content_mode is ContentMode.ENRICHED or self.resumir


def validar(
    opciones: OutputOptions,
    ia_disponible: bool,
    traductor_disponible: bool,
) -> List[str]:
    """Valida la combinación elegida contra las capacidades realmente disponibles.

    Se comprueba **antes** de llamar a la red para que el usuario reciba todos
    los problemas de una sola vez y no se genere ningún archivo a medias.

    Args:
        opciones: Opciones capturadas por el formulario.
        ia_disponible: ``True`` si hay un enriquecedor con credenciales.
        traductor_disponible: ``True`` si hay un traductor inyectado y operativo.

    Returns:
        Lista vacía si la combinación es válida; en caso contrario, una lista
        con todos los motivos de rechazo (nunca solo el primero).
    """
    errores: List[str] = []

    if not opciones.tema or not opciones.tema.strip():
        errores.append("El tema a investigar no puede estar vacío.")

    if opciones.requiere_ia and not ia_disponible:
        if opciones.content_mode is ContentMode.ENRICHED:
            errores.append(
                "El modo 'enriquecido' necesita IA, pero no hay credenciales "
                "configuradas. Usa el modo 'original' o revisa OPENAI_API_KEY."
            )
        if opciones.resumir:
            errores.append(
                "El resumen necesita IA, pero no hay credenciales configuradas. "
                "Desactiva el resumen o revisa OPENAI_API_KEY."
            )

    if opciones.idioma and not traductor_disponible:
        errores.append(
            f"Se pidió traducir al idioma '{opciones.idioma}', pero el módulo de "
            "traducción aún no está disponible. Mantén el idioma original."
        )

    if opciones.formato is not None and opciones.formato not in FORMATOS_VALIDOS:
        permitidos = " / ".join(FORMATOS_VALIDOS)
        errores.append(f"Formato no soportado: '{opciones.formato}'. Usa {permitidos}.")

    if opciones.formato is not None and not (opciones.nombre or "").strip():
        errores.append("El nombre del archivo no puede estar vacío.")

    return errores
