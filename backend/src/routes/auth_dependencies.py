from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.routes.prefixes import USER_PREFIX
from src.services.jwt import verify_access_token
from src.services.user_service import ADMIN_ROLE, TRAINER_ROLE, get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{USER_PREFIX}/token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")
    return payload


def get_current_user_entity(
    payload: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalido")

    return get_user_by_id(int(user_id), db)


def require_admin(current_user=Depends(get_current_user_entity)):
    if current_user.force_password_change:
        raise HTTPException(
            status_code=403,
            detail="Password change required before using admin endpoints",
        )
    if current_user.role != ADMIN_ROLE:
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user


def require_trainer(current_user=Depends(get_current_user_entity)):
    if current_user.force_password_change:
        raise HTTPException(
            status_code=403,
            detail="Password change required before using trainer endpoints",
        )
    if current_user.role != TRAINER_ROLE:
        raise HTTPException(status_code=403, detail="Trainer role required")
    return current_user
