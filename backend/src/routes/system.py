from fastapi import APIRouter

from src.routes.prefixes import (API_V1_PREFIX, GAME_TRAINER_PREFIX,
                                 SYSTEM_PREFIX)

router = APIRouter(tags=["System"])


@router.get("/")
def home():
    return {
        "message": "¡Bienvenido a Pok-ETrainer!",
        "status": "online",
        "version": "9.0.0",
        "system consulting endpoints": {
            "documentation": "/docs",
            "health_check": "/health",
        },
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "poketrainer-api",
        "version": "9.0.0",
    }
