# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Sustituir los valores REEMPLAZAR_... por las credenciales reales en el entorno de despliegue

DATABASE_URL = "mysql+pymysql://REEMPLAZAR_USUARIO:REEMPLAZAR_CONTRASEÑA@REEMPLAZAR_HOST/tecnoambiente"

engine = create_engine(DATABASE_URL,
pool_size=100,  # Tamaño del pool de conexiones
max_overflow=100,  # Máximo número de conexiones adicionales
pool_timeout=30,  # Timeout para obtener una conexión
pool_recycle=3600                      
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



Base = declarative_base()