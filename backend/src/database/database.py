# Conexión a PostgreSQL para PokéTrainer
# Versión optimizada para Alembic
import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión a PostgreSQL
# FORMATO: postgresql://usuario:contraseña@host:puerto/nombre_bd
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://pokemaster:pikapassword123@localhost:5433/poketrainer"
)

# Base para todos los modelos SQLAlchemy
# Fábrica de sesiones (sin engine todavía)
# Engine se configurará después
Base = declarative_base()
SessionLocal = sessionmaker()
engine = None


# Configura el engine de SQLAlchemy.
# Importa create_engine SOLO cuando sea necesario,
# evitando errores de importación temprana con psycopg2.
def setup_engine(url: str = None):
    global engine, SessionLocal
    # Importación diferida
    from sqlalchemy import create_engine

    url_to_use = url or DATABASE_URL
    engine = create_engine(url_to_use)
    SessionLocal.configure(bind=engine)
    return engine


# Proporciona una sesión de base de datos.
# Uso en FastAPI:
# @app.get("/items")
# def read_items(db: Session = Depends(get_db)):
# return db.query(Item).all()
def get_db():
    if engine is None:
        setup_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
