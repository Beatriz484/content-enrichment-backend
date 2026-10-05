import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

print(f"Probando conexion con base_url: {base_url}")

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)

try:
    models = client.models.list()
    print("\n✓ Modelos disponibles en tu cuenta:")
    for m in models.data:
        print(f" - {m.id}")
except Exception as e:
    print(f"\n✕ Error al conectar o consultar modelos: {e}")