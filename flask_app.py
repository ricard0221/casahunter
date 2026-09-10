import os
from flask import Flask, render_template_string, redirect, url_for
from groq import Groq
from app.scrapers.teruel_spider import scrape_teruel

app = Flask(__name__)

# Caché en memoria para almacenar los inmuebles
RESULTADOS_CACHE = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>House Hunter - Teruel & C. Valenciana</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f4f6f9; color: #333; }
        h1 { color: #1e3a8a; text-align: center; }
        .btn { display: block; width: 100%; max-width: 320px; margin: 20px auto; padding: 14px 20px; background-color: #10b981; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; text-align: center; text-decoration: none; }
        .btn:hover { background-color: #059669; }
        .card { background: white; padding: 18px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); }
        .card h3 { margin-top: 0; color: #1f2937; }
        .card a { color: #2563eb; text-decoration: none; font-weight: bold; }
        .card a:hover { text-decoration: underline; }
        .ai-box { background-color: #f0fdf4; border-left: 4px solid #10b981; padding: 10px 14px; margin: 10px 0; font-size: 14px; border-radius: 0 4px 4px 0; }
    </style>
</head>
<body>
    <h1>🏠 CasaHunter (Teruel & C. Valenciana)</h1>
    <a href="/extraer" class="btn">🔄 Extraer Pisos Nuevos Ahora</a>

    {% if resultados %}
        <h2>Inmuebles Encontrados ({{ resultados|length }}):</h2>
        {% for piso in resultados %}
            <div class="card">
                <h3>{{ piso.titulo }}</h3>
                <p><strong>Precio:</strong> {{ piso.precio }}</p>
                {% if piso.analisis_ai %}
                    <div class="ai-box">
                        <strong>💡 Análisis Groq IA:</strong> {{ piso.analisis_ai }}
                    </div>
                {% endif %}
                <a href="{{ piso.enlace }}" target="_blank">Ver anuncio en Pisos.com ➔</a>
            </div>
        {% endfor %}
    {% else %}
        <p style="text-align: center; color: #6b7280; margin-top: 40px;">No hay datos cargados. Haz clic en el botón verde para buscar ofertas en vivo.</p>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, resultados=RESULTADOS_CACHE)

@app.route("/extraer")
def extraer():
    global RESULTADOS_CACHE
    pisos = scrape_teruel()
    
    # Procesar con la Inteligencia Artificial de Groq si la API Key está configurada
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key and pisos:
        try:
            client = Groq(api_key=groq_key)
            for piso in pisos[:6]:  # Analizamos los primeros 6 para una respuesta rápida
                prompt = f"Proporciona un resumen muy breve en una frase sobre por qué puede ser interesante este inmueble: {piso['titulo']} con un precio de {piso['precio']}"
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    max_tokens=80
                )
                piso["analisis_ai"] = response.choices[0].message.content
        except Exception as e:
            print(f"Error procesando con Groq AI: {e}")

    RESULTADOS_CACHE = pisos
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
