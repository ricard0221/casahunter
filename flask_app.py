from flask import Flask, render_template, request
from app.scrapers.teruel_spider import TeruelSmartScraper
import cloudscraper
from bs4 import BeautifulSoup
import re
import json

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    pisos = []
    if request.method == "POST":
        scraper = TeruelSmartScraper()
        pisos = scraper.run()
    return render_template("index.html", pisos=pisos)

@app.route("/detalle")
def detalle():
    enlace = request.args.get("url")
    if not enlace:
        return "Error: No se encontró la URL de la propiedad.", 400
        
    try:
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
        res = scraper.get(enlace, timeout=8)
        soup = BeautifulSoup(res.text, "html.parser")
        
        titulo = soup.find("h1").text.strip() if soup.find("h1") else "Detalles del Inmueble"
        precio_elem = soup.find(class_="price") or soup.find(class_="h1-price")
        precio = precio_elem.text.strip() if precio_elem else "Consultar"
        
        desc_elem = soup.find("div", class_="description") or soup.find("div", id="description")
        descripcion_texto = desc_elem.text.strip() if desc_elem else ""
        
        telefonos = []

        # 1. Búsqueda directa en la ficha técnica de la inmobiliaria/agente (JSON-LD)
        for script in soup.find_all("script", type="application/ld+json"):
            if script.string and "telephone" in script.string:
                try:
                    data = json.loads(script.string)
                    # Extraer teléfono si está registrado en los metadatos
                    if isinstance(data, dict):
                        tel_raw = data.get("telephone") or data.get("offers", {}).get("offeredBy", {}).get("telephone")
                        if tel_raw:
                            num = re.sub(r'\D', '', str(tel_raw))
                            if len(num) >= 9 and num[-9:] not in telefonos:
                                telefonos.append(num[-9:])
                except Exception:
                    pass

        # 2. Si no está en la ficha técnica, buscar SOLO en el texto redactado de la descripción
        if not telefonos and descripcion_texto:
            patron_telefono = r'(?:(?:\+|00)34\s?)?(?:[679]\d{2}[\s.-]?\d{3}[\s.-]?\d{3})'
            coincidencias = re.findall(patron_telefono, descripcion_texto)
            for t in coincidencias:
                num_limpio = re.sub(r'\D', '', t)
                if len(num_limpio) == 9 and num_limpio not in telefonos:
                    telefonos.append(num_limpio)

        # Limitar a máximo 1 o 2 números reales para no saturar la pantalla
        telefonos = telefonos[:2]

        # Extraer imágenes del inmueble
        imagenes = []
        for img in soup.find_all("img"):
            src = img.get("data-src") or img.get("src")
            if src and "http" in src and "logo" not in src.lower() and "icon" not in src.lower():
                if src not in imagenes:
                    imagenes.append(src)
                    
        return render_template(
            "detalle.html", 
            titulo=titulo, 
            precio=precio, 
            descripcion=descripcion_texto if descripcion_texto else "Descripción disponible en el portal oficial.", 
            imagenes=imagenes[:15], 
            telefonos=telefonos,
            enlace_original=enlace
        )
    except Exception as e:
        return f"Error al cargar la propiedad: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
