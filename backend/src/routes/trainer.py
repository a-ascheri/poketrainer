from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.database import get_db
from src.schemas.trainer import TrainerCreate, TrainerRead
from src.services.trainer_service import create_trainer, list_trainers
from src.routes.user import get_current_user


router = APIRouter()


@router.post("/trainers/", response_model=TrainerRead)
def create_trainer_route(
    trainer: TrainerCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return create_trainer(trainer, db)


@router.get("/trainers/", response_model=list[TrainerRead])
def list_trainers_route(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return list_trainers(db)
