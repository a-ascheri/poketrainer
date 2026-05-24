from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.routes.user import require_admin
from src.schemas.trainer import TrainerCreate, TrainerRead, TrainerUpdate
from src.services.trainer_service import (
    create_trainer,
    delete_trainer,
    list_trainers,
    update_trainer,
)

from ..database.database import get_db

router = APIRouter()


@router.post("/trainers/", response_model=TrainerRead)
def create_trainer_route(
    trainer: TrainerCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return create_trainer(trainer, db)


@router.get("/trainers/", response_model=list[TrainerRead])
def list_trainers_route(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return list_trainers(db)


@router.put("/trainers/{trainer_id}", response_model=TrainerRead)
def update_trainer_route(
    trainer_id: int,
    trainer_update: TrainerUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return update_trainer(trainer_id, trainer_update, db)


@router.delete("/trainers/{trainer_id}")
def delete_trainer_route(
    trainer_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    """_summary_

    Args:
        trainer_id (int): _description_
        db (Session, optional): _description_. Defaults to Depends(get_db).
        user (_type_, optional): _description_. Defaults to Depends(get_current_user).

    Returns:
        _type_: _description_
    """
    return delete_trainer(trainer_id, db)
