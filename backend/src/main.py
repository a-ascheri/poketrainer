# FastAPI Básico: Crear app, rutas, documentación automática
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.system import router as system_router
from src.routes.trainer import router as trainer_router
from src.routes.user import router as user_router

# Constructor principa, Nombre en /docs, Descripción, Versión de la API
app = FastAPI(
    title="PokeTrainer",
    description="API para entrenadores",
    version="1.0.0",
)

# Habilitar CORS para el frontend en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Cambia esto en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(trainer_router)
app.include_router(system_router)
