import requests
from bs4 import BeautifulSoup


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

    def _construir_url(self) -> str:
        return self.base_url + self.tema.replace(" ", "_")

    def extraer_contenido(self) -> dict:
        # 1. Definimos la URL llamando al método interno
        url = self._construir_url()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 404:
                raise ValueError(f"El artículo de Wikipedia para '{self.tema}' no existe.")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error de conexión al acceder a Wikipedia: {e}")

        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. Extraer el título
        titulo_tag = soup.find(id="firstHeading")
        titulo = titulo_tag.text.strip() if titulo_tag else self.tema

        # 3. Extraer los primeros 5 párrafos
        content_div = soup.find(id="mw-content-text")
        parrafos_html = content_div.find_all('p', recursive=True) if content_div else []

        parrafos = []
        for p in parrafos_html:
            texto = p.get_text().strip()
            if texto:
                parrafos.append(texto)
            if len(parrafos) == 5:  # ¡Aquí limitamos exactamente a 5 párrafos!
                break

        # 4. Devolver el diccionario con el resultado final
        return {
            "titulo": titulo,
            "parrafos": parrafos
        }
