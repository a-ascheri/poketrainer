from datetime import datetime, timezone

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.user import AdminCreate, ChangePasswordInput, UserCreate, UserUpdate

ADMIN_ROLE = "admin"
TRAINER_ROLE = "trainer"
DEFAULT_ADMIN_PERMISSIONS = ["manage_users", "manage_admins"]

INITIAL_ADMIN_USERNAME = "originadmin"
INITIAL_ADMIN_PASSWORD = "admin123"
INITIAL_ADMIN_EMAIL = "originadmin@poketrainer.com"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _assert_unique_username_email(db: Session, username: str, email: str, skip_id: int | None = None):
    query = db.query(User).filter((User.username == username) | (User.email == email))
    if skip_id is not None:
        query = query.filter(User.id != skip_id)

    existing = query.first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")


def create_user(user: UserCreate, db: Session):
    _assert_unique_username_email(db, user.username, user.email)

    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=TRAINER_ROLE,
        permissions=[],
        force_password_change=False,
        starter_pokemon_selected=False,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def create_admin_user(payload: AdminCreate, db: Session):
    _assert_unique_username_email(db, payload.username, payload.email)

    new_admin = User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role=ADMIN_ROLE,
        permissions=payload.permissions or DEFAULT_ADMIN_PERMISSIONS,
        force_password_change=True,
        starter_pokemon_selected=True,
        is_active=True,
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin


def ensure_initial_admin(db: Session):
    existing = db.query(User).filter(User.username == INITIAL_ADMIN_USERNAME).first()
    if existing:
        return existing

    admin = User(
        username=INITIAL_ADMIN_USERNAME,
        email=INITIAL_ADMIN_EMAIL,
        hashed_password=get_password_hash(INITIAL_ADMIN_PASSWORD),
        role=ADMIN_ROLE,
        permissions=DEFAULT_ADMIN_PERMISSIONS,
        force_password_change=True,
        starter_pokemon_selected=True,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def list_users(db: Session, include_deleted: bool = False):
    query = db.query(User)
    if not include_deleted:
        query = query.filter(User.deleted_at.is_(None))
    return query.order_by(User.id.asc()).all()


def get_user_by_id(user_id: int, db: Session, include_deleted: bool = False):
    query = db.query(User).filter(User.id == user_id)
    if not include_deleted:
        query = query.filter(User.deleted_at.is_(None))

    user = query.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user(user_id: int, payload: UserUpdate, db: Session):
    user = get_user_by_id(user_id, db)

    next_username = payload.username if payload.username is not None else user.username
    next_email = payload.email if payload.email is not None else user.email
    _assert_unique_username_email(db, next_username, next_email, skip_id=user_id)

    if payload.username is not None:
        user.username = payload.username
    if payload.email is not None:
        user.email = payload.email
    if payload.password is not None:
        user.hashed_password = get_password_hash(payload.password)
        user.force_password_change = False
    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)
    return user


def soft_delete_user(user_id: int, db: Session):
    user = get_user_by_id(user_id, db)
    user.is_active = False
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"detail": "User soft deleted"}


def change_password(user: User, payload: ChangePasswordInput, db: Session):
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid current password")

    user.hashed_password = get_password_hash(payload.new_password)
    user.force_password_change = False
    db.commit()
    db.refresh(user)
    return {"detail": "Password updated"}


def authenticate_user(username: str, password: str, db: Session):
    user = (
        db.query(User)
        .filter(User.username == username, User.deleted_at.is_(None), User.is_active.is_(True))
        .first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    return user
