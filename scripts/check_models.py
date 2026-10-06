"""Diagnóstico de la conexión con la API de IA.

Uso (tras crear el ``.env``):

    python scripts/check_models.py

Comprueba tres cosas que son las que fallan cuando "el enriquecimiento no se
produce": que exista la API key, que la URL base sea la correcta y que el
modelo configurado en ``AI_MODEL`` esté disponible en la cuenta.
"""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
MODELO = os.getenv("AI_MODEL", "qwen/qwen3.8-27b")


def main() -> int:
    print("=" * 56)
    print("     DIAGNÓSTICO · API DE INTELIGENCIA ARTIFICIAL")
    print("=" * 56)
    print(f"OPENAI_API_KEY : {'configurada' if API_KEY else 'FALTA (archivo .env)'}")
    print(f"OPENAI_BASE_URL: {BASE_URL or '(por defecto de OpenAI)'}")
    print(f"AI_MODEL        : {MODELO}")

    if not API_KEY:
        print("\nSin API key no puede haber enriquecimiento ni resumen.")
        print("Copia .env.example a .env y rellena OPENAI_API_KEY.")
        return 1

    cliente = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    try:
        modelos = cliente.models.list()
    except Exception as error:  # noqa: BLE001 - el objetivo es mostrar el error tal cual
        print(f"\nNo se pudo contactar con la API: {error}")
        return 1

    print(f"\nModelos disponibles ({len(modelos.data)}):")
    for modelo in modelos.data:
        marcador = "  <-- AI_MODEL" if modelo.id == MODELO else ""
        print(f" - {modelo.id}{marcador}")

    if not any(modelo.id == MODELO for modelo in modelos.data):
        print(f"\n¡Atención! AI_MODEL='{MODELO}' no está en la lista de arriba.")
        print("El enriquecimiento fallará: cambia AI_MODEL en el archivo .env.")
        return 1

    print("\nConfiguración correcta: la IA puede enriquecer y resumir.")
    return 0


if __name__ == "__main__":  # pragma: no cover - script de diagnóstico manual
    raise SystemExit(main())
