# FastAPI Básico: Crear app, rutas, documentación automática
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database.database import SessionLocal, setup_engine
from src.routes.admin import router as admin_router
from src.routes.system import router as system_router
from src.routes.trainer import router as trainer_router
from src.routes.trainer_pokemon import router as trainer_pokemon_router
from src.routes.user import router as user_router
from src.services.user_service import ensure_initial_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_engine()
    db = SessionLocal()
    try:
        ensure_initial_admin(db)
    finally:
        db.close()
    yield


# Constructor principa, Nombre en /docs, Descripción, Versión de la API
app = FastAPI(
    title="PokeTrainer",
    description="API para entrenadores",
    version="1.0.0",
    lifespan=lifespan,
)

# Habilitar CORS para el frontend en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Cambiar esto en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(trainer_router)
app.include_router(admin_router)
app.include_router(trainer_pokemon_router)
app.include_router(system_router)
