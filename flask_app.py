from flask import Flask, render_template, request
from app.scrapers.teruel_spider import TeruelSmartScraper

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    pisos = []
    if request.method == "POST":
        # Ejecuta el scraper "Modo Dios" cuando se pulsa el botón
        scraper = TeruelSmartScraper()
        pisos = scraper.run()
        
    # Aquí es donde conecta tu código con el diseño que creamos en templates/index.html
    return render_template("index.html", pisos=pisos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
