import os
import hashlib
from sqlalchemy import text
from database import SessionLocal
import models

# Configuración
UPLOAD_DIR = "/var/www/tecnoambiente/BACKEND/uploads"

def calcular_hash(ruta_archivo):
    sha256_hash = hashlib.sha256()
    try:
        with open(ruta_archivo, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return None

def reparar_base_datos():
    db = SessionLocal()
    print("🚑 INICIANDO LIMPIEZA TOTAL Y REPARACIÓN DE LA BD...")
    
    # 1. Obtenemos TODOS los documentos
    docs = db.query(models.Documento).all()
    total = len(docs)
    print(f"📊 Total documentos a revisar: {total}")

    duplicados_eliminados = 0
    fantasmas_eliminados = 0
    actualizados = 0

    for i, doc in enumerate(docs):
        # Progreso visual cada 50 docs
        if i % 50 == 0: print(f"   ⏳ Procesando {i}/{total}...")

        # Construimos la ruta asumiendo que el archivo está en UPLOAD_DIR
        nombre_archivo = os.path.basename(doc.ruta_pdf)
        ruta_completa = os.path.join(UPLOAD_DIR, nombre_archivo)

        # ---------------------------------------------------------
        # CASO 1: EL FANTASMA (Registro en BD sin archivo físico)
        # ---------------------------------------------------------
        if not os.path.exists(ruta_completa):
            print(f"   [👻 FANTASMA] ID {doc.id} ({nombre_archivo}): Archivo no existe. Borrando registro...")
            try:
                db.delete(doc)
                db.commit() # Confirmamos eliminación inmediata
                fantasmas_eliminados += 1
            except Exception as e:
                db.rollback()
                print(f"      ❌ Error al borrar fantasma: {e}")
            continue # Pasamos al siguiente, este ya murió

        # ---------------------------------------------------------
        # CASO 2: CALCULAR HASH
        # ---------------------------------------------------------
        nuevo_hash = calcular_hash(ruta_completa)
        if not nuevo_hash:
            print(f"      ⚠️ No se pudo leer el archivo ID {doc.id} para hash.")
            continue

        # ---------------------------------------------------------
        # CASO 3: VERIFICAR DUPLICADOS (Integridad)
        # ---------------------------------------------------------
        # Buscamos si ALGUIEN MÁS tiene ya ese hash (y que no sea yo mismo)
        duplicado_existente = db.query(models.Documento).filter(
            models.Documento.archivo_hash == nuevo_hash,
            models.Documento.id != doc.id 
        ).first()

        if duplicado_existente:
            # ¡CONFLICTO! Ya existe otro documento igual.
            # Borramos el registro ACTUAL para mantener el anterior (o viceversa)
            print(f"   [🗑️ DUPLICADO] ID {doc.id} es copia del ID {duplicado_existente.id}. Eliminando ID {doc.id}...")
            try:
                db.delete(doc)
                db.commit()
                duplicados_eliminados += 1
            except Exception as e:
                db.rollback()
                print(f"      ❌ Error al borrar duplicado: {e}")

        else:
            # NO hay conflicto. Actualizamos el hash si hace falta.
            if doc.archivo_hash != nuevo_hash:
                doc.archivo_hash = nuevo_hash
                try:
                    db.commit()
                    # print(f"   [✅ HASH] ID {doc.id} actualizado.") 
                    actualizados += 1
                except Exception as e:
                    db.rollback()
                    print(f"      ❌ Error al guardar hash ID {doc.id}: {e}")

    print("="*60)
    print("🏁 LIMPIEZA FINALIZADA")
    print(f"   ✅ Documentos Sanos/Actualizados: {actualizados}")
    print(f"   👻 Fantasmas Eliminados (Sin archivo): {fantasmas_eliminados}")
    print(f"   🗑️ Duplicados Eliminados (Repetidos): {duplicados_eliminados}")
    print("="*60)
    db.close()

if __name__ == "__main__":
    reparar_base_datos()