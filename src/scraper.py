"""Extracción de contenido desde Wikipedia.

Estrategia: primero se intenta acceder directamente al artículo construyendo
la URL con el tema indicado. Si Wikipedia responde 404 (el tema no coincide con
el título real), se recurre a la búsqueda de la API como respaldo para localizar
el artículo más relevante.
"""
from typing import Optional

import requests
from bs4 import BeautifulSoup

API_BUSQUEDA = "https://es.wikipedia.org/w/api.php"
MAX_PARRAFOS = 5
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


class WikipediaScraper:
    """
    Clase responsable exclusivamente de realizar el web scraping en Wikipedia.
    Cumple con el principio de responsabilidad única (SRP).
    """

    def __init__(self, tema: str):
        if not tema or not tema.strip():
            raise ValueError("El tema de búsqueda no puede estar vacío.")
        self.tema = tema.strip()
        self.base_url = "https://es.wikipedia.org/wiki/"

    def _construir_url(self, titulo: Optional[str] = None) -> str:
        """Construye la URL del artículo a partir del tema o de un título alternativo."""
        referencia = titulo if titulo else self.tema
        return self.base_url + referencia.replace(" ", "_")

    def _obtener_respuesta(self, url: str, params: Optional[dict] = None) -> Optional[requests.Response]:
        """Realiza la petición y devuelve la respuesta, o ``None`` si es un 404.

        Raises:
            ConnectionError: Si la petición falla por red o por otro estado HTTP.
        """
        try:
            response = requests.get(url, headers=HEADERS, timeout=10, params=params)
        except requests.exceptions.RequestException as error:
            raise ConnectionError(f"Error de conexión al acceder a Wikipedia: {error}")

        if response.status_code == 404:
            return None

        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise ConnectionError(f"Error de conexión al acceder a Wikipedia: {error}")

        return response

    def _buscar_titulo(self) -> Optional[str]:
        """Busca en Wikipedia el artículo más relevante para el tema (respaldo del 404)."""
        params = {
            "action": "query",
            "list": "search",
            "srsearch": self.tema,
            "format": "json",
            "utf8": "1",
        }
        try:
            response = requests.get(API_BUSQUEDA, headers=HEADERS, timeout=10, params=params)
            response.raise_for_status()
            resultados = response.json().get("query", {}).get("search", [])
        except (requests.exceptions.RequestException, ValueError) as error:
            raise ConnectionError(f"Error de conexión al buscar en Wikipedia: {error}")

        if not resultados:
            return None
        return resultados[0].get("title")

    @staticmethod
    def _extraer_titulo(soup: BeautifulSoup) -> Optional[str]:
        titulo_tag = soup.find(id="firstHeading")
        return titulo_tag.text.strip() if titulo_tag else None

    @staticmethod
    def _extraer_parrafos(soup: BeautifulSoup) -> list:
        """Devuelve los primeros ``MAX_PARRAFOS`` párrafos con contenido del artículo."""
        content_div = soup.find(id="mw-content-text")
        parrafos_html = content_div.find_all("p", recursive=True) if content_div else []

        parrafos = []
        for paragraph in parrafos_html:
            texto = paragraph.get_text().strip()
            if texto:
                parrafos.append(texto)
            if len(parrafos) == MAX_PARRAFOS:
                break
        return parrafos

    def extraer_contenido(self) -> dict:
        """Extrae título y primeros párrafos del artículo.

        Returns:
            ``{"titulo": str, "parrafos": list[str]}``

        Raises:
            ValueError: Si el artículo no existe (tampoco en la búsqueda de respaldo).
            ConnectionError: Si falla la conexión con Wikipedia.
        """
        titulo_alternativo = None
        response = self._obtener_respuesta(self._construir_url())

        # Respaldo: el tema no coincide con ningún artículo → se busca por texto
        if response is None:
            titulo_alternativo = self._buscar_titulo()
            if not titulo_alternativo:
                raise ValueError(f"El artículo de Wikipedia para '{self.tema}' no existe.")
            response = self._obtener_respuesta(self._construir_url(titulo_alternativo))
            if response is None:
                raise ValueError(f"El artículo de Wikipedia para '{self.tema}' no existe.")

        soup = BeautifulSoup(response.text, "html.parser")
        titulo = self._extraer_titulo(soup) or titulo_alternativo or self.tema

        return {
            "titulo": titulo,
            "parrafos": self._extraer_parrafos(soup),
        }
