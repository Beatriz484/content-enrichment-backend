"""Extracción de contenido desde Wikipedia.

Estrategia: primero se intenta acceder directamente al artículo construyendo
la URL con el tema indicado. Si Wikipedia responde 404 (el tema no coincide con
el título real), se recurre a la búsqueda de la API como respaldo para localizar
el artículo más relevante.
"""
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

SEARCH_API_URL = "https://es.wikipedia.org/w/api.php"
MAX_PARAGRAPHS = 5
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


class WikipediaScraper:
    """
    Clase responsable exclusivamente de realizar el web scraping en Wikipedia.
    Cumple con el principio de responsabilidad única (SRP).
    """

    def __init__(self, topic: str):
        if not topic or not topic.strip():
            raise ValueError("El tema de búsqueda no puede estar vacío.")
        self.topic = topic.strip()
        self.base_url = "https://es.wikipedia.org/wiki/"

    def _build_url(self, title: Optional[str] = None) -> str:
        """Construye la URL del artículo a partir del tema o de un título alternativo."""
        reference = title if title else self.topic
        return self.base_url + reference.replace(" ", "_")

    def _get_response(self, url: str, params: Optional[dict] = None) -> Optional[requests.Response]:
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

    def _search_title(self) -> Optional[str]:
        """Busca en Wikipedia el artículo más relevante para el tema (respaldo del 404)."""
        params = {
            "action": "query",
            "list": "search",
            "srsearch": self.topic,
            "format": "json",
            "utf8": "1",
        }
        try:
            response = requests.get(SEARCH_API_URL, headers=HEADERS, timeout=10, params=params)
            response.raise_for_status()
            results = response.json().get("query", {}).get("search", [])
        except (requests.exceptions.RequestException, ValueError) as error:
            raise ConnectionError(f"Error de conexión al buscar en Wikipedia: {error}")

        if not results:
            return None
        return results[0].get("title")

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> Optional[str]:
        title_tag = soup.find(id="firstHeading")
        return title_tag.text.strip() if title_tag else None

    @staticmethod
    def _clean_text(text: str) -> str:
        """Normaliza el párrafo extraído.

        Wikipedia inserta espacios duros (``\\xa0``) y espacios repetidos que
        después se ven corruptos en el TXT/PDF, así que se normalizan en origen.
        """
        return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()

    @staticmethod
    def _extract_paragraphs(soup: BeautifulSoup) -> list:
        """Devuelve los primeros ``MAX_PARAGRAPHS`` párrafos con contenido del artículo."""
        content_div = soup.find(id="mw-content-text")
        paragraphs_html = content_div.find_all("p", recursive=True) if content_div else []

        paragraphs = []
        for paragraph in paragraphs_html:
            text = WikipediaScraper._clean_text(paragraph.get_text())
            if text:
                paragraphs.append(text)
            if len(paragraphs) == MAX_PARAGRAPHS:
                break
        return paragraphs

    def extract_content(self) -> dict:
        """Extrae título y primeros párrafos del artículo.

        Returns:
            ``{"title": str, "paragraphs": list[str]}``

        Raises:
            ValueError: Si el artículo no existe (tampoco en la búsqueda de respaldo).
            ConnectionError: Si falla la conexión con Wikipedia.
        """
        alternative_title = None
        response = self._get_response(self._build_url())

        # Respaldo: el tema no coincide con ningún artículo → se busca por texto
        if response is None:
            alternative_title = self._search_title()
            if not alternative_title:
                raise ValueError(f"El artículo de Wikipedia para '{self.topic}' no existe.")
            response = self._get_response(self._build_url(alternative_title))
            if response is None:
                raise ValueError(f"El artículo de Wikipedia para '{self.topic}' no existe.")

        soup = BeautifulSoup(response.text, "html.parser")
        title = self._extract_title(soup) or alternative_title or self.topic

        return {
            "title": title,
            "paragraphs": self._extract_paragraphs(soup),
        }
