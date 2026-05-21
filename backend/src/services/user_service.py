from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.user import UserCreate
from passlib.context import CryptContext
from fastapi import HTTPException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_user(user: UserCreate, db: Session):
    db_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    return user
