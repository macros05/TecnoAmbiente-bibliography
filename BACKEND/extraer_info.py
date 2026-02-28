import os
import json
import time
import hashlib # <--- NECESARIO para calcular hash si no viene de fuera
import requests
import pypdf
import pytesseract
from pdf2image import convert_from_path
from database import SessionLocal
import models
from datetime import datetime
from dotenv import load_dotenv

# === CONFIGURACIÓN ===
UPLOAD_DIR = "/var/www/tecnoambiente/BACKEND/uploads" 
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- 1. Funciones Auxiliares ---
def recortar_seguro(texto, limite=250):
    if not texto: return "Desconocido"
    texto_str = str(texto)
    if len(texto_str) > limite: return texto_str[:limite-3] + "..."
    return texto_str

def limpiar_datos(datos):
    defaults = {
        "titulo": "Título desconocido", "autores": ["Desconocido"], "anio": "S/F",
        "familia": "Desconocida", "genero": ["Desconocido"], "especie": ["No especificada"],
        "distribucion": "Desconocida", "palabras_clave": []
    }
    for key, default in defaults.items():
        if not datos.get(key): datos[key] = default
    return datos

def calcular_hash_interno(ruta_archivo):
    """Función de respaldo por si procesar_pdf se llama sin hash externo"""
    sha256_hash = hashlib.sha256()
    try:
        with open(ruta_archivo, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"      ❌ Error calculando hash interno: {e}")
        return None

# --- 2. MOTOR DE LECTURA ---
def obtener_texto_inteligente(ruta_pdf):
    print(f"   🔍 Analizando: {os.path.basename(ruta_pdf)}")
    texto_final = ""
    
    # A. Lectura Digital
    try:
        reader = pypdf.PdfReader(ruta_pdf)
        limit_digital = min(len(reader.pages), 10)
        for i in range(limit_digital):
            extracted = reader.pages[i].extract_text()
            if extracted: texto_final += extracted + "\n"
    except Exception as e:
        print(f"      ⚠️ Fallo pypdf: {e}")

    if len(texto_final.strip()) > 100:
        print("      ⚡ Texto digital detectado.")
        return texto_final

    # B. OCR Local (150 DPI para equilibrio RAM/Calidad)
    print("      📸 PDF Escaneado. Activando OCR Local (150 dpi)...")
    try:
        # Usamos 150 dpi que es mejor que 100 y no mata el servidor como 300
        images = convert_from_path(ruta_pdf, first_page=1, last_page=2, dpi=150)
        texto_ocr = ""
        for image in images:
            texto_ocr += pytesseract.image_to_string(image, lang='spa')
        print(f"      ✅ OCR Terminado ({len(texto_ocr)} caracteres).")
        return texto_ocr
    except Exception as e:
        print(f"      ❌ Error OCR: {e}")
        return ""

# --- 3. Análisis con Gemini ---
def analizar_con_gemini(texto_completo):
    texto_para_enviar = texto_completo[:15000]
    
    prompt_texto = (
        "Eres un experto biólogo marino. Analiza el texto.\n"
        "Extrae JSON: titulo, autores, anio, familia, genero, especie, distribucion, palabras_clave.\n"
        "Si no hay datos: 'Desconocido'.\n"
        f"TEXTO:\n{texto_para_enviar}"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt_texto}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }

    try:
        print(f"      🧠 Enviando a Gemini 2.5 Flash (HTTP)...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            resultado_json = response.json()
            try:
                texto_respuesta = resultado_json['candidates'][0]['content']['parts'][0]['text']
                return limpiar_datos(json.loads(texto_respuesta))
            except Exception as e:
                print(f"      ⚠️ Respuesta mal formada: {e}")
                return limpiar_datos({})
        elif response.status_code == 429:
             print("      🛑 Cuota excedida (429).")
             return limpiar_datos({})
        else:
            print(f"      ⚠️ Error API {response.status_code}")
            return limpiar_datos({})

    except Exception as e:
        print(f"      ⚠️ Error Conexión: {e}")
        return limpiar_datos({})

# --- 4. Guardado en BD (CON VARIABLE archivo_hash) ---
def insertar_en_bd(datos, ruta_pdf, archivo_hash):
    db = SessionLocal()
    try:
        # Verificar duplicado por hash antes de insertar
        if db.query(models.Documento).filter(models.Documento.archivo_hash == archivo_hash).first():
             print(f"⏭️ Duplicado encontrado al insertar.")
             return # Doble seguridad

        doc = models.Documento(
            titulo=recortar_seguro(datos.get("titulo"), 500),
            autores=recortar_seguro(", ".join(datos["autores"]) if isinstance(datos["autores"], list) else datos["autores"]),
            anio=str(datos.get("anio"))[:50],
            palabras_clave=recortar_seguro(", ".join(datos["palabras_clave"]) if isinstance(datos["palabras_clave"], list) else datos["palabras_clave"], 500),
            ruta_pdf=ruta_pdf,
            archivo_hash=archivo_hash,  # <--- GUARDAMOS LA VARIABLE AQUÍ
            fecha_subida=datetime.now()
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        fam = recortar_seguro(", ".join(datos.get("familia", [])) if isinstance(datos.get("familia"), list) else datos.get("familia"))
        gen = recortar_seguro(", ".join(datos.get("genero", [])) if isinstance(datos.get("genero"), list) else datos.get("genero"))
        dist = recortar_seguro(str(datos.get("distribucion")))
        
        especies = datos.get("especie", [])
        if isinstance(especies, str): especies = [especies]
        
        for esp in especies[:10]:
            nuevo_esp = models.Especie(familia=fam, genero=gen, especie=recortar_seguro(esp, 250), distribucion=dist)
            db.add(nuevo_esp)
            doc.especies.append(nuevo_esp)

        db.commit()
        print(f"✅ Guardado: {os.path.basename(ruta_pdf)}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error BD: {e}")
        raise e # Lanzamos error para que procesar_pdf lo capture
    finally:
        db.close()

# --- 5. Main (CON ARGUMENTO archivo_hash y RETORNOS) ---
def procesar_pdf(nombre_pdf, archivo_hash=None):
    ruta = os.path.join(UPLOAD_DIR, nombre_pdf)
    if nombre_pdf.startswith("._"): 
        return {"status": "ignored", "message": "Archivo oculto"}

    print(f"🎬 Procesando: {nombre_pdf}")

    # 1. GESTIÓN DEL HASH
    # Si no nos pasan el hash desde el router, lo calculamos aquí
    if not archivo_hash:
        archivo_hash = calcular_hash_interno(ruta)
    
    if not archivo_hash:
        return {"status": "error", "message": "No se pudo generar el hash"}

    # 2. VERIFICAR DUPLICADO (Seguridad Extra)
    db = SessionLocal()
    # Asegúrate de que en models.py la columna se llame 'archivo_hash' o 'file_hash' según tu BD
    duplicado = db.query(models.Documento).filter(models.Documento.archivo_hash == archivo_hash).first()
    db.close()

    if duplicado:
        return {
            "status": "duplicate", 
            "message": "El archivo ya existe en la base de datos.",
            "file": nombre_pdf
        }

    # 3. PROCESO DE IA
    try:
        texto = obtener_texto_inteligente(ruta)
        if not texto: 
            return {"status": "error", "message": "No se pudo leer texto del PDF"}

        datos = analizar_con_gemini(texto)
        
        # Pasamos el hash para guardarlo
        insertar_en_bd(datos, ruta, archivo_hash)
        
        return {"status": "success", "message": "Procesado correctamente"}

    except Exception as e:
        print(f"❌ Error en procesar_pdf: {e}")
        return {"status": "error", "message": str(e)}