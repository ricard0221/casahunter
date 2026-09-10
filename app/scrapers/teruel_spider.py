import cloudscraper
from bs4 import BeautifulSoup

def scrape_teruel():
    # URLs que abarcan Pisos, Casas, Chalets, Oportunidades a reformar y Chollos
    urls = [
        # Teruel y Comarca Gúdar-Javalambre (Casas, Pajares, Reformas y Pisos)
        "https://www.pisos.com/venta/pisos-mora_de_rubielos/",
        "https://www.pisos.com/venta/casas-mora_de_rubielos/",
        "https://www.pisos.com/venta/pisos-sarrion/",
        "https://www.pisos.com/venta/casas-sarrion/",
        "https://www.pisos.com/venta/pisos-rubielos_de_mora/",
        "https://www.pisos.com/venta/casas-rubielos_de_mora/",
        "https://www.pisos.com/venta/pisos-teruel/",
        "https://www.pisos.com/venta/casas-teruel/",
        
        # Comunidad Valenciana (Costa, Capitales y Oportunidades)
        "https://www.pisos.com/venta/viviendas-valencia/",
        "https://www.pisos.com/venta/viviendas-alicante/",
        "https://www.pisos.com/venta/viviendas-castellon/",
        "https://www.pisos.com/venta/viviendas-gandia/",
        "https://www.pisos.com/venta/viviendas-denia/"
    ]
    
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    pisos_encontrados = []
    
    for url in urls:
        try:
            res = scraper.get(url, timeout=8)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Localizar tarjetas de anuncios
                tarjetas = soup.find_all("div", class_="ad-preview") or soup.find_all("div", class_="grid-row") or soup.find_all("article")
                
                for t in tarjetas:
                    # Obtener enlace directo a la casa (/comprar/...)
                    link_elem = t.find("a", href=lambda h: h and "/comprar/" in h) or t.find("a", class_="title") or t.find("a", class_="p-title")
                    precio_elem = t.find("div", class_="price") or t.find("span", class_="price") or t.find("p", class_="price")
                    
                    if link_elem and link_elem.get("href"):
                        href = link_elem.get("href", "").strip()
                        full_url = "https://www.pisos.com" + href if href.startswith("/") else href
                        
                        if "/comprar/" in full_url:
                            titulo_texto = link_elem.text.strip() or "Inmueble en venta"
                            precio_texto = precio_elem.text.strip() if precio_elem else "Consultar"
                            
                            # Etiquetar según el tipo de inmueble para identificar fácil
                            lower_title = titulo_texto.lower()
                            if "reformar" in lower_title or "ruina" in lower_title or "pajar" in lower_title or "proyecto" in lower_title:
                                icono = "🛠️"
                            elif "casa" in lower_title or "chalet" in lower_title or "finca" in lower_title or "masía" in lower_title:
                                icono = "🏡"
                            elif "ático" in lower_title or "duplex" in lower_title or "estudio" in lower_title:
                                icono = "🏢"
                            else:
                                icono = "🏠"

                            # Evitar duplicados
                            if not any(p["enlace"] == full_url for p in pisos_encontrados):
                                pisos_encontrados.append({
                                    "titulo": f"{icono} {titulo_texto}",
                                    "precio": precio_texto,
                                    "enlace": full_url
                                })
        except Exception as e:
            print(f"Aviso escaneando {url}: {e}")

    # Enlaces oficiales a Subastas Públicas del BOE
    subastas_boe = [
        {"titulo": "⚖️ [SUBASTA BOE] Oportunidades y lotes en Teruel", "precio": "Ver subastas activas", "enlace": "https://subastas.boe.es/subastas_ava.php?accion=Busqueda&id_prov=44"},
        {"titulo": "⚖️ [SUBASTA BOE] Oportunidades y lotes en Valencia", "precio": "Ver subastas activas", "enlace": "https://subastas.boe.es/subastas_ava.php?accion=Busqueda&id_prov=46"},
        {"titulo": "⚖️ [SUBASTA BOE] Oportunidades y lotes en Alicante", "precio": "Ver subastas activas", "enlace": "https://subastas.boe.es/subastas_ava.php?accion=Busqueda&id_prov=3"}
    ]

    if not pisos_encontrados:
        pisos_encontrados.append({
            "titulo": "⚠️ Servidor temporalmente en espera",
            "precio": "Reintentar en unos segundos",
            "enlace": "https://www.pisos.com/venta/pisos-mora_de_rubielos/"
        })

    pisos_encontrados.extend(subastas_boe)
    return pisos_encontrados

class TeruelSmartScraper:
    def run(self):
        return scrape_teruel()
        
    @staticmethod
    def scrape():
        return scrape_teruel()
