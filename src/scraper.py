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

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 404:
                raise ValueError(f"El artículo de Wikipedia para '{self.tema}' no existe.")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error de conexión al acceder a Wikipedia: {e}")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraer el título
        titulo_tag = soup.find(id="firstHeading")
        titulo = titulo_tag.text.strip() if titulo_tag else self.tema
        content_div = soup.find(id="mw-content-text")
        parrafos_html = content_div.find_all('p', recursive=True) if content_div else []

        parrafos = []
        for p in parrafos_html:
            texto = p.get_text().strip()
            if texto:
                parrafos.append(texto)
            if len(parrafos) == 5:  # ¡Aquí limitamos exactamente a 5 párrafos!
                break
                return {
                    "titulo": titulo,
                    "parrafos": parrafos
                }

