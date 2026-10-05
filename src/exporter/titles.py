"""Rótulos de las secciones del informe.

Los títulos reflejan lo que **realmente** ocurrió en el flujo: si la IA no
actuó o el traductor sigue en desarrollo, el informe lo dice explícitamente en
lugar de prometer contenido que no existe. Una única fuente de verdad para que
TXT y PDF digan exactamente lo mismo.
"""
from typing import Any, Dict

NOTA_TRADUCCION_PENDIENTE = (
    "El módulo de traducción aún no está disponible; "
    "esta sección se completará automáticamente cuando esté integrado."
)


def ia_actuo(content_data: Dict[str, Any]) -> bool:
    """Indica si la sección 2 fue realmente producida por la IA.

    Se usa la bandera explícita ``enriched_with_ai`` si existe; si no, se
    infiere comparando el texto enriquecido con el original (si son iguales,
    la IA no llegó a actuar).
    """
    bandera = content_data.get("enriched_with_ai")
    if bandera is None:
        return str(content_data.get("enriched_text") or "") != str(
            content_data.get("raw_text") or ""
        )
    return bool(bandera)


def hay_traduccion(content_data: Dict[str, Any]) -> bool:
    """Indica si la sección 3 tiene contenido traducido real."""
    return bool(str(content_data.get("translated_text") or "").strip())


def titulos_del_informe(content_data: Dict[str, Any]) -> Dict[str, str]:
    """Devuelve el rótulo de cada sección del informe según el flujo ejecutado."""
    if ia_actuo(content_data):
        enriquecimiento = "2. Contenido Enriquecido (IA)"
    else:
        enriquecimiento = "2. Contenido Sin Enriquecer (IA no disponible)"

    traduccion = (
        "3. Contenido Traducido"
        if hay_traduccion(content_data)
        else "3. Contenido Traducido (pendiente)"
    )

    return {
        "original": "1. Contenido Original (Extraído)",
        "enriquecimiento": enriquecimiento,
        "traduccion": traduccion,
        "resumen": "4. Resumen Ejecutivo (IA)",
    }
