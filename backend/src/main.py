# FastAPI Básico: Crear app, rutas, documentación automática
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.database.database import SessionLocal, setup_engine
from src.routes.admin import router as admin_router
from src.routes.game import router as game_router
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
openapi_tags = [
    {
        "name": "Game",
        "description": (
            "Endpoints de estado de juego: partida guardada, posición en el mundo,"
            " party activa e inventario del entrenador."
        ),
    },
    {
        "name": "Admin",
        "description": (
            "Endpoints administrativos para gestion de usuarios, roles y"
            " operaciones internas. Solo accesible para administradores."
        ),
    },
    {
        "name": "Trainer",
        "description": (
            "Endpoints de logica de juego para entrenadores autenticados"
            " (starter, captura, experiencia, stats y movimientos)."
        ),
    },
    {
        "name": "User",
        "description": (
            "Endpoints de autenticacion y cuenta de usuario"
            " (registro, login, perfil y cambio de contrasena)."
        ),
    },
    {
        "name": "System",
        "description": "Endpoints de estado del sistema y health checks.",
    },
]

app = FastAPI(
    title="PokeTrainer",
    description="API para entrenadores",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=openapi_tags,
)

cors_origins = [
    origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()
]

# Habilitar CORS para el frontend en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(trainer_router)
app.include_router(admin_router)
app.include_router(trainer_pokemon_router)
app.include_router(game_router)
app.include_router(system_router)
