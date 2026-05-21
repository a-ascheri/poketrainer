from fastapi import APIRouter


router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "¡Bienvenido a Pok-ETrainer!",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "documentation": "/docs",
            "health_check": "/health",
            "trainers": "/trainers/"
        }
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "poketrainer-api",
        "timestamp": "2024-01-15T10:00:00Z"
    }
