from sqlalchemy import Table, Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# models.py
class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(200))
    rol_id = Column(Integer, ForeignKey('roles.id'))  # Relación con la tabla de roles

    rol = relationship('Role', back_populates='usuarios')  # Relación con la tabla Role

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True)

    usuarios = relationship('Usuario', back_populates='rol')

documento_especie = Table(
    "documento_especie",
    Base.metadata,
    Column("documento_id", Integer, ForeignKey("documentos.id"), primary_key=True),
    Column("especie_id", Integer, ForeignKey("especies.id"), primary_key=True)
)

class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    autores = Column(Text)
    anio = Column(String(255))
    palabras_clave = Column(Text)
    ruta_pdf = Column(String(500))
    fecha_subida = Column(TIMESTAMP)

    especies = relationship(
        "Especie",
        secondary=documento_especie,
        back_populates="documentos",
        lazy="joined",
        cascade="all, delete"
    )


class Especie(Base):
    __tablename__ = "especies"

    id = Column(Integer, primary_key=True, index=True)
    familia = Column(String(255))
    genero = Column(String(255))
    especie = Column(String(255))
    distribucion = Column(Text)

    documentos = relationship(
        "Documento",
        secondary=documento_especie,
        back_populates="especies"
    )
