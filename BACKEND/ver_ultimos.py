import os
from database import SessionLocal
import models

def ver_ultimos_registros():
    db = SessionLocal()
    
    # Traemos los 20 últimos (ID más alto = más nuevo)
    print(f"\n🔍 MOSTRANDO LOS ÚLTIMOS 20 DOCUMENTOS INSERTADOS:\n")
    docs = db.query(models.Documento).order_by(models.Documento.id.desc()).limit(20).all()

    # Cabecera
    print(f"{'ID':<6} | {'FECHA SUBIDA':<20} | {'ARCHIVO':<35} | {'TÍTULO EXTRACTADO'}")
    print("-" * 130)

    for doc in docs:
        # Limpieza visual de datos para que quepa en pantalla
        nombre_archivo = os.path.basename(doc.ruta_pdf) if doc.ruta_pdf else "SIN RUTA"
        if len(nombre_archivo) > 33: nombre_archivo = nombre_archivo[:30] + "..."
        
        titulo = doc.titulo if doc.titulo else "SIN TÍTULO"
        if len(titulo) > 50: titulo = titulo[:47] + "..."
        
        fecha = str(doc.fecha_subida)[:19] if doc.fecha_subida else "---"

        print(f"{doc.id:<6} | {fecha:<20} | {nombre_archivo:<35} | {titulo}")

    print("-" * 130)
    db.close()

if __name__ == "__main__":
    ver_ultimos_registros()