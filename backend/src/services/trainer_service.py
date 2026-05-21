from sqlalchemy.orm import Session
from src.models.trainer import Trainer
from src.schemas.trainer import TrainerCreate
from passlib.context import CryptContext
from fastapi import HTTPException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_trainer(trainer: TrainerCreate, db: Session):
    db_trainer = db.query(Trainer).filter((Trainer.username == trainer.username) | (Trainer.email == trainer.email)).first()
    
    if db_trainer:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    hashed_password = get_password_hash(trainer.password)
    new_trainer = Trainer(username=trainer.username, email=trainer.email, hashed_password=hashed_password)
    db.add(new_trainer)
    db.commit()
    db.refresh(new_trainer)
    
    return new_trainer


def list_trainers(db: Session):
    return db.query(Trainer).all()
