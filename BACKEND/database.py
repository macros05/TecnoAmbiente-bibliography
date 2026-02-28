# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost") 
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL,
pool_size=100,  # Tamaño del pool de conexiones
max_overflow=100,  # Máximo número de conexiones adicionales
pool_timeout=30,  # Timeout para obtener una conexión
pool_recycle=3600                      
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



Base = declarative_base()