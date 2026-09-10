import json
import logging
import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse

# Intentamos importar Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

logger = logging.getLogger(__name__)

class TeruelSmartScraper:
    def __init__(self, db=None):
        self.db = db
        # Ruta exacta al archivo json
        self.archivo = Path(__file__).resolve().parent / "anuncios.json"
        
        # Configuración de Groq
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.client = None
        if GROQ_AVAILABLE and self.groq_key:
            try:
                self.client = Groq(api_key=self.groq_key)
            except Exception as e:
                logger.error(f"Error inicializando Groq: {e}")

    def extraer_nuevos_datos(self):
        """Se conecta a internet, extrae los datos y los guarda en el JSON"""
        url = "https://www.pisos.com/venta/pisos-teruel/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            respuesta = requests.get(url, headers=headers, timeout=15)
            respuesta.raise_for_status()
            sopa = BeautifulSoup(respuesta.text, 'html.parser')
            
            anuncios_html = sopa.find_all('div', class_='ad-preview')
            casas_encontradas = []

            for anuncio in anuncios_html[:12]: # Limitamos a 12 para que sea rápido desde el móvil
                # Extraer título
                titulo_tag = anuncio.find('a', class_='ad-preview__title')
                titulo = titulo_tag.text.strip() if titulo_tag else "Piso en venta"
                
                # Extraer enlace
                if titulo_tag and 'href' in titulo_tag.attrs:
                    link = "https://www.pisos.com" + titulo_tag['href']
                else:
                    link = url
                
                # Extraer precio
                precio_tag = anuncio.find('span', class_='ad-preview__price')
                if precio_tag:
                    precio_str = precio_tag.text.replace('€', '').replace('.', '').strip()
                    precio = float(precio_str) if precio_str.isdigit() else None
                else:
                    precio = None
                
                casas_encontradas.append({
                    "title": titulo,
                    "source": "Pisos.com (Araña en Vivo)",
                    "listing_url": link,
                    "image_url": "https://images.unsplash.com/photo-1502672260266-1c1de2d96674?auto=format&fit=crop&w=800&q=80",
                    "municipality": "Teruel (Novedad)",
                    "price": precio,
                    "specs": "Recién extraído",
                    "description": "Anuncio actualizado desde la web en tiempo real al pulsar el botón."
                })

            if casas_encontradas:
                # Guardar en JSON
                with open(self.archivo, "w", encoding="utf-8") as f:
                    json.dump(casas_encontradas, f, indent=4, ensure_ascii=False)
                return True, f"¡Actualizado! Se encontraron {len(casas_encontradas)} pisos nuevos."
            else:
                return False, "No se encontraron pisos. Es posible que hayan cambiado la estructura de la web."
                
        except Exception as e:
            logger.error(f"Error extrayendo datos: {e}")
            return False, f"Error de conexión. PythonAnywhere podría estar bloqueando la salida: {e}"

    def _url_valida(self, url):
        if not isinstance(url, str): return False
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except: return False

    def _cargar_anuncios(self):
        if not self.archivo.exists(): return []
        try:
            with open(self.archivo, "r", encoding="utf-8") as file:
                datos = json.load(file)
            return datos if isinstance(datos, list) else []
        except: return []

    def _normalizar_anuncio(self, anuncio):
        if not isinstance(anuncio, dict): return None
        return {
            "title": str(anuncio.get("title", "Inmueble")).strip(),
            "source": str(anuncio.get("source", "")).strip(),
            "listing_url": anuncio.get("listing_url"),
            "image_url": anuncio.get("image_url"),
            "municipality": str(anuncio.get("municipality", "")).strip(),
            "price": anuncio.get("price"),
            "specs": str(anuncio.get("specs", "")).strip(),
            "description": str(anuncio.get("description", "")).strip(),
            "ai_insight": None
        }

    def generar_resumen_ia(self, casa):
        if not self.client: return None
        prompt = f"Analiza en 10 palabras el atractivo de este piso: {casa['title']} por {casa['price']}€ en {casa['municipality']}"
        try:
            res = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "user", "content": prompt}], 
                max_tokens=30, 
                temperature=0.3
            )
            return res.choices[0].message.content.strip().replace('"', '')
        except: return None

    def buscar_en_portales_reales(self, query_busqueda="todo"):
        anuncios = self._cargar_anuncios()
        resultados = []
        query = (query_busqueda or "todo").lower().strip()
        for anuncio in anuncios:
            res = self._normalizar_anuncio(anuncio)
            if not res: continue
            
            # Filtrar si hay búsqueda
            if query != "todo":
                texto = f"{res['title']} {res['municipality']} {res['description']}".lower()
                if query not in texto: continue
                
            if self.client: 
                res["ai_insight"] = self.generar_resumen_ia(res)
                
            resultados.append(res)
            
        resultados.sort(key=lambda x: (x["price"] is None, x["price"]))
        return resultados
