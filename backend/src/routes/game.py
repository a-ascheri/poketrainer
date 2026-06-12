from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.routes.auth_dependencies import require_trainer
from src.routes.prefixes import GAME_PREFIX
from src.schemas.game_save import GameSaveRead, GameSaveUpdate
from src.services import game_service

router = APIRouter(prefix=GAME_PREFIX, tags=["Game"])


@router.get("/save", response_model=GameSaveRead)
def load_save(
    current_user=Depends(require_trainer),
    db: Session = Depends(get_db),
):
    """
    Obtiene el estado actual de la partida del entrenador. Si no existe una partida, devuelve 404.
    
    Args:
        current_user (_type_, optional): _description_. Defaults to Depends(require_trainer).
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _type_: _description_
    """
    return game_service.get_game_save_or_404(current_user.id, db)


@router.post(
    "/save",
    response_model=GameSaveRead,
    status_code=status.HTTP_201_CREATED
)
def new_game(
    current_user=Depends(require_trainer),
    db: Session = Depends(get_db),
):
    """
    Crea una nueva partida para el entrenador. Si ya existe una partida, devuelve 400.

    Args:
        current_user (_type_, optional): _description_. Defaults to Depends(require_trainer).
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _type_: _description_
    """
    return game_service.create_game_save(current_user.id, db)


@router.put(
    "/save", response_model=GameSaveRead)
def save_game(
    payload: GameSaveUpdate,
    current_user=Depends(require_trainer),
    db: Session = Depends(get_db),
):
    """
    Su funcion es guardar el estado actual de la partida del entrenador.

    Args:
        payload (GameSaveUpdate): _description_
        current_user (_type_, optional): _description_. Defaults to Depends(require_trainer).
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _type_: _description_
    """
    return game_service.update_game_save(current_user.id, payload, db)


@router.post(
    "/save/party/{slot_position}",
    response_model=GameSaveRead,
)
def set_party_slot(
    slot_position: int,
    trainer_pokemon_id: int,
    current_user=Depends(require_trainer),
    db: Session = Depends(get_db),
):
    """
    Asigna un pokémon al slot indicado de la party activa.

    Args:
        slot_position (int): _description_
        trainer_pokemon_id (int): _description_
        current_user (_type_, optional): _description_. Defaults to Depends(require_trainer).
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _type_: _description_
    """
    game_service.set_party_slot(current_user.id, trainer_pokemon_id, slot_position, db)
    return game_service.get_game_save_or_404(current_user.id, db)


@router.delete(
    "/save/party/{slot_position}",
    response_model=GameSaveRead,
)
def remove_party_slot(
    slot_position: int,
    current_user=Depends(require_trainer),
    db: Session = Depends(get_db),
):
    """
    Elimina un pokémon del slot indicado de la party activa.

    Args:
        slot_position (int): _description_
        current_user (_type_, optional): _description_. Defaults to Depends(require_trainer).
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _type_: _description_
    """
    game_service.remove_party_slot(current_user.id, slot_position, db)
    return game_service.get_game_save_or_404(current_user.id, db)
