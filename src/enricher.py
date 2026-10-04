import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class AiContentEnricher:
    """Clase responsable de enriquecer y resumir contenido mediante OpenAI."""

    def __init__(self, api_key: str | None = None) -> None:
        """Inicializa el cliente de OpenAI validando la presencia de la API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "No se encontró la clave de API de OpenAI. "
                "Asegúrate de configurarla en el archivo .env o pasarla al constructor."
            )

        self.client = OpenAI(api_key=self.api_key)

    def _es_texto_valido(self, texto: str | None) -> bool:
        """Comprueba si el texto de entrada contiene información válida."""
        if not texto or not isinstance(texto, str):
            return False
        return bool(texto.strip())

    def _ajustar_longitud(self, texto: str, max_caracteres: int = 10000) -> str:
        """Recorta el texto a un tamaño seguro si supera el límite establecido."""
        if len(texto) > max_caracteres:
            return texto[:max_caracteres].strip()
        return texto

    def enriquecer_contenido(self, texto: str, modelo: str = "gpt-4o-mini") -> str:
        """Enriquece el contenido proporcionado utilizando la API de OpenAI."""
        if not self._es_texto_valido(texto):
            return texto

        texto_preparado = self._ajustar_longitud(texto)

        prompt_sistema = (
            "Eres un asistente educativo especializado en investigación y síntesis académica. "
            "Tu tarea es enriquecer el contenido proporcionado: amplía los conceptos clave, "
            "añade contexto histórico o técnico relevante y organiza la información con claridad, "
            "manteniendo un tono didáctico, riguroso y estructurado."
        )

        try:
            respuesta = self.client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": f"Contenido a enriquecer:\n\n{texto_preparado}"},
                ],
                temperature=0.7,
            )
            contenido_enriquecido = respuesta.choices[0].message.content
            return contenido_enriquecido.strip() if contenido_enriquecido else texto
        except Exception:
            return texto

    def resumir_contenido(self, texto: str, modelo: str = "gpt-4o-mini") -> str:
        """Genera un resumen estructurado del contenido proporcionado."""
        if not self._es_texto_valido(texto):
            return texto

        texto_preparado = self._ajustar_longitud(texto)

        prompt_sistema = (
            "Eres un asistente educativo especializado en síntesis de información. "
            "Tu tarea es generar un resumen conciso y estructurado del contenido proporcionado, "
            "destacando los puntos principales, definiciones clave y conclusiones esenciales."
        )

        try:
            respuesta = self.client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": f"Contenido a resumir:\n\n{texto_preparado}"},
                ],
                temperature=0.5,
            )
            resumen = respuesta.choices[0].message.content
            return resumen.strip() if resumen else texto
        except Exception:
            return texto
