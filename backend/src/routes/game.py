from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.routes.auth_dependencies import require_trainer
from src.routes.prefixes import GAME_PREFIX
from src.schemas.game_save import GameSaveRead, GameSaveUpdate
from src.services import game_service

router = APIRouter(prefix=GAME_PREFIX, tags=["Game"])


@router.get("/save", response_model=GameSaveRead, summary="Cargar partida guardada")
def load_save(
    current_user=Depends(require_trainer),
    db: Session = Depends(get_db),
):
    """Devuelve la partida guardada del entrenador autenticado."""
    return game_service.get_game_save_or_404(current_user.id, db)


@router.post("/save", response_model=GameSaveRead, status_code=status.HTTP_201_CREATED, summary="Crear nueva partida")
def new_game(
    current_user=Depends(require_trainer),
    db: Session = Depends(get_db),
):
    """Crea una nueva partida para el entrenador (solo si no existe una)."""
    return game_service.create_game_save(current_user.id, db)


@router.put("/save", response_model=GameSaveRead, summary="Guardar partida (autosave / manual)")
def save_game(
    payload: GameSaveUpdate,
    current_user=Depends(require_trainer),
    db: Session = Depends(get_db),
):
    """Actualiza el estado de la partida del entrenador (posición, inventario, flags, etc.)."""
    return game_service.update_game_save(current_user.id, payload, db)


@router.post(
    "/save/party/{slot_position}",
    response_model=GameSaveRead,
    summary="Asignar pokémon a un slot de la party",
)
def set_party_slot(
    slot_position: int,
    trainer_pokemon_id: int,
    current_user=Depends(require_trainer),
    db: Session = Depends(get_db),
):
    """Asigna un pokémon del trainer a un slot (0-5) de la party activa."""
    game_service.set_party_slot(current_user.id, trainer_pokemon_id, slot_position, db)
    return game_service.get_game_save_or_404(current_user.id, db)


@router.delete(
    "/save/party/{slot_position}",
    response_model=GameSaveRead,
    summary="Remover pokémon de la party",
)
def remove_party_slot(
    slot_position: int,
    current_user=Depends(require_trainer),
    db: Session = Depends(get_db),
):
    """Remueve un pokémon del slot indicado de la party activa."""
    game_service.remove_party_slot(current_user.id, slot_position, db)
    return game_service.get_game_save_or_404(current_user.id, db)
