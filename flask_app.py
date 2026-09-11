from flask import Flask, render_template, request
from app.scrapers.teruel_spider import TeruelSmartScraper
import cloudscraper
from bs4 import BeautifulSoup

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
        descripcion = desc_elem.text.strip() if desc_elem else "Descripción detallada disponible en el anuncio oficial."
        
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
            descripcion=descripcion, 
            imagenes=imagenes[:15], 
            enlace_original=enlace
        )
    except Exception as e:
        return f"Error al cargar la propiedad: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
