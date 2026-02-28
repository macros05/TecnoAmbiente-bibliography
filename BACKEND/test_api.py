import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

print(f"🔑 Analizando llave: {API_KEY[:10]}...")

# 1. Obtener la lista REAL de modelos disponibles para TI
url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
headers = {'Content-Type': 'application/json'}

try:
    print("📋 Descargando catálogo de modelos...")
    response = requests.get(url_list, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error descargando lista: {response.text}")
        exit()
        
    data = response.json()
    modelos = data.get('models', [])
    
    candidatos = []
    print(f"🔎 Encontrados {len(modelos)} modelos. Filtrando los válidos...")
    
    for m in modelos:
        nombre = m['name'] # Ej: models/gemini-pro
        metodos = m.get('supportedGenerationMethods', [])
        
        # Solo queremos modelos que generen texto (generateContent)
        if 'generateContent' in metodos:
            # Filtramos los experimentales o muy nuevos que suelen dar error 429
            candidatos.append(nombre)

    print(f"✅ Candidatos viables: {len(candidatos)}")

    # 2. Probar uno por uno hasta que funcione
    modelo_ganador = None
    
    for modelo in candidatos:
        print(f"\n👉 Probando conexión con: {modelo} ...")
        
        # URL de prueba
        # Quitamos 'models/' del inicio si la URL ya lo espera, o lo ajustamos
        # La API espera: .../models/gemini-pro:generateContent
        # El nombre ya viene como 'models/gemini-pro'
        
        url_test = f"https://generativelanguage.googleapis.com/v1beta/{modelo}:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": "TEST"}]}],
            "generationConfig": {"maxOutputTokens": 5}
        }
        
        try:
            r = requests.post(url_test, headers=headers, json=payload, timeout=10)
            
            if r.status_code == 200:
                print(f"🎉 ¡BINGO! Este modelo funciona: {modelo}")
                modelo_ganador = modelo
                break # Dejamos de buscar
            else:
                print(f"   ❌ Falló con error {r.status_code}: {r.text[:100]}...")
                
        except Exception as e:
            print(f"   ⚠️ Error de red: {e}")

    # 3. Resultado final
    if modelo_ganador:
        print("\n" + "="*40)
        print("🚀 SOLUCIÓN ENCONTRADA")
        print("="*40)
        print("Ve a tu archivo 'pdf_processor.py' y busca la línea:")
        print('url = f"https://generativelanguage.googleapis.com/v1beta/models/..."')
        print("\nCAMBIA ESA LÍNEA POR ESTA EXACTA:")
        print(f'url = f"https://generativelanguage.googleapis.com/v1beta/{modelo_ganador}:generateContent?key={{GEMINI_API_KEY}}"')
        print("="*40)
    else:
        print("\n💀 Ningún modelo funcionó. Tu API Key tiene bloqueos graves.")

except Exception as e:
    print(f"❌ Error fatal: {e}")
    