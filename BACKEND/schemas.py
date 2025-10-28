from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UsuarioCreate(BaseModel):
    username: str
    email: str
    password: str
    rol_id: int  # Relacionado con la tabla de roles

    class Config:
        orm_mode = True

        
class UsuarioLogin(BaseModel):
    username: str
    password: str

class UsuarioOut(BaseModel):
    id: int
    username: str
    rol_id: int
    email: str 
    
    class Config:
        orm_mode = True
         
class DocumentoCreate(BaseModel):
    titulo: str
    autores: Optional[str]
    anio: str
    palabras_clave: Optional[str]
    ruta_pdf: str

    class Config:
        from_attributes = True

class Especie(BaseModel):
    familia: Optional[str]
    genero: Optional[str]
    especie: Optional[str]
    distribucion: Optional[str]

    class Config:
        orm_mode = True

class Documento(BaseModel):
    id: int
    titulo: str
    autores: Optional[str]
    anio: str                         
    palabras_clave: Optional[str]
    ruta_pdf: str
    fecha_subida: datetime
    especies: List[Especie] = []

    class Config:
        orm_mode = True

class EspecieBase(BaseModel):
    familia: Optional[str]
    genero: Optional[str]
    especie: Optional[str]
    distribucion: Optional[str]

class DocumentoUpdate(BaseModel):
    titulo: str
    autores: Optional[str]
    anio: Optional[str]
    palabras_clave: Optional[str]
    especies: List[EspecieBase]