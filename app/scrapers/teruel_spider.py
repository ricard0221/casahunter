import requests
from bs4 import BeautifulSoup
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
]

def scrape_teruel():
    # Zonas específicas solicitadas (Provincia de Teruel + Costa C. Valenciana)
    urls = [
        "https://www.pisos.com/venta/pisos-mora_de_rubielos/",
        "https://www.pisos.com/venta/pisos-sarrion/",
        "https://www.pisos.com/venta/pisos-teruel/",
        "https://www.pisos.com/venta/pisos-valencia/",
        "https://www.pisos.com/venta/pisos-alicante/",
        "https://www.pisos.com/venta/pisos-castellon/"
    ]
    
    pisos_encontrados = []
    
    for url in urls:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.google.com/"
        }
        try:
            res = requests.get(url, headers=headers, timeout=4)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                tarjetas = soup.find_all("div", class_="ad-preview") or soup.find_all("div", class_="grid-row")
                
                for t in tarjetas[:3]:
                    titulo_elem = t.find("a", class_="title") or t.find("a", class_="p-title")
                    precio_elem = t.find("div", class_="price") or t.find("span", class_="price")
                    
                    if titulo_elem:
                        href = titulo_elem.get("href", "")
                        if href and not href.startswith("http"):
                            link_directo = "https://www.pisos.com" + href
                        else:
                            link_directo = href
                            
                        pisos_encontrados.append({
                            "titulo": f"🏠 {titulo_elem.text.strip()}",
                            "precio": precio_elem.text.strip() if precio_elem else "Consultar",
                            "enlace": link_directo
                        })
        except Exception as e:
            print(f"Error procesando {url}: {e}")

    # Enlaces oficiales del BOE para subastas
    subastas_boe = [
        {"titulo": "⚖️ [SUBASTA BOE] Subastas activas en la provincia de Teruel", "precio": "Ver portal BOE", "enlace": "https://subastas.boe.es/subastas_ava.php?accion=Busqueda&id_prov=44"},
        {"titulo": "⚖️ [SUBASTA BOE] Subastas activas en la provincia de Valencia", "precio": "Ver portal BOE", "enlace": "https://subastas.boe.es/subastas_ava.php?accion=Busqueda&id_prov=46"},
        {"titulo": "⚖️ [SUBASTA BOE] Subastas activas en la provincia de Alicante", "precio": "Ver portal BOE", "enlace": "https://subastas.boe.es/subastas_ava.php?accion=Busqueda&id_prov=3"}
    ]

    # Enlaces de respaldo 100% funcionales (usan la ruta correcta /venta/pisos-...)
    if len(pisos_encontrados) < 3:
        pisos_encontrados = [
            {"titulo": "🏠 Inmuebles en Mora de Rubielos (Teruel)", "precio": "Ver catálogo directo", "enlace": "https://www.pisos.com/venta/pisos-mora_de_rubielos/"},
            {"titulo": "🏠 Inmuebles en Sarrión (Teruel)", "precio": "Ver catálogo directo", "enlace": "https://www.pisos.com/venta/pisos-sarrion/"},
            {"titulo": "🏠 Apartamentos en Gandía Playa (Valencia)", "precio": "Ver catálogo directo", "enlace": "https://www.pisos.com/venta/pisos-gandia/"},
            {"titulo": "🏠 Pisos cerca del mar en Dénia (Alicante)", "precio": "Ver catálogo directo", "enlace": "https://www.pisos.com/venta/pisos-denia/"},
            {"titulo": "🏠 Casas y pisos en Peñíscola (Castellón)", "precio": "Ver catálogo directo", "enlace": "https://www.pisos.com/venta/pisos-peniscola/"}
        ]

    pisos_encontrados.extend(subastas_boe)
    return pisos_encontrados

class TeruelSmartScraper:
    def run(self): return scrape_teruel()
    @staticmethod
    def scrape(): return scrape_teruel()
