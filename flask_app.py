import logging
from flask import Flask, render_template_string, request, redirect, url_for
from app.scrapers.teruel_spider import TeruelSmartScraper

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CasaHunter IA</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0; padding: 15px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f4f6f9; color: #202124;
        }
        .container { max-width: 850px; margin: auto; }
        .header {
            background: linear-gradient(135deg, #1e3c72, #2a5298); color: white;
            padding: 28px 20px; border-radius: 18px; text-align: center; margin-bottom: 18px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        }
        .header h1 { margin: 0; font-size: 30px; }
        .header p { margin: 8px 0 0; opacity: 0.9; }
        
        .search { background: white; padding: 15px; border-radius: 14px; margin-bottom: 18px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06); }
        .search form { display: flex; gap: 10px; }
        .search input { flex: 1; padding: 13px; border: 1px solid #ddd; border-radius: 9px; font-size: 15px; outline: none; }
        .search button { border: none; padding: 13px 18px; border-radius: 9px; background: #1e3c72; color: white; font-weight: bold; cursor: pointer; }
        
        .btn-actualizar {
            display: block; background: #16803c; color: white; text-align: center; 
            padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; 
            margin-bottom: 18px; box-shadow: 0 4px 10px rgba(22, 128, 60, 0.2);
        }
        .btn-actualizar:hover { background: #126b32; }

        .filters { background: white; padding: 12px; border-radius: 14px; margin-bottom: 18px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06); }
        .tag { display: inline-block; padding: 8px 11px; margin: 3px; border-radius: 20px; background: #eef2f7; font-size: 13px; text-decoration: none; color: #1e3c72; }
        .count { color: #666; font-size: 14px; margin-bottom: 12px; }
        
        .card { background: white; border-radius: 16px; overflow: hidden; margin-bottom: 18px; box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08); }
        .image { width: 100%; height: 250px; object-fit: cover; display: block; background: #e9edf2; }
        .no-image { height: 180px; display: flex; align-items: center; justify-content: center; background: #e9edf2; color: #687080; text-align: center; padding: 20px; }
        
        .content { padding: 20px; }
        .source { display: inline-block; background: #e8f1ff; color: #1e3c72; padding: 6px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-bottom: 10px; }
        .ai-badge { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
        .title { font-size: 20px; font-weight: bold; margin-bottom: 8px; }
        .location { color: #666; margin-bottom: 10px; }
        .price { color: #16803c; font-size: 23px; font-weight: bold; margin: 10px 0; }
        .specs { background: #f5f7fa; padding: 10px; border-radius: 8px; margin: 12px 0; font-size: 14px; }
        .description { color: #555; line-height: 1.5; margin-bottom: 16px; }
        
        .button { display: block; width: 100%; padding: 15px; background: #1e3c72; color: white; text-align: center; text-decoration: none; border-radius: 10px; font-weight: bold; transition: background 0.2s; }
        .button:hover { background: #2a5298; }
        .empty { background: white; padding: 30px 20px; text-align: center; border-radius: 15px; color: #666; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05); }
        
        @media (max-width: 600px) {
            .search form { flex-direction: column; }
            .search button { width: 100%; }
            .header h1 { font-size: 25px; }
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>🏠 CasaHunter IA</h1>
        <p>Buscador de Chollos Inmobiliarios potenciado por Groq AI</p>
    </div>

    <div class="search">
        <form method="GET" action="/">
            <input type="text" name="q" placeholder="Buscar Teruel, Mora, chollo, playa..." value="{{ query if query != 'todo' else '' }}">
            <button type="submit">🔎 Buscar</button>
        </form>
    </div>

    <!-- EL BOTÓN MÁGICO PARA EL MÓVIL -->
    <a href="/actualizar" class="btn-actualizar">🔄 Extraer Pisos Nuevos Ahora</a>

    <div class="filters">
        <a href="/?q=todo" class="tag">📍 Ver Todo</a>
        <a href="/?q=teruel" class="tag">📍 Teruel</a>
        <a href="/?q=castellon" class="tag">🌊 Castellón</a>
        <a href="/?q=chollo" class="tag">💰 Chollos</a>
        <a href="/?q=reforma" class="tag">🏚️ Reformas</a>
    </div>

    {% if propiedades %}
        <div class="count">
            {{ propiedades|length }} oportunidad(es) encontrada(s)
        </div>

        {% for casa in propiedades %}
        <div class="card">
            {% if casa.image_url %}
                <img src="{{ casa.image_url }}" alt="Imagen del inmueble" class="image" loading="lazy">
            {% else %}
                <div class="no-image">🏠<br>Fotos en el anuncio original</div>
            {% endif %}

            <div class="content">
                <div class="source">{{ casa.source }}</div>

                {% if casa.ai_insight %}
                    <div class="ai-badge">🤖 <strong>Groq:</strong> {{ casa.ai_insight }}</div>
                {% endif %}

                <div class="title">{{ casa.title }}</div>
                <div class="location">📍 {{ casa.municipality }}</div>

                {% if casa.price is not none %}
                    <div class="price">{{ "{:,.0f}".format(casa.price).replace(",", ".") }} €</div>
                {% endif %}

                {% if casa.specs %}
                    <div class="specs">{{ casa.specs }}</div>
                {% endif %}

                {% if casa.description %}
                    <div class="description">{{ casa.description }}</div>
                {% endif %}

                <a href="{{ casa.listing_url }}" target="_blank" rel="noopener noreferrer" class="button">
                    🔗 VER ANUNCIO REAL
                </a>
            </div>
        </div>
        {% endfor %}
    {% else %}
        <div class="empty">
            <h2>🔎 Sin oportunidades</h2>
            <p>No se encontraron resultados o la base de datos está vacía. ¡Pulsa el botón verde para buscar nuevos pisos!</p>
        </div>
    {% endif %}
</div>

</body>
</html>
"""

@app.route("/")
def home():
    query = request.args.get("q", "todo").strip()
    try:
        spider = TeruelSmartScraper()
        propiedades = spider.buscar_en_portales_reales(query)
    except Exception as e:
        logger.exception(f"Error ejecutando CasaHunter IA: {e}")
        propiedades = []

    return render_template_string(
        HTML_TEMPLATE,
        propiedades=propiedades,
        query=query
    )

# NUEVA RUTA PARA ACTUALIZAR DESDE EL MÓVIL
@app.route("/actualizar")
def actualizar():
    try:
        spider = TeruelSmartScraper()
        exito, mensaje = spider.extraer_nuevos_datos()
        
        color_fondo = "#d1fae5" if exito else "#fee2e2"
        color_texto = "#065f46" if exito else "#991b1b"
        
        return f"""
        <!DOCTYPE html>
        <html>
            <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
            <body style="font-family:sans-serif; text-align:center; padding:50px; background-color:#f4f6f9;">
                <div style="background:{color_fondo}; color:{color_texto}; padding:30px; border-radius:15px; max-width:400px; margin:auto;">
                    <h2>{'✅ Éxito' if exito else '❌ Aviso'}</h2>
                    <p style="font-size:18px;">{mensaje}</p>
                    <br><br>
                    <a href="/" style="display:inline-block; padding:15px 30px; background:#1e3c72; color:white; text-decoration:none; border-radius:10px; font-weight:bold;">Volver a la App</a>
                </div>
            </body>
        </html>
        """
    except Exception as e:
        return f"Error crítico durante la actualización: {e}"

if __name__ == "__main__":
    app.run(debug=True)
