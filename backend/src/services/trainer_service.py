from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.models.trainer import Trainer
from src.schemas.trainer import TrainerCreate, TrainerUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_trainer(trainer: TrainerCreate, db: Session):
    db_trainer = (
        db.query(Trainer)
        .filter(
            (Trainer.username == trainer.username) | (Trainer.email == trainer.email)
        )
        .first()
    )

    if db_trainer:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )

    hashed_password = get_password_hash(trainer.password)
    new_trainer = Trainer(
        username=trainer.username, email=trainer.email, hashed_password=hashed_password
    )
    db.add(new_trainer)
    db.commit()
    db.refresh(new_trainer)

    return new_trainer


def list_trainers(db: Session):
    return db.query(Trainer).all()


def update_trainer(trainer_id: int, trainer_update: TrainerUpdate, db: Session):
    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    if trainer_update.username is not None:
        # Check for username uniqueness
        if (
            db.query(Trainer)
            .filter(
                Trainer.username == trainer_update.username, Trainer.id != trainer_id
            )
            .first()
        ):
            raise HTTPException(status_code=400, detail="Username already registered")
        trainer.username = trainer_update.username

    if trainer_update.email is not None:
        # Check for email uniqueness
        if (
            db.query(Trainer)
            .filter(Trainer.email == trainer_update.email, Trainer.id != trainer_id)
            .first()
        ):
            raise HTTPException(status_code=400, detail="Email already registered")
        trainer.email = trainer_update.email

    if trainer_update.password is not None:
        trainer.hashed_password = get_password_hash(trainer_update.password)

    db.commit()
    db.refresh(trainer)
    return trainer


def delete_trainer(trainer_id: int, db: Session):
    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    db.delete(trainer)
    db.commit()
    return {"detail": "Trainer deleted"}
