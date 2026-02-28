from database import SessionLocal
from models import Usuario, Role
from passlib.context import CryptContext

# Configuración de seguridad (encriptado)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def crear_datos_iniciales():
    db = SessionLocal()
    try:
        print("🛠️  Iniciando configuración inicial...")

        # --- 1. CREAR ROLES ---
        # Buscamos si existe el rol 'admin', si no, lo creamos
        rol_admin = db.query(Role).filter_by(nombre="admin").first()
        if not rol_admin:
            rol_admin = Role(nombre="admin")
            db.add(rol_admin)
            print("✅ Rol 'admin' creado.")
        else:
            print("ℹ️  El rol 'admin' ya existía.")

        # Buscamos si existe el rol 'usuario'
        rol_usuario = db.query(Role).filter_by(nombre="usuario").first()
        if not rol_usuario:
            rol_usuario = Role(nombre="usuario")
            db.add(rol_usuario)
            print("✅ Rol 'usuario' creado.")
        
        # Guardamos los roles para que tengan ID
        db.commit()
        db.refresh(rol_admin)

        # --- 2. CREAR SUPERUSUARIO ---
        usuario_admin = db.query(Usuario).filter_by(username="admin").first()
        
        if not usuario_admin:
            # Encriptamos la contraseña "admin123"
            password_secreta = pwd_context.hash("admin123")
            
            nuevo_admin = Usuario(
                username="admin",
                email="admin@tecnoambiente.com",
                hashed_password=password_secreta,
                rol_id=rol_admin.id  # Le asignamos el ID del rol admin que acabamos de recuperar
            )
            db.add(nuevo_admin)
            db.commit()
            print("\n🎉 ¡ÉXITO TOTAL!")
            print("-----------------------------------")
            print("👤 Usuario:  admin")
            print("🔑 Password: admin123")
            print("-----------------------------------")
        else:
            print("\n⚠️  El usuario 'admin' ya existe. No se ha tocado nada.")

    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    crear_datos_iniciales()