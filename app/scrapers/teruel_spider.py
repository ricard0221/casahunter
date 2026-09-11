import cloudscraper
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Añadimos las URLs de EMBARGOS DE BANCOS junto con las normales
URLS = [
    # 🏦 EMBARGOS Y PISOS DE BANCOS
    "https://www.pisos.com/venta/pisos-bancos-teruel/",
    "https://www.pisos.com/venta/pisos-bancos-valencia/",
    "https://www.pisos.com/venta/pisos-bancos-alicante/",
    "https://www.pisos.com/venta/pisos-bancos-castellon/",

    # Provincia de Teruel (Casas, Pisos, Oportunidades, Reformas)
    "https://www.pisos.com/venta/pisos-mora_de_rubielos/",
    "https://www.pisos.com/venta/casas-mora_de_rubielos/",
    "https://www.pisos.com/venta/pisos-sarrion/",
    "https://www.pisos.com/venta/casas-sarrion/",
    "https://www.pisos.com/venta/pisos-teruel/",
    
    # Costa y Provincia de la Comunidad Valenciana
    "https://www.pisos.com/venta/viviendas-valencia/",
    "https://www.pisos.com/venta/viviendas-alicante/",
    "https://www.pisos.com/venta/viviendas-gandia/",
    "https://www.pisos.com/venta/viviendas-denia/"
]

def fetch_url(url, scraper):
    results = []
    try:
        res = scraper.get(url, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            tarjetas = soup.find_all("div", class_="ad-preview") or soup.find_all("div", class_="grid-row") or soup.find_all("article")
            
            for t in tarjetas[:4]:
                link_elem = t.find("a", href=lambda h: h and "/comprar/" in h)
                precio_elem = t.find("div", class_="price") or t.find("span", class_="price") or t.find("p", class_="price")
                
                # Extraer la IMAGEN de la casa para mostrarla en tu app
                img_elem = t.find("img")
                imagen_url = ""
                if img_elem:
                    # Pisos.com suele usar data-src para cargar las imágenes (lazy loading)
                    imagen_url = img_elem.get("data-src") or img_elem.get("src") or ""
                
                if link_elem:
                    href = link_elem.get("href", "").strip()
                    full_url = "https://www.pisos.com" + href if href.startswith("/") else href
                    
                    if "/comprar/" in full_url:
                        titulo_texto = link_elem.text.strip() or "Vivienda en venta"
                        precio_texto = precio_elem.text.strip() if precio_elem else "Consultar"
                        
                        lower_title = titulo_texto.lower()
                        # Si viene de la URL de bancos, le ponemos el icono de embargo
                        if "bancos" in url:
                            icono = "🏦 [EMBARGO/BANCO]"
                        elif any(k in lower_title for k in ["reformar", "ruina", "pajar"]):
                            icono = "🛠️ [REFORMA]"
                        elif any(k in lower_title for k in ["casa", "chalet", "finca"]):
                            icono = "🏡 [CASA]"
                        else:
                            icono = "🏠 [PISO]"

                        results.append({
                            "titulo": f"{icono} {titulo_texto}",
                            "precio": precio_texto,
                            "enlace": full_url,
                            "imagen": imagen_url  # Pasamos la imagen a la web
                        })
    except Exception as e:
        print(f"Error extrayendo {url}: {e}")
    return results

def scrape_teruel():
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    pisos_encontrados = []
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(fetch_url, url, scraper) for url in URLS]
        for future in as_completed(futures):
            try:
                data = future.result()
                if data:
                    for item in data:
                        if not any(x["enlace"] == item["enlace"] for x in pisos_encontrados):
                            pisos_encontrados.append(item)
            except Exception as e:
                pass

    subastas_boe = [
        {"titulo": "⚖️ [SUBASTAS JUDICIALES] Ver pujas oficiales en Teruel y C.Valenciana", "precio": "Consultar Expedientes", "enlace": "https://subastas.boe.es/index.php?c=1", "imagen": "https://s03.s3c.es/imag/_v0/770x420/5/2/2/boe-logo-770.jpg"}
    ]

    pisos_encontrados.extend(subastas_boe)
    return pisos_encontrados

class TeruelSmartScraper:
    def run(self): return scrape_teruel()
    @staticmethod
    def scrape(): return scrape_teruel()
