from datetime import timedelta
import hashlib
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Header, Path, Query, UploadFile, File, status 
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse, StreamingResponse
from jose import JWTError, jwt
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import APIRouter
from auth import router

import os
import shutil

import models, schemas, crud
from database import SessionLocal, engine
from models import Usuario
from schemas import DocumentoUpdate, UsuarioCreate, UsuarioLogin, UsuarioOut
from extraer_info import procesar_pdf
from models import Documento 
from auth import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_user,
    get_current_user,
    verify_password,
    admin_required,
    router as auth_router
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)  # Ocultar documentación por defecto
main_router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@main_router.get("/docs", include_in_schema=False)
def protected_docs(current_user: Usuario = Depends(get_current_user)):
    admin_required(current_user)
    return RedirectResponse(url="/_docs")

@main_router.get("/openapi.json", include_in_schema=False)
def protected_openapi(current_user: Usuario = Depends(get_current_user)):
    admin_required(current_user)
    return JSONResponse(app.openapi())

@main_router.get("/_docs", include_in_schema=False)
def swagger_ui_html(current_user: Usuario = Depends(get_current_user)):
    admin_required(current_user)
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")

# Listar documentos
@main_router.get("/documentos", response_model=list[schemas.Documento])
def listar_documentos(db: Session = Depends(get_db), current_user: Usuario = Depends(admin_required)):
    return crud.obtener_documentos(db)

# Crear documento
@main_router.post("/documentos", response_model=schemas.Documento)
def crear_documento(doc: schemas.DocumentoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(admin_required)):
    return crud.crear_documento(db, doc)

# Listar especies 
@main_router.get("/especies", response_model=list[schemas.Especie])
def listar_especies(db: Session = Depends(get_db)):
    return crud.obtener_especies(db)

## Búsqueda con filtros Y ORDENACIÓN
@main_router.get("/documentos/buscar", response_model=dict)
def buscar_documentos(
    titulo: str = "",
    autor: str = "",
    familia: str = "",
    genero: str = "",
    especie: str = "",
    palabras_clave: str = "",
    distribucion: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    order_by: str = Query(None, description="Campo por el que ordenar: 'titulo' o 'fecha'"),
    order_dir: str = Query("asc", description="Dirección: 'asc' o 'desc'"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Documento).options(joinedload(models.Documento.especies))

    if titulo:
        query = query.filter(models.Documento.titulo.ilike(f"%{titulo}%"))
    if autor:
        query = query.filter(models.Documento.autores.ilike(f"%{autor}%"))
    if palabras_clave:
        palabras = palabras_clave.split(",")
        condiciones_palabras = [models.Documento.palabras_clave.ilike(f"%{p.strip()}%") for p in palabras]
        query = query.filter(or_(*condiciones_palabras))

    if familia or genero or especie or distribucion:
        query = query.join(models.Documento.especies)
        if familia:
            query = query.filter(models.Especie.familia.ilike(f"%{familia}%"))
        if genero:
            query = query.filter(models.Especie.genero.ilike(f"%{genero}%"))
        if especie:
            query = query.filter(models.Especie.especie.ilike(f"%{especie}%"))
        if distribucion:
            query = query.filter(models.Especie.distribucion.ilike(f"%{distribucion}%"))

  
    if order_by == "titulo":
        if order_dir == "desc":
            query = query.order_by(models.Documento.titulo.desc())
        else:
            query = query.order_by(models.Documento.titulo.asc())
            
    elif order_by == "fecha":
        if order_dir == "desc":
            query = query.order_by(models.Documento.fecha_subida.desc())
        else:
            query = query.order_by(models.Documento.fecha_subida.asc())
            
    else:
        query = query.order_by(models.Documento.id.asc())

    total = query.distinct().count()
    resultados = query.distinct().offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "resultados": jsonable_encoder(resultados)
    }

@main_router.post("/documentos/subir")
async def subir_documentos(
    archivos: List[UploadFile] = File(...), 
    db: Session = Depends(get_db)
):
    resultados = []

    for archivo in archivos:
        ruta_temp = os.path.join("uploads", archivo.filename)
        
        try:
            
            contenido = await archivo.read()
            sha_hash = hashlib.sha256(contenido).hexdigest()

            existe = db.query(models.Documento).filter(models.Documento.archivo_hash == sha_hash).first()
            
            if existe:
                resultados.append({
                    "archivo": archivo.filename, 
                    "status": "⛔ Duplicado",
                    "mensaje": "El archivo ya existe en la base de datos."
                })
                continue 

            with open(ruta_temp, "wb") as f:
                f.write(contenido)

           
            respuesta_proceso = procesar_pdf(archivo.filename, archivo_hash=sha_hash)

            # 5. INTERPRETAR RESPUESTA
            if respuesta_proceso["status"] == "success":
                resultados.append({
                    "archivo": archivo.filename,
                    "status": "✅ Procesado",
                    "mensaje": "Guardado correctamente con IA."
                })
            elif respuesta_proceso["status"] == "duplicate":
                # Por si acaso hubo una condición de carrera
                resultados.append({
                    "archivo": archivo.filename,
                    "status": "⛔ Duplicado",
                    "mensaje": "Detectado duplicado durante el procesamiento."
                })
            else:
                resultados.append({
                    "archivo": archivo.filename,
                    "status": "❌ Error Procesamiento",
                    "mensaje": respuesta_proceso.get("message", "Error desconocido")
                })

        except Exception as e:
            # Si falló algo crítico, borramos el archivo para no dejar basura
            if os.path.exists(ruta_temp):
                os.remove(ruta_temp)
            
            resultados.append({
                "archivo": archivo.filename, 
                "status": "❌ Error Crítico", 
                "error": str(e)
            })

    return {"resultados": resultados}

@main_router.delete("/documentos/{doc_id}")
def eliminar_documento(
    doc_id: int, 
    db: Session = Depends(get_db), 
):
    doc = db.query(models.Documento).filter(models.Documento.id == doc_id).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    try:
        if doc.ruta_pdf and os.path.exists(doc.ruta_pdf):
            os.remove(doc.ruta_pdf)
            print(f"🗑️ Archivo físico eliminado: {doc.ruta_pdf}")
        else:
            print(f"⚠️ No se encontró el archivo físico: {doc.ruta_pdf}")
    except Exception as e:
        print(f"❌ Error al borrar archivo de disco: {e}")

    db.delete(doc)
    db.commit()

    return {"message": "Documento eliminado correctamente", "id": doc_id}

from fastapi import Query

from fastapi.responses import FileResponse

@main_router.get("/ver-pdf")
def ver_pdf(nombre: str = Query(...), authorization: str = Header(...)):
    # Obtener el token desde la cabecera Authorization
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Formato de autorización inválido")
    token = authorization.removeprefix("Bearer ").strip()

    # Validar token y extraer datos
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Cargar PDF
    file_path = os.path.join("uploads", os.path.basename(nombre))
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=nombre,
        headers={"Content-Disposition": "inline"}
    )

@main_router.put("/documentos/{id}")
def actualizar_documento(id: int, datos: DocumentoUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(admin_required)):
    doc = db.query(Documento).filter(Documento.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    doc.titulo = datos.titulo
    doc.autores = datos.autores
    doc.anio = datos.anio
    doc.palabras_clave = datos.palabras_clave

    doc.especies.clear() 
    
    for especie_data in datos.especies:
        especie = models.Especie(
            familia=especie_data.familia,
            genero=especie_data.genero,
            especie=especie_data.especie,
            distribucion=especie_data.distribucion
        )
        doc.especies.append(especie)

    db.commit()
    return {"msg": "Documento actualizado correctamente"}

@auth_router.post("/register", response_model=UsuarioOut)
def register(user: UsuarioCreate, db: Session = Depends(get_db)):
    db_user = db.query(Usuario).filter(Usuario.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado")
    return create_user(db, user)

@auth_router.post("/login")
def login(user: UsuarioLogin, db: Session = Depends(get_db)):
    db_user = db.query(Usuario).filter(Usuario.email == user.username).first()
    
    if not db_user:
        db_user = db.query(Usuario).filter(Usuario.username == user.username).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    
    token = create_access_token(
        data={
            "sub": db_user.username,
            "rol_id": db_user.rol_id,
            "role": "admin" if db_user.rol_id == 1 else "user"
        },
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token": token, "token_type": "bearer", "rol_id": db_user.rol_id}

#  Incluir rutas
app.include_router(auth_router, prefix="/api")
app.include_router(router, prefix="/api")
app.include_router(main_router, prefix="/api")  
