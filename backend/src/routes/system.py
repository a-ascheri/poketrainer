from fastapi import APIRouter

from src.routes.prefixes import (ADMIN_TRAINER_PREFIX, API_V1_PREFIX,
                                 GAME_TRAINER_PREFIX, SYSTEM_PREFIX)

router = APIRouter(prefix=SYSTEM_PREFIX, tags=["System"])


@router.get("/")
def home():
    return {
        "message": "¡Bienvenido a Pok-ETrainer!",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "documentation": "/docs",
            "api_base": API_V1_PREFIX,
            "health_check": f"{SYSTEM_PREFIX}/health",
            "admin_trainers": f"{ADMIN_TRAINER_PREFIX}/",
            "game_trainer": GAME_TRAINER_PREFIX,
        },
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "poketrainer-api",
        "timestamp": "2024-01-15T10:00:00Z",
    }
