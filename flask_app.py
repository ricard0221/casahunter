import os
from flask import Flask, render_template_string, redirect, url_for
from groq import Groq
from concurrent.futures import ThreadPoolExecutor
from app.scrapers.teruel_spider import scrape_teruel

app = Flask(__name__)

RESULTADOS_CACHE = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CasaHunter PRO - Teruel & Costa Valenciana</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #0f172a; color: #f8fafc; }
        h1 { color: #38bdf8; text-align: center; font-size: 26px; font-weight: 800; margin-bottom: 20px; }
        .btn { display: block; width: 100%; max-width: 340px; margin: 20px auto; padding: 16px 24px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; border-radius: 8px; font-size: 17px; font-weight: bold; cursor: pointer; text-align: center; text-decoration: none; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4); }
        .btn:active { transform: scale(0.98); }
        .card { background: #1e293b; padding: 20px; margin-bottom: 16px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }
        .card h3 { margin-top: 0; color: #f1f5f9; font-size: 18px; }
        .price { color: #34d399; font-size: 18px; font-weight: bold; margin: 8px 0; }
        .card a { display: inline-block; margin-top: 10px; color: #38bdf8; text-decoration: none; font-weight: 600; font-size: 14px; }
        .card a:hover { text-decoration: underline; }
        .ai-box { background-color: #064e3b; border-left: 4px solid #10b981; color: #a7f3d0; padding: 12px 16px; margin: 12px 0; font-size: 14px; border-radius: 0 8px 8px 0; line-height: 1.5; }
        .badge { display: inline-block; background-color: #334155; color: #cbd5e1; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 15px; }
    </style>
</head>
<body>
    <h1>⚡ CasaHunter PRO (Teruel & C. Valenciana)</h1>
    <a href="/extraer" class="btn">🚀 Extraer Pisos en Tiempo Real</a>

    {% if resultados %}
        <div style="text-align: center; margin-bottom: 15px;">
            <span class="badge">🔥 {{ resultados|length }} Ofertas Encontradas en Tiempo Real</span>
        </div>
        {% for piso in resultados %}
            <div class="card">
                <h3>{{ piso.titulo }}</h3>
                <div class="price">💰 {{ piso.precio }}</div>
                {% if piso.analisis_ai %}
                    <div class="ai-box">
                        <strong>🤖 Análisis Groq AI:</strong> {{ piso.analisis_ai }}
                    </div>
                {% endif %}
                <a href="{{ piso.enlace }}" target="_blank">Ver anuncio en Pisos.com ➔</a>
            </div>
        {% endfor %}
    {% else %}
        <p style="text-align: center; color: #94a3b8; margin-top: 50px; font-size: 16px;">
            No hay inmuebles cargados aún.<br>Haz clic en el botón verde para iniciar la búsqueda ultrarrápida.
        </p>
    {% endif %}
</body>
</html>
"""

def analizar_piso_con_ai(piso, client):
    try:
        prompt = f"Resume en 1 frase directa por qué destaca este inmueble: {piso['titulo']} por {piso['precio']}"
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=60
        )
        piso["analisis_ai"] = response.choices[0].message.content
    except Exception as e:
        print(f"Error en Groq AI: {e}")
    return piso

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, resultados=RESULTADOS_CACHE)

@app.route("/extraer")
def extraer():
    global RESULTADOS_CACHE
    pisos = scrape_teruel()
    
    # Procesamiento paralelo ultra-rápido de la IA
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key and pisos:
        try:
            client = Groq(api_key=groq_key)
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(analizar_piso_con_ai, p, client) for p in pisos[:5]]
                for future in futures:
                    future.result()
        except Exception as e:
            print(f"Error en Groq AI: {e}")

    RESULTADOS_CACHE = pisos
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
