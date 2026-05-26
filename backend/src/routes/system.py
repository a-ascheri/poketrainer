from fastapi import APIRouter

from src.routes.prefixes import (ADMIN_TRAINER_PREFIX, API_V1_PREFIX,
                                 GAME_TRAINER_PREFIX, SYSTEM_PREFIX)

router = APIRouter(tags=["System"])


@router.get("/")
def home():
    return {
        "message": "¡Bienvenido a Pok-ETrainer!",
        "status": "online",
        "version": "1.0.0",
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
        "timestamp": "2024-01-15T10:00:00Z",
    }
