from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Usuario
from database import SessionLocal
from schemas import UsuarioCreate, UsuarioLogin, UsuarioOut

router = APIRouter()

# Seguridad y configuración JWT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Reemplazar secret key. 
SECRET_KEY = "e7e56b70a6235a50fc65f72dd3128d91f013ce76377fddf45052e3b1406fa201"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependency para base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# Obtener usuario actual desde el token
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Usuario:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        user = db.query(Usuario).filter(Usuario.username == username).first()
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Verificar si es administrador
def admin_required(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol_id != 1:
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")

# Crear usuario
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_user(db: Session, user: UsuarioCreate):
    db_user = Usuario(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        rol_id=user.rol_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Endpoints de usuarios
@router.get("/usuarios", response_model=List[UsuarioOut])
def get_all_users(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    admin_required(current_user)
    return db.query(Usuario).all()

@router.delete("/usuarios/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    admin_required(current_user)
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()

@router.put("/usuarios/{user_id}", response_model=UsuarioOut)
def update_user(user_id: int, user_update: UsuarioCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    admin_required(current_user)
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.username = user_update.username
    user.email = user_update.email
    if user_update.password:
        user.hashed_password = hash_password(user_update.password)
    user.rol_id = user_update.rol_id
    db.commit()
    db.refresh(user)
    return user
