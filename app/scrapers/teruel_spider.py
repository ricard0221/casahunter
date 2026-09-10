import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Zonas objetivo: Provincia de Teruel (Mora de Rubielos, Sarrión...) + Costa C. Valenciana
URLS = [
    "https://www.pisos.com/venta/pisos-teruel/",
    "https://www.pisos.com/venta/pisos-valencia/",
    "https://www.pisos.com/venta/pisos-alicante/",
    "https://www.pisos.com/venta/pisos-castellon/"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def fetch_zone(url):
    results = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=4)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            tarjetas = soup.find_all("div", class_="ad-preview") or soup.find_all("div", class_="row")
            
            for tarjeta in tarjetas[:4]:
                titulo_elem = tarjeta.find("a", class_="title") or tarjeta.find("a", class_="p-title")
                precio_elem = tarjeta.find("div", class_="price") or tarjeta.find("span", class_="price")
                ubicacion_elem = tarjeta.find("div", class_="location") or tarjeta.find("p", class_="location")

                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    href = titulo_elem.get("href", "")
                    enlace = "https://www.pisos.com" + href if href.startswith("/") else href
                    precio = precio_elem.text.strip() if precio_elem else "Consultar"
                    ubicacion = ubicacion_elem.text.strip() if ubicacion_elem else ""

                    results.append({
                        "titulo": f"{titulo} ({ubicacion})" if ubicacion else titulo,
                        "precio": precio,
                        "enlace": enlace
                    })
    except Exception as e:
        print(f"Error extrayendo de {url}: {e}")
    return results

def scrape_teruel():
    pisos_encontrados = []
    # Extracción simultánea multihilo (Modo Ultra Rápido)
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(fetch_zone, url): url for url in URLS}
        for future in as_completed(future_to_url):
            try:
                data = future.result()
                if data:
                    pisos_encontrados.extend(data)
            except Exception as e:
                print(f"Error procesando hilo: {e}")
                
    return pisos_encontrados

# Clase de compatibilidad absoluta
class TeruelSmartScraper:
    def __init__(self):
        pass
    def run(self):
        return scrape_teruel()
    @staticmethod
    def scrape():
        return scrape_teruel()
