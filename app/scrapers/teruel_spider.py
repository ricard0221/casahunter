import requests
from bs4 import BeautifulSoup

def scrape_teruel():
    # Lista de zonas: Teruel + Comunidad Valenciana (Valencia, Alicante, Castellón)
    urls = [
        "https://www.pisos.com/venta/pisos-teruel/",
        "https://www.pisos.com/venta/pisos-valencia/",
        "https://www.pisos.com/venta/pisos-alicante/",
        "https://www.pisos.com/venta/pisos-castellon/"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    pisos_encontrados = []

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                # Busca las tarjetas de anuncios
                tarjetas = soup.find_all("div", class_="ad-preview")

                # Extrae los primeros 5 de cada provincia para mantener la app rápida
                for tarjeta in tarjetas[:5]:
                    titulo_elem = tarjeta.find("a", class_="title")
                    precio_elem = tarjeta.find("div", class_="price")

                    if titulo_elem:
                        titulo = titulo_elem.text.strip()
                        href = titulo_elem.get("href", "")
                        enlace = "https://www.pisos.com" + href if href.startswith("/") else href
                        precio = precio_elem.text.strip() if precio_elem else "Consultar"

                        pisos_encontrados.append({
                            "titulo": titulo,
                            "precio": precio,
                            "enlace": enlace
                        })
        except Exception as e:
            print(f"Error extrayendo de {url}: {e}")

    return pisos_encontrados
