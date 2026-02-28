from database import SessionLocal
import models
from sqlalchemy import desc

# Conectamos a la BD
db = SessionLocal()

print("="*60)
print("📊 AUDITORÍA DE LOS ÚLTIMOS 5 DOCUMENTOS GUARDADOS")
print("="*60)

# Sacamos los 5 últimos subidos
docs = db.query(models.Documento).order_by(desc(models.Documento.id)).limit(5).all()

if not docs:
    print("❌ No hay documentos en la base de datos.")
else:
    for doc in docs:
        print(f"📄 ID: {doc.id} | Archivo: {doc.ruta_pdf.split('/')[-1]}")
        print(f"   🔹 Título:   {doc.titulo}")
        print(f"   🔹 Autores:  {doc.autores}")
        print(f"   🔹 Año:      {doc.anio}")
        print(f"   🔹 Distrib.: {doc.especies[0].distribucion if doc.especies else 'No detectada'}")
        
        # Listar especies encontradas
        print("   🐟 Especies detectadas:")
        if doc.especies:
            for esp in doc.especies:
                print(f"      - {esp.genero} {esp.especie} (Fam: {esp.familia})")
        else:
            print("      ⚠️ Ninguna especie extraída")
            
        print("-" * 60)

db.close()