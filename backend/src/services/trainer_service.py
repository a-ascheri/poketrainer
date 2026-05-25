from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.trainer import TrainerCreate, TrainerUpdate
from src.services.user_service import TRAINER_ROLE, get_password_hash


def create_trainer(trainer: TrainerCreate, db: Session):
    db_trainer = (
        db.query(User)
        .filter((User.username == trainer.username) | (User.email == trainer.email))
        .first()
    )

    if db_trainer:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )

    hashed_password = get_password_hash(trainer.password)
    new_trainer = User(
        username=trainer.username,
        email=trainer.email,
        hashed_password=hashed_password,
        role=TRAINER_ROLE,
        permissions=[],
        force_password_change=False,
        starter_pokemon_selected=False,
        is_active=True,
    )
    db.add(new_trainer)
    db.commit()
    db.refresh(new_trainer)

    return new_trainer


def list_trainers(db: Session):
    return (
        db.query(User)
        .filter(User.role == TRAINER_ROLE, User.deleted_at.is_(None))
        .order_by(User.id.asc())
        .all()
    )


def update_trainer(trainer_id: int, trainer_update: TrainerUpdate, db: Session):
    trainer = (
        db.query(User)
        .filter(
            User.id == trainer_id,
            User.role == TRAINER_ROLE,
            User.deleted_at.is_(None),
        )
        .first()
    )
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    if trainer_update.username is not None:
        # Check for username uniqueness
        if (
            db.query(User)
            .filter(
                User.username == trainer_update.username,
                User.id != trainer_id,
            )
            .first()
        ):
            raise HTTPException(status_code=400, detail="Username already registered")
        trainer.username = trainer_update.username

    if trainer_update.email is not None:
        # Check for email uniqueness
        if (
            db.query(User)
            .filter(User.email == trainer_update.email, User.id != trainer_id)
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
    trainer = (
        db.query(User)
        .filter(
            User.id == trainer_id,
            User.role == TRAINER_ROLE,
            User.deleted_at.is_(None),
        )
        .first()
    )
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    trainer.is_active = False
    trainer.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"detail": "Trainer soft deleted"}
